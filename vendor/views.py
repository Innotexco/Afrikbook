from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages 


from .models import vendor_table, Vendor_Quote, Vendor_Order, Vendor_Return, Vendor_invoice, edited_Vendor_invoice

# from account.models import Payment_method, StockIn_Log, Stock_In, account_log, Outlet_StockIn, Outlet_StockIn_Log, chart_of_account
from account.models import *
from settings.models import *

from Stock.models import *
from customer.models import customer_invoice, payable, Vat
from main.models import User

from .functions.vendorfunc import *
from .functions.purchasequote import add_purchase_quote, update_purchase_quote
from .functions.purchaseorder import add_purchase_order
from .functions.ReturnOutward import add_return_item
from .functions.purchaseinvoice import add_purchase_invoice

from django.http.response import JsonResponse


from routers.page_permission import  urls_name
from Stock.utils import random_string_generator;
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.db.models import Q

from itertools import zip_longest
import logging
import traceback
import decimal

logger = logging.getLogger(__name__)






@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def NewPurchase(request):
    db = request.user.company_id.db_name
    account = chart_of_account.objects.using(db).filter(account_id__startswith='2')
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    payment = Payment_method.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    item = Item.objects.using(db).all()
    invoices = Vendor_invoice.objects.using(db).all()


    old_invoiceID =  invoices.latest('invoice_date').invoiceID if invoices.exists() else '1000000'
    invoiceID = int(old_invoiceID) + 1

    if request.method == "POST":
           
        # outlet = User.objects.get(id = request.user.id).outlet
        # if outlet:
           add_purchase_invoice(request, db)
        # else:
        #     messages.error(request, "Assign outlet to logged in user")
     
   
    context = {
        'account': account,
        'supplier': supplier,
        'warehouse': warehouse,
        'payment': payment,
        'outlet': outlet,
        'item': item,
       'invoiceID': invoiceID,

    }
    return render(request, 'vendor/NewPurchase.html', context)




def EditPurchaseInvoice(request, invoice_id):
    db        = request.user.company_id.db_name
    invoices  = Vendor_invoice.objects.using(db).filter(invoiceID=invoice_id)

    if not invoices.exists():
        messages.error(request, "Invoice not found")
        return redirect('vendor:NewPurchase')

    first      = invoices.first()
    vendors    = vendor_table.objects.using(db).all()
    warehouses = Warehouse.objects.using(db).all()
    outlets    = sales_outlet.objects.using(db).all()
    items      = Item.objects.using(db).all()
    accounts   = chart_of_account.objects.using(db).filter(account_id__startswith='2')
    payments   = Payment_method.objects.using(db).all()

    # Build a set of item codes already on this invoice for duplicate check
    existing_itemcodes = set(
        invoices.values_list('itemcode', flat=True)
    )

    if request.method == 'POST' and request.POST.get('action') == 'update_all':
        try:
            with db_transaction.atomic(using=db):

                removed_raw    = request.POST.get('removed_ids', '')
                removed_set    = set(r.strip() for r in removed_raw.split(',') if r.strip())
                new_codes      = request.POST.getlist('new_item_code[]')
                new_qtys       = request.POST.getlist('new_qty[]')
                new_units      = request.POST.getlist('new_unit[]')
                new_descs      = request.POST.getlist('new_desc[]')
                new_discounts  = request.POST.getlist('new_discount[]')
                line_ids       = request.POST.getlist('line_id[]')
                line_qtys      = request.POST.getlist('line_qty[]')
                line_units     = request.POST.getlist('line_unit[]')
                line_descs     = request.POST.getlist('line_desc[]')
                line_discounts = request.POST.getlist('line_discount[]')
                line_itemcodes = request.POST.getlist('line_itemcode[]')

                # ── Duplicate check: if new item already exists in invoice,
                #    merge its qty into the existing line instead ──────────
                merge_map = {}  # itemcode → extra qty to add
                truly_new_codes     = []
                truly_new_qtys      = []
                truly_new_units     = []
                truly_new_descs     = []
                truly_new_discounts = []

                for i, code in enumerate(new_codes):
                    if not code:
                        continue
                    qty = float(new_qtys[i]) if new_qtys[i] else 1

                    if code in existing_itemcodes:
                        # Merge into existing line
                        if code in merge_map:
                            merge_map[code] += qty
                        else:
                            merge_map[code] = qty
                        messages.warning(
                            request,
                            f"Item '{code}' already on invoice — quantity merged into existing line."
                        )
                    else:
                        truly_new_codes.append(code)
                        truly_new_qtys.append(new_qtys[i])
                        truly_new_units.append(new_units[i])
                        truly_new_descs.append(new_descs[i])
                        truly_new_discounts.append(new_discounts[i])

                # Apply merges to line_qtys before archiving
                for idx, lid in enumerate(line_ids):
                    if idx < len(line_itemcodes):
                        code = line_itemcodes[idx]
                        if code in merge_map:
                            current_qty = float(line_qtys[idx]) if line_qtys[idx] else 0
                            line_qtys[idx] = str(current_qty + merge_map[code])

                # ── Step 1: Archive original lines ────────────────────────
                for line in invoices:
                    edited_Vendor_invoice.objects.using(db).create(
                        original_invoiceID = invoice_id,
                        edited_by          = request.user.username,
                        cusID              = line.cusID,
                        vendor_name        = line.vendor_name,
                        invoiceID          = line.invoiceID,
                        orderID            = line.orderID,
                        Gdescription       = line.Gdescription,
                        invoice_date       = line.invoice_date,
                        due_date           = line.due_date,
                        itemcode           = line.itemcode,
                        item_name          = line.item_name,
                        item_descriptions  = line.item_descriptions,
                        qty                = line.qty,
                        unit_p             = line.unit_p,
                        discount_price     = line.discount_price,
                        amount             = line.amount,
                        token_id           = line.token_id,
                        amount_paid        = line.amount_paid,
                        amount_expected    = line.amount_expected,
                        cancellation       = line.cancellation,
                        warehouse          = getattr(line, 'warehouse', ''),
                        Userlogin          = line.Userlogin,
                    )

                # ── Step 2: Undo stock additions ──────────────────────────
                old_warehouse = getattr(first, 'warehouse', None)
                old_outlet    = request.POST.get('old_outlet', '')

                for line in invoices:
                    if old_warehouse:
                        stock = CreateStockIn.objects.using(db).filter(
                            warehouse=old_warehouse, item_code=line.itemcode
                        ).first()
                        if stock:
                            stock.quantity = float(stock.quantity or 0) - float(line.qty or 0)
                            stock.save(using=db)

                    if old_outlet:
                        outlet_stock = CreateOutletStockIn.objects.using(db).filter(
                            outlet=old_outlet, item_code=line.itemcode
                        ).first()
                        if outlet_stock:
                            outlet_stock.quantity = float(outlet_stock.quantity or 0) - float(line.qty or 0)
                            outlet_stock.save(using=db)

                # ── Step 3: Undo accounting ───────────────────────────────
                try:
                    bank_account = chart_of_account.objects.using(db).get(account_id='2067-Purchase')
                    bank_account.actual_balance -= decimal.Decimal(
                        str(first.amount_expected or 0)
                    )
                    bank_account.save(using=db)
                except chart_of_account.DoesNotExist:
                    logger.warning(
                        f"[EditPurchaseInvoice] Purchase Account not found | "
                        f"invoiceID={invoice_id}"
                    )

                # ── Step 4: Delete original lines ─────────────────────────
                invoices.delete()

                # ── Step 5: Build item lists ──────────────────────────────
                item_list     = []
                qty_list      = []
                unit_list     = []
                desc_list     = []
                discount_list = []
                amount_list   = []
                name_list     = []

                archived_lines = list(
                    edited_Vendor_invoice.objects.using(db)
                    .filter(original_invoiceID=invoice_id)
                    .order_by('id')
                )

                # Existing lines (with merges applied, minus removed)
                for idx, lid in enumerate(line_ids):
                    if lid in removed_set:
                        continue
                    if idx < len(archived_lines):
                        orig     = archived_lines[idx]
                        qty      = float(line_qtys[idx]) if line_qtys[idx] else float(orig.qty)
                        unit_p   = float(line_units[idx]) if line_units[idx] else float(orig.unit_p or 0)
                        discount = float(line_discounts[idx]) if line_discounts[idx] else float(orig.discount_price or 0)
                        amt      = (qty * unit_p) - discount

                        item_list.append(orig.itemcode)
                        qty_list.append(str(int(qty)))
                        unit_list.append(str(unit_p))
                        desc_list.append(line_descs[idx] if line_descs[idx] else orig.item_descriptions)
                        discount_list.append(str(discount))
                        amount_list.append(str(amt))
                        name_list.append(orig.item_name)

                # Truly new items (not duplicates)
                for i, code in enumerate(truly_new_codes):
                    try:
                        item_obj = Item.objects.using(db).get(generated_code=code)
                        qty      = float(truly_new_qtys[i]) if truly_new_qtys[i] else 1
                        unit_p   = float(truly_new_units[i]) if truly_new_units[i] else 0
                        discount = float(truly_new_discounts[i]) if truly_new_discounts[i] else 0
                        amt      = (qty * unit_p) - discount

                        item_list.append(code)
                        qty_list.append(str(int(qty)))
                        unit_list.append(str(unit_p))
                        desc_list.append(truly_new_descs[i] if truly_new_descs[i] else '')
                        discount_list.append(str(discount))
                        amount_list.append(str(amt))
                        name_list.append(item_obj.item_name)
                    except Item.DoesNotExist:
                        messages.error(request, f"Item {code} not found — skipped")
                        continue

                grand_total = sum(float(a) for a in amount_list)

                # ── Step 6: Patch POST and call add_purchase_invoice ──────
                request.POST = request.POST.copy()
                request.POST['invoiceID']    = invoice_id
                request.POST['orderID']      = request.POST.get('order_id', first.orderID or '')
                request.POST['warehouse']    = request.POST.get('warehouse', '')
                request.POST['outlet']       = request.POST.get('outlet', '')
                request.POST['vendor_name']  = request.POST.get('vendor_id', '')
                request.POST['Gdescription'] = request.POST.get('Gdescription', first.Gdescription)
                request.POST['invoice_date'] = request.POST.get('invoice_date')
                request.POST['due_date']     = request.POST.get('due_date')
                request.POST['source']       = request.POST.get('source', 'Credit')
                request.POST['total']        = str(grand_total)
                request.POST.setlist('item[]',      item_list)
                request.POST.setlist('qty[]',       qty_list)
                request.POST.setlist('unit[]',      unit_list)
                request.POST.setlist('desc[]',      desc_list)
                request.POST.setlist('discount[]',  discount_list)
                request.POST.setlist('amount[]',    amount_list)
                request.POST.setlist('item_name',   name_list)

                add_purchase_invoice(request, db)

        except Exception as e:
            logger.error(
                f"[EditPurchaseInvoice] Failed | invoiceID={invoice_id} | "
                f"{e}\n{traceback.format_exc()}"
            )
            messages.error(request, f"Edit failed: {e}")

        return redirect('vendor:EditPurchaseInvoice', invoice_id=invoice_id)

    context = {
        'invoices':          invoices,
        'first':             first,
        'vendors':           vendors,
        'warehouses':        warehouses,
        'outlets':           outlets,
        'items':             items,
        'accounts':          accounts,
        'payments':          payments,
        'invoice_id':        invoice_id,
        'existing_itemcodes': list(existing_itemcodes),
    }
    return render(request, 'vendor/EditPurchaseInvoice.html', context)




from datetime import datetime

   
def getdate(fromdate, todate):
   from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
   to_date = datetime.strptime(todate, '%Y-%m-%d').date()
   return from_date, to_date

def getStockAdjustmentData(request, db):
   if request.method == 'GET':
      getinvoiceID = request.GET.get('invoiceID')
      getidcode = request.GET.get('idcode')
      if getinvoiceID and getidcode:
        ifFailed = {'failed': "No Data Found"}
        try: 
            getid = Vendor_invoice.objects.using(db).get(Q(invoiceID=getinvoiceID,) & Q(id=getidcode))
        except Vendor_invoice.DoesNotExist:
            return ifFailed
        # try:
        #     getid = CreateOutletStockInLog.objects.using(db).get(Q(invoice_no=getinvoiceID,) & Q(id=getidcode))
        # except CreateOutletStockInLog.DoesNotExist:
        #     pass

        fetchonce = {
            'item':getid.item_name,
            'invoice_no':getid.invoiceID,
            'date':getid.invoice_date,
            'description':getid.item_descriptions,
            'qty':getid.qty,
            'id':getid.id,
         }
        if fetchonce:
            return fetchonce
        else:
            return ifFailed



def getStockAdjustmentDate2(request, context, db, con):
   if request.method == 'GET':
        getfromdate = request.GET.get('fromdate')
        gettodate = request.GET.get('todate')
        invoice = request.GET.get('invoice')
        sortbyItem = request.GET.get('sortbyItem')
        failed = {'failed': "No Data Found"}
        if getfromdate and gettodate:
            from_date, to_date =getdate(getfromdate, gettodate)
            try:
                getstockin_log = Vendor_invoice.objects.using(db).filter(Q(invoice_date__range=(from_date, to_date)) & con)
            except Vendor_invoice.DoesNotExist:
                return failed
            
        if sortbyItem is not None:
            try:
                getstockin_log = Vendor_invoice.objects.using(db).filter(Q(itemcode=sortbyItem) & con)
            except Vendor_invoice.DoesNotExist:
                return failed
          
        if invoice is not None and invoice != '_ _Choose Item_ _':
            try:
                getstockin_log = Vendor_invoice.objects.using(db).filter(Q(invoiceID=invoice) & con)
            except Vendor_invoice.DoesNotExist:
                return failed
          
        if sortbyItem or invoice or getfromdate and gettodate is not None:
        
            if getstockin_log:
                # Vendor_invoice
                result_stockinlog = [({
                    'id': stockinlog.id if stockinlog and stockinlog.id is not None else None,
                    'datetx': stockinlog.invoice_date if stockinlog and stockinlog.invoice_date is not None else None,
                    'invoice_no': stockinlog.invoiceID if stockinlog and stockinlog.invoiceID is not None else None,
                    'item': stockinlog.item_name if stockinlog and stockinlog.item_name is not None else None,
                    'quantity': stockinlog.qty if stockinlog and stockinlog.qty is not None else None,
                    'item_decription': stockinlog.item_descriptions if stockinlog and stockinlog.item_descriptions is not None else None,
                    'token_id': stockinlog.token_id if stockinlog and stockinlog.token_id is not None else None,
                    })
                    for stockinlog in getstockin_log
                ]
                return result_stockinlog
            else:
                return failed


def stock_adjustment_arithmetic_logic(stockinQty, form_qty, getqty):
    if float(form_qty) > float(getqty.qty):
        currentQty = float(form_qty) - float(getqty.qty)
        stockinQtyNew = float(stockinQty) + float(currentQty)
        return stockinQtyNew
        # stockinQty.save(using=db)
        # stockinLog qty update
        
    else:
        currentQty = float(getqty.qty) - float(form_qty)
        stockinQtyNew = float(stockinQty) - float(currentQty)
        return stockinQtyNew
        # stockinLog qty update
        
from decimal import Decimal
@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def cancle_invoice(request, context, form_invoiceID, db, form_id):
    try:
        vendorInv = Vendor_invoice.objects.using(db).get(invoiceID=form_invoiceID, id=form_id)
    except Vendor_invoice.DoesNotExist:
        context['error_message'] = 'Data Not Found'
        return context

    amount_paid = Decimal(str(vendorInv.amount_paid))
    amount_expected = Decimal(str(vendorInv.amount_expected))

    # ── 1. Accounting entries ─────────────────────────────────────────
    if amount_paid == amount_expected:
        payable.objects.using(db).create(
            type='Credit',
            transaction_id=form_invoiceID,
            amount=vendorInv.amount,
            vendor_name=vendorInv.vendor_name,
            payment_method='Cash',
            Userlogin=request.user,
        )
    elif amount_paid < amount_expected and amount_paid > 0:
        payable.objects.using(db).create(
            type='Credit',
            transaction_id=form_invoiceID,
            amount=amount_paid,
            vendor_name=vendorInv.vendor_name,
            payment_method='Cash',
            Userlogin=request.user,
        )
    elif amount_paid == 0:
        Liability_account.objects.using(db).create(
            type='Credit',
            transaction_id=form_invoiceID,
            amount=vendorInv.amount,
            vendor_name=vendorInv.vendor_name,
            payment_method='Cash',
            Userlogin=request.user,
        )

    # ── 2. Mark logs as cancelled ─────────────────────────────────────
    try:
        stock_log = CreateStockInLog.objects.using(db).get(invoice_no=form_invoiceID, item_code=vendorInv.itemcode)
        stock_log.quantity = 0
        stock_log.status = 'Cancelled'
        stock_log.save(using=db)
    except CreateStockInLog.DoesNotExist:
        stock_log = None

    try:
        outlet_log = CreateOutletStockInLog.objects.using(db).get(invoice_no=form_invoiceID, item_code=vendorInv.itemcode)
        outlet_log.quantity = 0
        outlet_log.status = 'Cancelled'
        outlet_log.save(using=db)
    except CreateOutletStockInLog.DoesNotExist:
        outlet_log = None

    # ── 3. Reverse warehouse stock (FIFO across multiple records) ────
    qty_to_reverse = Decimal(str(vendorInv.qty))
    if stock_log:
        # Find all stock‑in records for this warehouse + item, oldest first
        stock_records = CreateStockIn.objects.using(db).filter(
            warehouse=stock_log.warehouse,
            item_code=stock_log.item_code
        ).order_by('id')
        remaining = qty_to_reverse
        for record in stock_records:
            if remaining <= 0:
                break
            deduct = min(Decimal(str(record.quantity)), remaining)
            record.quantity = Decimal(str(record.quantity)) - deduct
            record.save(using=db)
            remaining -= deduct
        if remaining > 0:
            context['error_message'] = f'Not enough warehouse stock to cancel (short by {remaining})'
            return context

    # ── 4. Reverse outlet stock (if any) ──────────────────────────────
    if outlet_log:
        outlet_records = CreateOutletStockIn.objects.using(db).filter(
            warehouse=outlet_log.warehouse,   # or outlet_log.outlet – depends on your model
            item_code=outlet_log.item_code
        ).order_by('id')
        remaining = qty_to_reverse
        for record in outlet_records:
            if remaining <= 0:
                break
            deduct = min(Decimal(str(record.quantity)), remaining)
            record.quantity = Decimal(str(record.quantity)) - deduct
            record.save(using=db)
            remaining -= deduct
        if remaining > 0:
            context['error_message'] = f'Not enough outlet stock to cancel (short by {remaining})'
            return context

    # ── 5. Mark invoice as cancelled ──────────────────────────────────
    vendorInv.amount_paid = amount_expected
    vendorInv.cancellation = 1
    vendorInv.save(using=db)

    context['success_message'] = 'Invoice has been canceled'
    return context

# @login_required(login_url="/")
# @urls_name(name="Purchase Invoices")
def update_invoice(db, context, form_id, form_invoiceID, form_qty, request):
    # Convert qty to integer early (with fallback)
    try:
        form_qty = int(form_qty)
    except (ValueError, TypeError):
        form_qty = 0
        context['error_message'] = 'Invalid quantity value'
        return

    # Default initial quantity
    stockinQty = 0
    getqty_outlet_stockinlog = None
    getqty_stockinlog = None
    vendorInv = None  # ← initialize here so it's always defined

    try:
        vendorInv = Vendor_invoice.objects.using(db).get(invoiceID=form_invoiceID, id=form_id)

        # Update regular stock-in log if exists
        try:
            getqty_stockinlog = CreateStockInLog.objects.using(db).get(
                invoice_no=form_invoiceID,
                item_code=vendorInv.itemcode
            )
            getqty_stockinlog.quantity = form_qty
            getqty_stockinlog.save(using=db)
        except CreateStockInLog.DoesNotExist:
            pass

        # Update outlet stock-in log if exists
        try:
            getqty_outlet_stockinlog = CreateOutletStockInLog.objects.using(db).get(
                invoice_no=form_invoiceID,
                item_code=vendorInv.itemcode
            )
            getqty_outlet_stockinlog.quantity = form_qty
            getqty_outlet_stockinlog.save(using=db)
        except CreateOutletStockInLog.DoesNotExist:
            pass

        # Update main stock quantity (warehouse)
        if getqty_stockinlog is not None:
            try:
                get_qty_from_stockin = CreateStockIn.objects.using(db).get(
                    warehouse=getqty_stockinlog.warehouse,
                    item_code=getqty_stockinlog.item_code
                )
                stockinQty = get_qty_from_stockin.quantity
                get_qty_from_stockin.quantity = stock_adjustment_arithmetic_logic(
                    stockinQty, form_qty, vendorInv
                )
                get_qty_from_stockin.save(using=db)
            except CreateStockIn.DoesNotExist:
                pass

        # Update main stock quantity (outlet) — only if no warehouse log
        elif getqty_outlet_stockinlog is not None:
            try:
                get_qty_from_stockin = CreateOutletStockIn.objects.using(db).get(
                    warehouse=getqty_outlet_stockinlog.warehouse,
                    item_code=getqty_outlet_stockinlog.item_code
                )
                stockinQty = get_qty_from_stockin.quantity
                get_qty_from_stockin.quantity = stock_adjustment_arithmetic_logic(
                    stockinQty, form_qty, vendorInv
                )
                get_qty_from_stockin.save(using=db)
            except CreateOutletStockIn.DoesNotExist:
                pass

        else:
            context['error_message'] = 'No matching stock-in log found'

    except Vendor_invoice.DoesNotExist:
        context['error_message'] = 'Invoice not found'
        # No return here — continue to log if possible, or return early if you prefer
        # return

    # Create adjustment log — safe because stockinQty is always set
    Stock_Adjustment_Log = StockAdjustmentLog.objects.using(db).create(
        invoice_no=form_invoiceID,
        initial_qty=stockinQty,
        new_qty=form_qty,
        item_code=vendorInv.itemcode if vendorInv else None,  # ← safe access
        Userlogin=request.user.username,
        type='purchase',
    )

    # Only update invoice if it exists
    if vendorInv:
        vendorInv.qty = form_qty
        vendorInv.save(using=db)
        context['success_message'] = 'Quantity Updated'
    else:
        context['error_message'] = 'Update Failed - Invoice not found'
        

def updateStockAdjustmentData(request, context, db):
   if request.method == 'POST':
        form_qty = request.POST.get('modalNewqty')
        form_id = request.POST.get('modalID')
        form_invoiceID = request.POST.get('modalinvoiceID')
        # UPDATE INVOICE
        if 'update_invoice' in request.POST:
            update_invoice(db, context, form_id, form_invoiceID, form_qty, request)
        

        # CANCLE INVOICE
        if 'cancle_invoice' in request.POST:
            cancle_invoice(request, context, form_invoiceID, db, form_id)



# ********************************************************************************************************

@login_required(login_url="/")
@urls_name(name = "Purchase Adjustment")
def PurchaseAdjustment(request):
    db = request.user.company_id.db_name
    # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
    vendorInvoice = Vendor_invoice.objects.using(db).filter(~Q(cancellation=1))
    # outlet_stockin_log = CreateStockInLog.objects.using(db).all()
    # outlet_stockin_log = CreateOutletStockInLog.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    getitem = Item.objects.using(db).all();
    context = {
      'allinvoice': vendorInvoice,
      'items': getitem,
      'warehouse': warehouse,
      'outlet': outlet,
    }
 
   # function to fetch data for update(when edit btn is clicked)
    data = getStockAdjustmentData(request, db)
    if data:
        # do not assign a key to data
        return JsonResponse(data)
    # update function
    updateStockAdjustmentData(request, context, db)

   # get function
    stockinlog=getStockAdjustmentDate2(request, context, db, ~Q(cancellation=1))
    if stockinlog:
        return JsonResponse({'stockin':stockinlog})


    return render(request, 'vendor/PurchaseAdjustment.html', context)

# ********************************************************************************************************



# ********************************************************************************************************


# @login_required(login_url="/")
# @urls_name(name="Purchase Invoices")
# def CanclePurchaseInvoice(request):
#     db            = request.user.company_id.db_name
#     vendorInvoice = Vendor_invoice.objects.using(db).filter(~Q(cancellation=1))
#     warehouse     = Warehouse.objects.using(db).all()
#     outlet        = sales_outlet.objects.using(db).all()
#     getitem       = Item.objects.using(db).all()

#     context = {
#         'allinvoice': vendorInvoice,
#         'items':      getitem,
#         'warehouse':  warehouse,
#         'outlet':     outlet,
#         'type':       'cancle',   # tells template to render Cancel button
#     }

#     # ── Handle cancel POST ───────────────────────────────────────────────────
#     if request.method == 'POST' and 'cancle_invoice' in request.POST:
#         modal_id         = request.POST.get('modalID')
#         modal_invoice_id = request.POST.get('modalinvoiceID')

#         if not modal_id or not modal_invoice_id:
#             messages.error(request, "Invalid cancellation request — missing invoice reference.")
#             return render(request, 'vendor/CanclePurchaseInvoice.html', context)

#         try:
#             # ── 1. Mark every line on this invoice as cancelled ──────────────
#             rows_updated = (
#                 Vendor_invoice.objects
#                 .using(db)
#                 .filter(invoiceID=modal_invoice_id)
#                 .update(cancellation=1)
#             )

#             if rows_updated == 0:
#                 messages.warning(request, f"No invoice lines found for Invoice {modal_invoice_id}.")
#                 return render(request, 'vendor/CanclePurchaseInvoice.html', context)

#             # ── 2. Reverse stock — add quantities back ───────────────────────
#             cancelled_lines = (
#                 Vendor_invoice.objects
#                 .using(db)
#                 .filter(invoiceID=modal_invoice_id)
#             )
#             for line in cancelled_lines:
#                 try:
#                     # Reverse the stock reduction that happened when the
#                     # purchase was originally received into the warehouse
#                     stock_item = (
#                         CreateStockIn.objects
#                         .using(db)
#                         .filter(itemcode=line.itemcode)
#                         .first()
#                     )
#                     if stock_item:
#                         stock_item.quantity = (
#                             float(stock_item.quantity or 0) + float(line.qty or 0)
#                         )
#                         stock_item.save(using=db)
#                 except Exception as stock_err:
#                     logger.warning(
#                         f"[CanclePurchaseInvoice] Stock reversal failed | "
#                         f"invoiceID={modal_invoice_id} | itemcode={line.itemcode} | {stock_err}"
#                     )

#             messages.success(
#                 request,
#                 f"Invoice {modal_invoice_id} has been cancelled successfully."
#             )
#             logger.info(
#                 f"[CanclePurchaseInvoice] Cancelled | invoiceID={modal_invoice_id} | "
#                 f"id={modal_id} | user={request.user.username} | rows={rows_updated}"
#             )

#         except Exception as e:
#             logger.error(
#                 f"[CanclePurchaseInvoice] Cancellation failed | "
#                 f"invoiceID={modal_invoice_id} | {e}\n{traceback.format_exc()}"
#             )
#             messages.error(request, f"Cancellation failed: {e}")

#         # Refresh queryset so the cancelled invoice no longer appears
#         context['allinvoice'] = Vendor_invoice.objects.using(db).filter(~Q(cancellation=1))
#         return render(request, 'vendor/CanclePurchaseInvoice.html', context)

#     # ── GET: just render the page ────────────────────────────────────────────
#     return render(request, 'vendor/CanclePurchaseInvoice.html', context)



@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def CanclePurchaseInvoice(request):
    db = request.user.company_id.db_name
    allinvoice = customer_invoice.objects.filter(invoiceID='11971')
    vendorInvoice = Vendor_invoice.objects.using(db).filter(~Q(cancellation=1))
    outlet_stockin_log = CreateStockInLog.objects.using(db).all()
    outlet_stockin_log = CreateOutletStockInLog.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    getitem = Item.objects.using(db).all();
    context = {
      'allinvoice': vendorInvoice,
      'items': getitem,
      'warehouse': warehouse,
      'outlet': outlet,
    }

   
#     # update function
    updateStockAdjustmentData(request, context, db)

#    # get function
    stockinlog=getStockAdjustmentDate2(request, context, db, ~Q(cancellation=1))
    if stockinlog:
        return JsonResponse({'stockin':stockinlog})


    return render(request, 'vendor/CanclePurchaseInvoice.html', context)

# ********************************************************************************************************


# ********************************************************************************************************
         
@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def viewCanclePurchase(request):
    db = request.user.company_id.db_name
    # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
    vendorInvoice = Vendor_invoice.objects.using(db).filter(Q(cancellation=1))
    # outlet_stockin_log = CreateStockInLog.objects.using(db).all()
    # outlet_stockin_log = CreateOutletStockInLog.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    getitem = Item.objects.using(db).all();
    context = {
      'allinvoice': vendorInvoice,
      'items': getitem,
      'warehouse': warehouse,
      'outlet': outlet,
    }

   
   # get function
    stockinlog=getStockAdjustmentDate2(request, context, db, Q(cancellation=1))
    if stockinlog:
        return JsonResponse({'stockin':stockinlog})


    return render(request, 'vendor/viewCanclePurchase.html', context)

# ********************************************************************************************************


def GetSubCategory(request, id):
    db = request.user.company_id.db_name
    try:
        vendor = vendor_table.objects.using(db).get(id=id)
        data = {
                'name': vendor.name,
            }
        return JsonResponse(data)
    except vendor_table.DoesNotExist: 
        return JsonResponse({'error': 'Vendor not found'}, status=404)






# def GetVendorDetails(request, id):
#     db = request.user.company_id.db_name
#     venID =   request.POST.get('venID')
#     lookup = Q(id__iexact=venID) | Q(custID__iexact=venID)
#     try:
#         vendor = vendor_table.objects.using(db).get(Q(lookup))
#         data = {
#                 'name': vendor.name,
#                 'phone': vendor.phone,
#                 'email': vendor.email,
#                 'custID': vendor.custID,
#                 'company_name': vendor.company_name,
#                 'address': vendor.address,
#             }
#         return JsonResponse(data)
#     except vendor_table.DoesNotExist:
#         return JsonResponse({'error': 'Vendor not found'}, status=404)


def GetVendorDetails(request, id):
    db = request.user.company_id.db_name
    
    if not id:
        return JsonResponse({'error': 'No vendor ID provided'}, status=400)
    
    try:
        # Build lookup based on whether id is numeric or not
        if id.isdigit():
            lookup = Q(id=id) | Q(custID__iexact=id) | Q(name__iexact=id)
        else:
            lookup = Q(custID__iexact=id) | Q(name__iexact=id)
            
        vendor = vendor_table.objects.using(db).get(lookup)
        data = {
            'name': vendor.name,
            'phone': vendor.phone,
            'email': vendor.email,
            'custID': vendor.custID,
            'company_name': vendor.company_name,
            'address': vendor.address,
        }
        return JsonResponse(data)
    except vendor_table.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)
    except vendor_table.MultipleObjectsReturned:
        return JsonResponse({'error': 'Multiple vendors found'}, status=400)



def GetItemDetails(request, item_id):
    db = request.user.company_id.db_name
    try:
        item = Item.objects.using(db).get(generated_code=item_id)
        data = {
                    'desc': item.description,
                    'name': item.item_name,
                    'unit': item.selling_price,
                    'amount': item.purchase_price
                }
        return JsonResponse(data)
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def GetInvoiceDetails(request, invoice_id):
    db = request.user.company_id.db_name
    invoiceID = request.GET.get('invoiceID')
    try:
        # Fetch all fields related to the given invoice_id
        data = Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).values()
        
       
        def get_customer_or_vendor():
            invoice = Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
            if invoice:
                try:
                    vendor_table.objects.using(db).filter(custID=invoice.cusID)
                    return "Vendor"
                except vendor_table.DoesNotExist:
                    return "None"
            else:
                return "None"

        accountType = get_customer_or_vendor()
        
        try:
            vat = Vat.objects.using(db).get(source=invoiceID).amount
        except Vat.DoesNotExist:
            vat = None

        # Serialize the queryset to JSON

        serialized_data = {
            'invoice':list(data),
            'accountType':accountType,
            'vat': vat
        }

        return JsonResponse(serialized_data,  safe=False)
    except Vendor_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
   



@login_required(login_url='/')
@urls_name(name = "Purchase Quotes")
def NewPurchaseQuote(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()

    if request.method == "POST":
        add_purchase_quote(request, db)
    
    context = {
        
        'supplier': supplier,
        'item': item
    }

    return render(request, 'vendor/NewPurchaseQuote.html', context)


@login_required(login_url='/')
@urls_name(name = "Purchase Quotes")
def UpdatePurchaseQuote(request, pk):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    instance = Vendor_Quote.objects.using(db).get(pk=pk)
    quotes = Vendor_Quote.objects.using(db).filter(quote_ID=instance.quote_ID)
    item = Item.objects.using(db).all()

    if request.method == "POST":
        update_purchase_quote(request, instance, db)
        return redirect('vendor:ViewPurchaseQuote')
    
    context = {
        
        'supplier': supplier,
        'instance': instance,
        'quotes': quotes,
        'item': item
    }

    return render(request, 'vendor/UpdatePurchaseQuote.html', context)
  

@login_required(login_url="/")
@urls_name(name='Purchase Quotes')
def delete_PurchaseQuote(request, id):
    db = request.user.company_id.db_name
    delete_PurchaseQuote = Vendor_Quote.objects.using(db).get(id=id)
    delete_PurchaseQuote.delete()
    messages.success(request, "Purchase Quote deleted successfully")
    return redirect('vendor:ViewPurchaseQuote')



@login_required(login_url='/')
@urls_name(name = "Purchase Quotes")
def ViewPurchaseQuote(request):
    db = request.user.company_id.db_name

    # Deduplicate by quote_ID — one row per quote (like sales quotes by referenceID)
    raw = Vendor_Quote.objects.using(db).all().order_by('quote_ID', 'id')
    seen = set()
    unique_quotes = []
    for q in raw:
        if q.quote_ID not in seen:
            seen.add(q.quote_ID)
            unique_quotes.append(q)

    return render(request, 'vendor/ViewPurchaseQuote.html', {'quotes': unique_quotes})



@login_required(login_url='/')
@urls_name(name = "Purchase Order")
def NewPurchaseOrder(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    
    if request.method == "POST":
        add_purchase_order(request, db)
     
    context = {
        
        'supplier': supplier,
        'item': item
    }
   
    return render(request, 'vendor/NewPurchaseOrder.html', context)

@login_required(login_url='/')
@urls_name(name = "Purchase Order")
def ViewPurchaseOrder(request):
    db = request.user.company_id.db_name
    purchase_order = Vendor_Order.objects.using(db).all()
   
    return render(request, 'vendor/ViewPurchaseOrder.html', {'purchase_order': purchase_order})


@login_required(login_url='/')
@urls_name(name = "Returns Outwards")
def ReturnItems(request):
    db = request.user.company_id.db_name
    payment = Payment_method.objects.using(db).all()
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    amount = Vendor_Order.objects.using(db).all()
    item = Item.objects.using(db).all()
    account = chart_of_account.objects.using(db).filter(account_bankname__icontains="Return Outward")
    invoices = Vendor_invoice.objects.using(db).all().order_by('-invoice_date')
    
    if request.method == "POST":
        add_return_item(request, db)
     
    context = {
        'payment': payment,
        'warehouse': warehouse,
        'supplier': supplier,
        'amount': amount,
        'items': item,
        'accounts': account,
        'invoices': invoices,
    }
   
    return render(request, 'vendor/ReturnItems.html', context)

@login_required(login_url='/')
@urls_name(name = "Returns Outwards")
def ViewReturnOutwards(request):
    db = request.user.company_id.db_name
    return_outwards = Vendor_Return.objects.using(db).all()
   
    return render(request, 'vendor/ViewReturnOutwards.html', {'return_outwards': return_outwards})

@login_required(login_url='/')
@urls_name(name = "Returns Outwards")
def GetReturnOutwardItemDetails(request, invoice, item_id):
    db = request.user.company_id.db_name
  
    try:
       item = Vendor_invoice.objects.using(db).get(invoiceID=invoice, itemcode=item_id)
      
       data = {
            'desc': item.item_descriptions,
            'name': item.item_name,
            'qty': item.qty,
            'unit': item.amount,
            'generated_code': item.itemcode
        }
       return JsonResponse(data)
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)


@login_required(login_url="/")
@urls_name(name='Vendor')
def register_vendor(request):
    db = request.user.company_id.db_name
    form = VendorRegistrationForm(request.POST or None)
    display_vendor = vendor_table.objects.using(db).all()

    if request.method == "POST":
        add_vendor(request, db)

    context = {
        "form": form,
        "display_vendor": display_vendor
    }
    return render(request, 'vendor/AddVendor.html', context)


@login_required(login_url="/")
@urls_name(name='Vendor')
def update_vendor(request, id):
    db = request.user.company_id.db_name
    vendor = vendor_table.objects.using(db).get(id = id)
    
    if request.method == "POST":
        edit_vendor(request, id, db)
        return redirect('vendor:view_vendor')
        

    context = {
        'vendor': vendor
    }
    return render(request, 'vendor/EditVendor.html', context)


@login_required(login_url="/")
@urls_name(name='Vendor')
def view_vendor(request):
    db = request.user.company_id.db_name
    display_vendor = vendor_table.objects.using(db).all()

    context = {
        "display_vendor": display_vendor
    }
    return render(request, 'vendor/ViewVendor.html', context)


@login_required(login_url="/")
@urls_name(name='Vendor')
def delete_vendor(request, id):
    db = request.user.company_id.db_name
    delete_vendor = vendor_table.objects.using(db).get(id=id)
    delete_vendor.delete()
    messages.success(request, "Vendor deleted successfully")
    return redirect('vendor:register_vendor')




# ==== VIEW USER INFORMATION ====
def view_user_information(request, username):
    db = request.user.company_id.db_name
    account = vendor_table.objects.using(db).get(username=username)

    following = False

    muted = None

    if request.user.is_authenticated:

        if request.user.id == account.id:
            return redirect("profile")
        
        followers = account.followers.filter(
            followed_by__id = request.user.id
        )

        if followers.exists():
            following = True

    if following:
        queryset = followers.first()
        if queryset.muted:
            muted = True
        else:
            muted = False

    context = {
        "account": account,
        "following": following,
        "muted": muted,
    }

    return render(request, "user_information.html", context)




