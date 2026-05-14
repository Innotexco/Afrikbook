import requests
import json
from django.shortcuts import render, redirect
from .models import customer_table, customer_invoice
from vendor.models import vendor_table
from account.models import *
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .utils import  generate_invoice_id, generate_customer_id

from .functions.customer import *
from .functions.salesquote import *
from .functions.salesorder import *
# from .functions.newsales import *
from .functions.newsalesfunc import *
from .functions.returninwards import *
from .functions.verifypayment import *
from django.db.models import Q
from Stock.models import Item, CreateStockIn
from settings.models import *
from client .models import shipping_addr
from client .api import is_endpoint_available
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name
from main .models import company_table
import re
import copy
from django.db import transaction as db_transaction

#Vendor functions
from vendor.functions.purchasequote import add_purchase_quote
from vendor.functions.purchaseorder import add_purchase_order
# import requests

# Create your views here.
@login_required(login_url='/')
@urls_name(name = "Customer")
def Customers(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()

    context = {
        'customers':customers,
    }
   
    return render(request, 'customer/Customers.html', context)

@login_required(login_url='/')
@urls_name(name="Customer")
def ViewCustomerDetails(request, id):
    db = request.user.company_id.db_name
    
    try:
        customer = customer_table.objects.using(db).get(customer_code=id)
        invoice = customer_invoice.objects.using(db).filter(cusID=id).values('invoiceID').distinct()
    #    invoice = list(customer_invoice.objects.filter(cusID=id).values())
    
    #    invoices = customer_invoice.objects.filter(cusID=id).values()

        unique_invoice = []
        for i in invoice:
           new_data = customer_invoice.objects.using(db).filter(cusID=id, invoiceID=i['invoiceID']).values()#.order_by('invoice_date')

           if new_data.exists():
               unique_invoice.append(new_data.first())

        try:
            credit = receivable.objects.using(db).filter(customer_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
            debit = receivable.objects.using(db).filter(customer_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
            balance = Decimal(credit) - Decimal(debit)
            
      
        except receivable.DoesNotExist:
            balance = "0.00"

        data = {
            'customer': {
                'name': customer.name,
                'phone': customer.phone,
                'code': customer.customer_code,
                'balance': format(balance, ".2f"),
            },
            'invoices': list(unique_invoice),
        }
       
        return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    


@login_required(login_url='/')
@urls_name(name="Customer")
def AddCustomer(request):
    db = request.user.company_id.db_name
    customer_code = generate_customer_id()


    customer = customer_table.objects.using(db).all()
    
    #Endpoint api 
    try:
        response = requests.get('https://console.afrikbook.com/address', timeout=10)
        if response.status_code == 200:
            data = response.json()

            for cus in customer:  
                ship_count = sum(0 for ship in data['ship'] if ship['addr_id_id'] == cus.id)
                cus.ship = ship_count
        else:
            for cus in customer:
                cus.ship = 0
    except requests.RequestException:
        messages.error(request, "Endpoint not available")
        #pass
    
    form = None
    if request.method == 'POST':
        # add_customer(request, db)
        form = add_customer(request, db)
     
    context = {
        'customers': customer,
        'customer_code': customer_code,
        'form': form
    }
    return render(request, "customer/NewCustomer.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def UpdateCustomer(request, id):
    db = request.user.company_id.db_name
    
    customer = customer_table.objects.using(db).get(id=id)
    customers = customer_table.objects.using(db).all()
   
    if request.method == 'POST':    
        update_customer(request, id, db)
        return redirect("customer:NewCustomer")
        
    context = {
        "customer": customer,
        "customers": customers
    }   
    return render(request, "customer/EditCustomer.html", context)

# @urls_name(name="Customer")

def delete_customer(request, id):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).get(id=id)
    customer.delete()
    messages.error(request, "Customer was deleted successfully")
    return redirect("customer:NewCustomer")

@login_required(login_url='/')
@urls_name(name="Customer")
def CusOpenBalance(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    if request.method == "POST":
        cus_open_balance(request, db)

    context = {
        "customers": customers,
        "accounts": accounts
    }
    return render(request, "customer/CustomerOpeningBalance.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def RefundCustomer(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    form = None
    if request.method == "POST":
       form = refund_customer(request, db)

    context = {
        "customers": customers,
        "accounts": accounts,
        "form":form
    }
    return render(request, "customer/RefundCustomer.html", context)


@login_required(login_url='/')
@urls_name(name="Sales Invoices")
def SalesInvoice(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    billing_address = billing_addr.objects.using('afrikbook_client').all()
    company = company_table.objects.get(id=request.user.company_id_id)
    item = Item.objects.using(db).all()
    method = shipping_method.objects.using(db).all()
    invoices = customer_invoice.objects.using(db).all()

    try:
        response = requests.get('https://console.afrikbook.com/address', timeout=10)
        shipping_address = response.json() if response.status_code == 200 else []
    except requests.RequestException:
        shipping_address = []
        
        next_invoice = 1000000
        
        if invoices.exists():
            highest = 0
            for inv in invoices.values_list('invoiceID', flat=True):
                if not inv:
                    continue
                # Strip any _cancelled / _returned suffix
                match = re.match(r'^(\d+)', str(inv))
                if match:
                    num = int(match.group(1))
                    if num > highest:
                        highest = num
            if highest >= 1000000:
                next_invoice = highest + 1
                
        while customer_invoice.objects.using(db).filter(invoiceID=str(next_invoice)).exists():
            next_invoice += 1

        auto_invoice = str(next_invoice)


    # if invoices.exists():
    #     latest_invoice = invoices.latest('invoice_date')
    #     latest_id_str  = latest_invoice.invoiceID
    #     numeric_part   = re.match(r'^(\d+)', str(latest_id_str))
    #     next_invoice   = int(numeric_part.group(1)) + 1 if numeric_part else 1000000
    # else:
    #     next_invoice = 1000000

    # # Keep incrementing until we find an ID that doesn't exist yet
    # while customer_invoice.objects.using(db).filter(invoiceID=str(next_invoice)).exists():
    #     next_invoice += 1

    # invoice = str(next_invoice)
    form = None

    whatsapp_url = request.session.pop('whatsapp_url', None)

    if request.method == "POST":
        outlet = User.objects.get(id=request.user.id).outlet
        if outlet:
            form = add_new_sales(request, db)
            whatsapp_url = request.session.pop('whatsapp_url', None)
        else:
            messages.error(request, "Assign outlet to logged in user")

    context = {
        'customers': customer,
        'vendor': vendor,
        'accounts': accounts,
        'items': item,
        'auto_invoice': auto_invoice,
        'form': form,
        'company': company,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'shipping_method': method,
        'whatsapp_url': whatsapp_url,
    }
    return render(request, "customer/NewSales.html", context)




def EditSalesInvoice(request, invoice_id):
    db       = request.user.company_id.db_name
    invoices = customer_invoice.objects.using(db).filter(invoiceID=invoice_id)

    if not invoices.exists():
        messages.error(request, "Invoice not found")
        return redirect('customer:SalesInvoice')

    first     = invoices.first()
    customers = customer_table.objects.using(db).all()
    vendors   = vendor_table.objects.using(db).all()
    accounts  = chart_of_account.objects.using(db).all()
    items     = Item.objects.using(db).all()
    method    = shipping_method.objects.using(db).all()
    payments  = Payment_method.objects.using(db).all()
    
    existing_itemcodes = set(
        invoices.values_list('itemcode', flat=True)
    )

    if request.method == 'POST' and request.POST.get('action') == 'update_all':
        try:
            with db_transaction.atomic(using=db):

                # ── Step 1: Archive original lines ───────────────────────
                for line in invoices:
                    edited_customer_invoice.objects.using(db).create(
                        cusID               = line.cusID,
                        customer_name       = line.customer_name,
                        invoiceID           = line.invoiceID,
                        order_ID            = line.order_ID,
                        Gdescription        = line.Gdescription,
                        invoice_date        = line.invoice_date,
                        due_date            = line.due_date,
                        itemcode            = line.itemcode,
                        item_name           = line.item_name,
                        item_description    = line.item_description,
                        qty                 = line.qty,
                        unit_p              = line.unit_p,
                        discount            = line.discount,
                        amount              = line.amount,
                        token_id            = line.token_id,
                        amount_paid         = line.amount_paid,
                        amount_expected     = line.amount_expected,
                        cancellation_status = line.cancellation_status,
                        status              = line.status,
                        Userlogin           = line.Userlogin,
                        payment_method      = line.payment_method,
                        Transfer            = line.Transfer,
                        POS                 = line.POS,
                        Cash                = line.Cash,
                        Customer_account    = line.Customer_account,
                        Cheque              = line.Cheque,
                        invoice_state       = line.invoice_state,
                        purchaseP           = line.purchaseP,
                        total_purchaseP     = line.total_purchaseP,
                        outlet              = line.outlet,
                    )

                # ── Step 2: Undo original stock reductions ────────────────
                if first.invoice_state == "Supplied":
                    for line in invoices:
                        IncreaseOutletStockinItemQuantity(
                            db, line.outlet, line.itemcode, line.qty
                        )

                # ── Step 3: Undo accounting entries ──────────────────────
                # Reverse by calling CancelSales logic directly
                accountType = get_customer_or_vendor(db, invoice_id)
                try:
                    sales_account = chart_of_account.objects.using(db).get(
                        account_bankname="Sales account"
                    )
                    if first.amount_paid == first.amount_expected:
                        if accountType == "Customer":
                            cus = customer_table.objects.using(db).filter(
                                customer_code=first.cusID
                            )
                            CreditReceivable(
                                request, db, cus, first.invoice_date,
                                first.Gdescription, "Transfer",
                                sales_account.account_id, first.amount_paid
                            )
                        elif accountType == "Vendor":
                            ven = vendor_table.objects.using(db).filter(
                                custID=first.cusID
                            )
                            CreditPayable(
                                request, db, ven, first.invoice_date,
                                first.Gdescription, "Transfer",
                                sales_account.account_id, first.amount_paid
                            )
                except chart_of_account.DoesNotExist:
                    logger.warning(
                        f"[EditSalesInvoice] Sales account not found for reversal | "
                        f"invoiceID={invoice_id}"
                    )

                # ── Step 4: Delete original invoice lines ─────────────────
                invoices.delete()

                # ── Step 5: Build a fake POST from submitted form data
                #            and call add_new_sales ─────────────────────────
                request.POST = request.POST.copy()

                # Remap submitted form fields to what add_new_sales expects
                new_cusID        = request.POST.get('cusID', '')
                new_date         = request.POST.get('invoice_date')
                new_due_date     = request.POST.get('due_date')
                new_desc         = request.POST.get('Gdescription')
                payment_method   = request.POST.get('payment_method', first.payment_method)

                # Line IDs that were NOT removed
                removed_raw  = request.POST.get('removed_ids', '')
                removed_set  = set(r.strip() for r in removed_raw.split(',') if r.strip())

                line_ids      = request.POST.getlist('line_id[]')
                line_qtys     = request.POST.getlist('line_qty[]')
                line_units    = request.POST.getlist('line_unit[]')
                line_descs    = request.POST.getlist('line_desc[]')
                line_discounts = request.POST.getlist('line_discount[]')
                
                line_itemcodes = request.POST.getlist('line_itemcode[]')

                # New items added in the form
                new_codes     = request.POST.getlist('new_item_code[]')
                new_qtys      = request.POST.getlist('new_qty[]')
                new_units     = request.POST.getlist('new_unit[]')
                new_descs     = request.POST.getlist('new_desc[]')
                new_discounts = request.POST.getlist('new_discount[]')
                
                merge_map = {}          
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
                        # Merge into the existing line
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

                # Apply merges to the existing line quantities
                for idx, lid in enumerate(line_ids):
                    if idx < len(line_itemcodes):
                        code = line_itemcodes[idx]
                        if code in merge_map:
                            current_qty = float(line_qtys[idx]) if line_qtys[idx] else 0
                            line_qtys[idx] = str(current_qty + merge_map[code])

                # Build item lists for add_new_sales
                item_list     = []
                qty_list      = []
                unit_list     = []
                desc_list     = []
                discount_list = []
                amount_list   = []
                name_list     = []
                purchaseP_list = []

                # Existing lines (not removed)
                archived = edited_customer_invoice.objects.using(db).filter(
                    invoiceID=invoice_id
                )
                archived_map = {str(a.id): a for a in archived}

                for idx, lid in enumerate(line_ids):
                    if lid in removed_set:
                        continue
                    # Find original line from archive by matching order
                    orig_lines = list(
                        edited_customer_invoice.objects.using(db)
                        .filter(invoiceID=invoice_id)
                        .order_by('id')
                    )
                    if idx < len(orig_lines):
                        orig = orig_lines[idx]
                        qty      = float(line_qtys[idx]) if line_qtys[idx] else float(orig.qty)
                        unit_p   = float(line_units[idx]) if line_units[idx] else float(orig.unit_p)
                        discount = float(line_discounts[idx]) if line_discounts[idx] else float(orig.discount or 0)
                        amt      = (qty * unit_p) - discount

                        item_list.append(orig.itemcode)
                        qty_list.append(str(qty))
                        unit_list.append(str(unit_p))
                        desc_list.append(line_descs[idx] if line_descs[idx] else orig.item_description)
                        discount_list.append(str(discount))
                        amount_list.append(str(amt))
                        name_list.append(orig.item_name)
                        purchaseP_list.append(str(orig.purchaseP))

                # New items
                for i, code in enumerate(new_codes):
                    if not code:
                        continue
                    try:
                        item_obj = Item.objects.using(db).get(generated_code=code)
                        qty      = float(new_qtys[i]) if new_qtys[i] else 1
                        unit_p   = float(new_units[i]) if new_units[i] else 0
                        discount = float(new_discounts[i]) if new_discounts[i] else 0
                        amt      = (qty * unit_p) - discount

                        item_list.append(code)
                        qty_list.append(str(qty))
                        unit_list.append(str(unit_p))
                        desc_list.append(new_descs[i] if new_descs[i] else '')
                        discount_list.append(str(discount))
                        amount_list.append(str(amt))
                        name_list.append(item_obj.item_name)
                        purchaseP_list.append('0.00')
                    except Item.DoesNotExist:
                        messages.error(request, f"Item {code} not found — skipped")
                        continue

                # Compute total
                grand_total = sum(float(a) for a in amount_list)

                # Patch POST so add_new_sales reads the right values
                request.POST['invoiceID']      = invoice_id
                request.POST['cusID']          = new_cusID or first.cusID
                request.POST['venID']          = request.POST.get('venID', '')
                request.POST['accountType']    = request.POST.get('accountType', 'Customer')
                request.POST['genby']          = request.POST.get('genby', first.customer_name)
                request.POST['invoice_date']   = new_date
                request.POST['due_date']       = new_due_date
                request.POST['order_id']       = request.POST.get('order_id', first.order_ID or '')
                request.POST['Gdescription']   = new_desc
                request.POST['payment_method'] = payment_method
                request.POST['sub-total']      = str(grand_total)
                request.POST['total']          = str(grand_total)
                request.POST['vat']            = request.POST.get('vat', '0')
                request.POST.setlist('item[]',      item_list)
                request.POST.setlist('qty[]',       qty_list)
                request.POST.setlist('unit[]',      unit_list)
                request.POST.setlist('desc[]',      desc_list)
                request.POST.setlist('discount[]',  discount_list)
                request.POST.setlist('amount[]',    amount_list)
                request.POST.setlist('item_name',   name_list)
                request.POST.setlist('purchaseP',   purchaseP_list)

                # Call the real create function
                add_new_sales(request, db)

        except Exception as e:
            logger.error(
                f"[EditSalesInvoice] Failed | invoiceID={invoice_id} | "
                f"{e}\n{traceback.format_exc()}"
            )
            messages.error(request, f"Edit failed: {e}")

        return redirect('customer:EditSalesInvoice', invoice_id=invoice_id)

    context = {
        'invoices':   invoices,
        'first':      first,
        'customers':  customers,
        'vendors':    vendors,
        'items':      items,
        'accounts':   accounts,
        'invoice_id': invoice_id,
        'payments':payments,
        'shipping_method': method,
        'existing_itemcodes': list(existing_itemcodes),
    }
    return render(request, 'customer/EditSalesInvoice.html', context)



from main .views import send_email, send_email_with_pdf

@login_required(login_url='/')
@urls_name(name="Sales Quotes")
def AddSalesQuote(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    company = company_table.objects.get(id=request.user.company_id_id)
    form = None

    if request.method == "POST":
        selected = request.POST.get('accountType')
        
        if selected == "Customer":
            form = add_sales_quote(request, db)
        elif selected == "Vendor":
            form = add_sales_quote(request, db)
            # add_purchase_quote(request, db)
        else:
            messages.error(request, "Select customer or vendor")
            
            send_email()

    context = {
        'customers': customer,
        'vendor': vendor,
        'items': item,
        'form': form,
        'company': company
    }
    return render(request, "customer/NewSalesQuote.html", context)


@login_required(login_url='/')
@urls_name(name="Sales Quotes")
def SalesQuote(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    # customer = customer_table.objects.all()
    # vendor = vendor_table.objects.all()
    # item = Item.objects.all()
    
    # if request.method == "POST":
    #     add_sales_quote(request)
     
    context = {
        
        'company': company,
    }
    return render(request, "customer/SalesQuote.html", context)

@login_required(login_url='/')
@urls_name(name="Sales Order")
def AddSalesOrder(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    company = company_table.objects.get(id=request.user.company_id_id)
    form = None
    if request.method == "POST":
        selected = request.POST['accountType']
       
        if selected == 'Customer':
           form = add_sales_order(request, db)
        elif selected == 'Vendor':
           form =  add_sales_order(request, db)
            # add_purchase_order(request, db)
        else:
            messages.error(request, "Select customer or vendor")
     
    context = {
        
        'customers': customer,
        'vendor':vendor,
        'items': item,
        'form':form,
        'company': company
    }    
    return render(request, "customer/NewSalesOrder.html", context)


@login_required(login_url='/')
@urls_name(name="Sales Order")
def SalesOrder(request):
    # customer = customer_table.objects.all()
    # item = Item.objects.all()

    # if request.method == "POST":
    #     add_sales_order(request)
     
    # context = {
        
    #     'customers': customer,
    #     'items': item
    # }   
    return render(request, "customer/SalesOrder.html")


def GetItemDetails(request, item_id):
    db = request.user.company_id.db_name 
    sales_type = request.GET.get('type')
   
    stock =    CreateOutletStockIn.objects.using(db).filter(item_code=item_id, outlet=request.user.outlet).count()
    
    if sales_type == "sales":
        if stock > 0:
            data, status = getItem(db, item_id)
            return JsonResponse(data, status=status)
        else:
        
            return JsonResponse({'error': 'Item not in '+request.user.outlet}, status=404)
    else:
        data, status = getItem(db, item_id)
        return JsonResponse(data, status=status)

def getItem(db, item_id):
    try:  
        item = Item.objects.using(db).get(generated_code=item_id)
        data = {
                'desc': item.description,
                'name': item.item_name,
                'unit': item.selling_price,
                'purchase': item.purchase_price,
                'generated_code': item.generated_code
            }
        # return JsonResponse(data)
        status = 200
    except Item.DoesNotExist: 
        data = {'error': 'Item not found'}
        status = 404
    return data, status
    
def GetReturnItemDetails(request,invoice, item_id):
    db = request.user.company_id.db_name
 
    try:
       
       item = customer_invoice.objects.using(db).get(invoiceID=invoice, itemcode=item_id)
       data = {
            'desc': item.item_description,
            'name': item.item_name,
            'qty': item.qty,
            'unit': item.amount,
            'purchase': item.purchaseP,
            'generated_code': item.itemcode
        }
       return JsonResponse(data)
    except customer_invoice.DoesNotExist: 
        
        return JsonResponse({'error': 'Item not found'}, status=404)
    

def get_customer_category(request, customer_id):
    """Get customer category for pricing"""
    try:
        db = request.user.company_id.db_name
        customer = customer_table.objects.using(db).get(id=customer_id)
        return JsonResponse({
            'category': customer.category,
            'name': customer.name
        })
    except customer_table.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



def GetCustomerDetails(request, id):
    db = request.user.company_id.db_name
    cusID = request.GET.get("cusID")
    
    lookup = Q(id__iexact=cusID) | Q(customer_code__iexact=cusID)
    try:
       customer = customer_table.objects.using(db).get(lookup)
       data = {
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'category': customer.category,
            'code': customer.customer_code,
            'company': customer.company_name,
            'instant_email': customer.instant_email,
            'balance': customer.Balance
        }
       return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    
def GetCustomerBalance(request, id):
    db = request.user.company_id.db_name
    try:
        credit = receivable.objects.using(db).filter(customer_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
        debit = receivable.objects.using(db).filter(customer_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
        data = Decimal(credit) - Decimal(debit)
        return JsonResponse(data, safe=False)
        
    except receivable.DoesNotExist: 
        return JsonResponse({'error': 'Customer not found'}, status=404)
    
def GetCustomer_or_VendorBalance(request,):
    db = request.user.company_id.db_name
    cusID = request.GET.get("ID")
    accountType = request.GET.get("type")
    if accountType == "Customer":
        id = customer_table.objects.using(db).get(id=cusID).customer_code
        try:
            credit = receivable.objects.using(db).filter(customer_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
            debit = receivable.objects.using(db).filter(customer_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
            data = Decimal(credit) - Decimal(debit)
            return JsonResponse(data, safe=False)
            
        except receivable.DoesNotExist: 
            
            return JsonResponse({'error': 'Customer not found'}, status=404)
    elif accountType == "Vendor":
        
        id = vendor_table.objects.using(db).get(id=cusID).custID
        try:
            credit = payable.objects.using(db).filter(vendor_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
            debit = payable.objects.using(db).filter(vendor_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
            data = Decimal(credit) - Decimal(debit)
            return JsonResponse(data, safe=False)
            
        except payable.DoesNotExist: 
            return JsonResponse({'error': 'Customer not found'}, status=404)
    else:
        return JsonResponse({'error': 'Customer not found'}, status=404)
        

def GetVendorDetails(request, id):
    db = request.user.company_id.db_name
    cusID = request.GET.get("venID")

    lookup = Q(id__iexact=cusID) | Q(custID__iexact=cusID)

    try:
       customer = vendor_table.objects.using(db).get(lookup)
       data = {
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'code': customer.custID,
            'company': customer.company_name,
            'address': customer.address,
        }
       return JsonResponse(data)
    except vendor_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required(login_url='/')
@urls_name(name="Returns Inwards")
def ViewReturnsInWards(request):
   
    return render(request, 'customer/ViewReturnsInWards.html')


@login_required(login_url='/')
@urls_name(name="Returns Inwards")
def ReturnInward(request):
    db = request.user.company_id.db_name
   
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    items = Item.objects.using(db).all()
    invoice_no = customer_invoice.objects.using(db).values("invoiceID").distinct().exclude(invoice_state="Cancelled")
    form = None 
    if request.method == 'POST':
        form = new_return_inwards(request, db)
    context = {
        'customers': customer,
        'vendors': vendor,
        'invoice_no': invoice_no,
        'items': items,
        'form': form,
    }
    
    return render(request, "customer/ReturnsInwards.html", context)

@login_required(login_url='/')
@urls_name(name="Returns Inwards")
def ViewCustomerReturnedItem(request, code, invoice):
    db = request.user.company_id.db_name
    customer = None
    invoice1 = None
    invoices = []

    if code:
        try:
            code_int = int(code)
        except ValueError:
            code_int = None

        lookups = Q()
        if code_int is not None:
            lookups |= Q(id=code_int) | Q(customer_code=code_int)

        customer = customer_table.objects.using(db).filter(lookups).first()
        if customer is None:
            messages.error(request, f"Customer with {code} and {invoice} does not exist")
            return redirect('customer:ViewReturnsInWards')
        else:
            invoice1 = customer_invoice.objects.using(db).filter(cusID=customer, invoiceID=invoice).first()
            invoices = customer_invoice.objects.using(db).filter(cusID=customer, invoiceID=invoice)

    context = { 
        "customer": customer,
        "invoice": invoice1,
        "invoices": invoices
    }

    return render(request, "customer/ViewCustomerReturnedItem.html", context)

def ReturnedInwardChangeDate(request):
    db = request.user.company_id.db_name
    code = request.GET.get('cusID')
    invoiceID = request.GET.get('invoiceID')
    try:
        lookups = Q(id__iexact=code) | Q(customer_code__iexact=code)
   
        customer = customer_table.objects.using(db).get(lookups)
    
        invoice = customer_invoice.objects.using(db).filter(cusID=customer.pk, invoiceID=invoiceID).values().first()
      
        # serialized_data = list(invoice)
        data = {
            'customer': {
                'company': customer.company_name,
                'phone': customer.phone,
                'email': customer.email,
                'code': customer.customer_code,
                'address': customer.address,
                'balance': customer.Balance,
            },
            'invoice': invoice,
        }  
        return JsonResponse(data)
        
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    

def ChangeReturnInwardDate(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        invoice_id = request.POST['invoice_id']
        invoice_date = request.POST['invoice_date']
        new_date = request.POST['new_date']
       
        if new_date:

           invoice = customer_invoice.objects.using(db).filter(invoice_date=invoice_date, invoiceID=invoice_id)
           invoice.update(invoice_date=new_date) 
       

        #    messages.success(request, "Invoice date updated successfully")
           return JsonResponse(new_date, safe=False)
        else:
            return JsonResponse(new_date, safe=False) 


def get_customer_or_vendor(db, invoiceID):
    invoice = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
   
    if customer_table.objects.using(db).filter(customer_code=invoice.cusID):
        return "Customer"
    elif vendor_table.objects.using(db).filter(custID=invoice.cusID):
        return "Vendor"
    else:
        return "None"

def GetInvoiceDetails(request, invoice_id):
    db = request.user.company_id.db_name
    invoiceID = request.GET.get('invoiceId')
    
    try:
        # Fetch all fields related to the given invoice_id
        data = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).values()
        
        
        

        accountType = get_customer_or_vendor(db, invoiceID)
        
        try:
            vat = Vat.objects.using(db).get(source=invoice_id).amount
        except Vat.DoesNotExist:
            vat = None

        serialized_data = {
            'invoice':list(data),
            'accountType':accountType,
            'vat': vat
        }

        return JsonResponse(serialized_data,  safe=False)
    except customer_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
   
from Stock.models import Check_StockLevel_By
from Stock.functions.functionHub.functionHub import *

def CheckItemQty(request):
    db = request.user.company_id.db_name
    item_id = request.GET.get('item_id')
  
    try:
    #    stock_level = Check_StockLevel_By.objects.using(db).first().level
        stock_ = Check_StockLevel_By.objects.using(db).first() #.level or "NO"
      
        if stock_ is not None:
            stock_level = stock_.level
        else:
            stock_level = "NO"
    except Check_StockLevel_By.DoesNotExist:
        stock_level = "NO"

    state = Qty_State(db, item_id)
    

    if state:
        outlet = request.user.outlet
        filter_sales_conditions = Q(outlet=outlet) #& Q(item_code=item_id)
        if stock_level == "YES":    
            qty = get_grand_total_from_outlet_stockin(item_id, CreateOutletStockIn,  outlet, db, filter_sales_conditions)           
        else:  
            qty = get_grand_total_from_stock_log(item_id, CreateOutletStockInLog, CreateStockInLog,  outlet, db, filter_sales_conditions, filter_sales_conditions)
      
    else:
        qty = 100000
    
    return JsonResponse(qty, safe=False)

def Qty_State(db, item_code):
    state = Item.objects.using(db).get(generated_code=item_code).qty_state
    
    if state == "Quantify":
        return True
    else:
        return False
    # try:
    #    qty = CreateOutletStockIn.objects.using(db).filter(item_code=item_id).first().quantity or 0
       
    #    return JsonResponse(qty, safe=False)
    # except CreateOutletStockIn.DoesNotExist: 
    #     
    #     return JsonResponse({'error': 'Item not found'}, status=404)

def StockCheckItemQty(request):
    db = request.user.company_id.db_name
    item_id = request.GET.get('item_id')
    try:
       stock_level = Check_StockLevel_By.objects.using(db).first().level
    except Check_StockLevel_By.DoesNotExist:
        stock_level = "NO"

    outlet = request.user.outlet
    filter_sales_conditions = Q(outlet=outlet) #& Q(item_code=item_id)
    if stock_level == "YES":    
        qty = get_grand_total_from_outlet_stockin(item_id, CreateOutletStockIn,  outlet, db, filter_sales_conditions)           
    else:  
         qty = get_grand_total_from_stock_log(item_id, CreateOutletStockInLog, CreateStockInLog,  outlet, db, filter_sales_conditions, filter_sales_conditions)
   
    return JsonResponse(qty, safe=False)
    # try:
    #    qty = CreateStockIn.objects.using(db).filter(item_code=item_id).first().quantity or 0
    
    #    return JsonResponse(qty, safe=False)
    # except CreateOutletStockIn.DoesNotExist: 
    #     return JsonResponse({'error': 'Item not found'}, status=404)

@login_required(login_url='/')
@urls_name(name="Customer")
def VerifiedPayment(request):
    db = request.user.company_id.db_name
    payments = evidentPayment.objects.using(db).filter(state="Verified").all()

    

    context = {
        'payments': payments
    }
    return render(request, 'customer/VerifiedPayment.html', context)


@login_required(login_url='/')
@urls_name(name="Customer")
def VerifyPayment(request):
    db = request.user.company_id.db_name
    accounts = chart_of_account.objects.using(db).all()
    payments = evidentPayment.objects.using(db).filter(state="Pending").order_by("-created_at")

    

    context = {
        'accounts': accounts,
        'payments': payments
    }
    return render(request, 'customer/VerifyPayment.html', context)

def Verify(request):
    db = request.user.company_id.db_name   
    runfunction = verify_payment(request, db)

    if runfunction:
        return JsonResponse({'message': "Payment Verified "}, safe=False)
    else:
        return JsonResponse({'message': "Error Verifying Payment"}, status=404)



def CancleCustomerInvoicePage(request):
    db              = request.user.company_id.db_name
    customerInvoice = customer_invoice.objects.using(db).filter(
        cancellation_status="0"
    ).exclude(invoice_state="Cancelled")
    getitem = Item.objects.using(db).all()

    # ── AJAX GET — filter ────────────────────────────────────────────────
    if request.method == 'GET' and any([
        request.GET.get('fromdate'),
        request.GET.get('invoice'),
        request.GET.get('sortbyItem'),
    ]):
        qs = customerInvoice

        fromdate   = request.GET.get('fromdate')
        todate     = request.GET.get('todate')
        invoice    = request.GET.get('invoice')
        sortbyItem = request.GET.get('sortbyItem')

        if fromdate and todate:
            qs = qs.filter(invoice_date__date__range=[fromdate, todate])
        if invoice and invoice != '_ _Choose Invoice_ _':
            qs = qs.filter(invoiceID=invoice)
        if sortbyItem and sortbyItem != '_ _Choose Item_ _':
            qs = qs.filter(itemcode=sortbyItem)

        if not qs.exists():
            return JsonResponse({'failed': 'No records found'})

        data = []
        for row in qs.values('id', 'invoiceID', 'cusID', 'invoice_date',
                              'customer_name', 'item_name', 'qty',
                              'amount', 'outlet', 'token_id'):
            row['invoice_date'] = (
                row['invoice_date'].strftime('%d %b %Y')
                if row['invoice_date'] else ''
            )
            data.append(row)

        return JsonResponse({'invoices': data})

    context = {
        'allinvoice': customerInvoice,
        'items':      getitem,
    }
    return render(request, 'customer/CancleCustomerInvoice.html', context)


def CancelSales(request):
    db = request.user.company_id.db_name 
    invoice = request.POST.get("invoice")
    cusID = request.POST.get("cusID")

    try:
        inital_invioice = customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID).first()
        cancel_invioice = customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID)
        accountType = get_customer_or_vendor(db, invoice)

        for item in cancel_invioice:
            outlet= request.user.outlet
            if inital_invioice.invoice_state == "Supplied":
                # Increase outlet stockin returned quatity
                IncreaseOutletStockinItemQuantity(db, outlet, item.itemcode, item.qty)
                
                CreateOutletStockinLog(db, item.invoice_date, item.invoiceID, item.order_ID or "", item.customer_name, " ", outlet, item.Gdescription, item.item_name, item.item_description, item.qty, item.token_id, item.Userlogin,  item.itemcode, item.unit_p, "")

        account = chart_of_account.objects.using(db).get(account_bankname="Sales Account").account_id
        if inital_invioice.amount_paid == inital_invioice.amount_expected:
            #Paid
            if accountType == "Customer":
                cus = customer_table.objects.using(db).filter(customer_code=cusID).first()
                if not cus:
                    return JsonResponse({'error': 'Customer not found'}, status=404)
                CreditReceivable(request, db, cus, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
            
            elif accountType == "Vendor":
                ven = vendor_table.objects.using(db).filter(custID=cusID).first()
                if not ven:
                    return JsonResponse({'error': 'Vendor not found'}, status=404)
                CreditPayable(request, db, ven, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
            
        elif inital_invioice.amount_paid != 0 and inital_invioice.amount_paid < inital_invioice.amount_expected:
            #Partly paid
            if accountType == "Customer":
                cus = customer_table.objects.using(db).filter(customer_code=cusID).first()
                if not cus:
                    return JsonResponse({'error': 'Customer not found'}, status=404)
                CreditReceivable(request, db, cus, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
            
            elif accountType == "Vendor":
                ven = vendor_table.objects.using(db).filter(custID=cusID).first()
                if not ven:
                    return JsonResponse({'error': 'Vendor not found'}, status=404)
                CreditPayable(request, db, ven, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
                    
        else:
            if accountType == "Customer":
                cus = customer_table.objects.using(db).filter(customer_code=cusID).first()
                if not cus:
                    return JsonResponse({'error': 'Customer not found'}, status=404)
                debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Inward")
                CreditReceivable(request, db, cus, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", debtor_account.account_id, inital_invioice.amount_paid)
                CreateLog(db, debtor_account, inital_invioice.amount_expected)
            elif accountType == "Vendor":
                ven = vendor_table.objects.using(db).filter(custID=cusID).first()
                if not ven:
                    return JsonResponse({'error': 'Vendor not found'}, status=404)
                debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Outward")
                CreditPayable(request, db, ven, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", debtor_account.account_id, inital_invioice.amount_paid)
                CreateLog(db, debtor_account, inital_invioice.amount_expected)


        #update customer invoice
        customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID).update(invoiceID = invoice + "_cancelled", invoice_state = "Cancelled", cancellation_status = "1")
                        
        return JsonResponse(True, safe=False)
    except customer_invoice.DoesNotExist:
        return JsonResponse(False, safe=False)


def getCancelledSalesFilter(request, db, con):
    """AJAX helper to filter cancelled sales invoices by date, item, or invoice ID."""
    if request.method == 'GET':
        fromdate = request.GET.get('fromdate')
        todate = request.GET.get('todate')
        invoice = request.GET.get('invoice')
        sortbyItem = request.GET.get('sortbyItem')
        failed = {'failed': "No Data Found"}

        qs = customer_invoice.objects.using(db).filter(con)

        if fromdate and todate:
            from_date, to_date = getdate(fromdate, todate)  # reuse your getdate function
            qs = qs.filter(invoice_date__date__range=(from_date, to_date))

        if sortbyItem and sortbyItem != '_ _Choose Item_ _':
            qs = qs.filter(itemcode=sortbyItem)

        if invoice and invoice != '_ _Choose Invoice_ _':
            qs = qs.filter(invoiceID=invoice)

        if not qs.exists():
            return failed

        result = [{
            'id': obj.id,
            'datetx': obj.invoice_date.strftime('%Y-%m-%d %H:%M:%S') if obj.invoice_date else None,
            'invoice_no': obj.invoiceID,
            'item': obj.item_name,
            'quantity': str(obj.qty),
            'item_decription': obj.item_description,
            'token_id': obj.token_id,
            'customer_name': obj.customer_name,
            'amount': str(obj.amount),
        } for obj in qs]
        return result

def viewCancleSales(request):
    db = request.user.company_id.db_name
    con = Q(cancellation_status="1") | Q(invoice_state="Cancelled")
    cancelled_invoices = customer_invoice.objects.using(db).filter(con).distinct()
    getitem = Item.objects.using(db).all()

    context = {
        'allinvoice': cancelled_invoices,
        'items':      getitem,
        'title':      'Cancelled Sales Invoices',
        'type':       'viewsalescancelled',
    }

    # Only run AJAX filter if at least one filter param is present
    has_filter = any([
        request.GET.get('fromdate'),
        request.GET.get('todate'),
        request.GET.get('invoice'),
        request.GET.get('sortbyItem'),
    ])

    if request.method == 'GET' and has_filter:
        stockinlog = getCancelledSalesFilter(request, db, con)
        if isinstance(stockinlog, dict) and 'failed' in stockinlog:
            return JsonResponse(stockinlog)
        return JsonResponse({'stockin': stockinlog})

    return render(request, 'customer/viewCancleSales.html', context)

def Edit_incoice(request):
    db = request.user.company_id.db_name 
    if request.method == "POST":
        form = edit(request, db)

    # Redirect to the current URL
    return redirect('customer:ReturnInward')

def supply_pending_invoice(request):
    db = request.user.company_id.db_name 
    invoice = request.POST.get("invoice")
    cusID = request.POST.get("cusID")

    try:
        invioice = customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID, invoice_state='Pending')
       
        return JsonResponse(True, safe=False)
    except customer_invoice.DoesNotExist:
        return JsonResponse(False, safe=False)
    



def get_shipping_cost(request, itemcode, city):
    db = request.user.company_id.db_name
    if request.method == 'GET':
        qty = request.GET.get('qty')
        try:
           address = shipping_addr.objects.using("afrikbook_client").get(id=city)
           try:
              cost = addressShippingPrice.objects.using(db).get(generated_code=itemcode, city=address.city, country=address.country).cost
              data = cost * decimal.Decimal(qty)
           except addressShippingPrice.DoesNotExist:
               data = 0.00
        except shipping_addr.DoesNotExist:
            data = 0.00
     
    return JsonResponse({'data': data}, safe=False)
