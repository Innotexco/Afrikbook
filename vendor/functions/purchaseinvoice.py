from vendor.forms import VendorInovoiceForm
from django.contrib import messages
from django.http import HttpResponse
from account.models import account_log, chart_of_account, Expenses_account
from Stock.models import CreateStockIn, CreateStockInLog, CreateOutletStockIn, CreateOutletStockInLog
from settings.models import sales_outlet
from main.models import User
from vendor.models import vendor_table
from customer.functions.generalFunction import *
from customer.functions.newsalesfunc import *
import decimal
from django.db import transaction



def add_purchase_invoice(request, db):

    message_displayed = False

    invoice_id   = request.POST.get('invoiceID')
    order_id     = request.POST.get('orderID')
    account_id   = request.POST.get('account_id')
    warehouse    = request.POST.get('warehouse')
    p_method     = request.POST.get('source')
    outlet       = request.POST.get('outlet')
    vendor_name  = request.POST.get('vendor_name')
    Gdescription = request.POST.get('Gdescription')
    invoice_date = request.POST.get('invoice_date')
    due_date     = request.POST.get('due_date')
    item_name         = request.POST.getlist('item_name')
    itemcode          = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities        = request.POST.getlist('qty[]')
    unit              = request.POST.getlist('unit[]')
    discount          = request.POST.getlist('discount[]')
    amount            = request.POST.getlist('amount[]')
    total        = request.POST.get('total')
    vat          = request.POST.get('vat')
    amount_paid  = request.POST.get('amount_paid')
    amount_expected = request.POST.get('amount_expected')

    if p_method == "Cash":
        amount_paid     = total
        amount_expected = total
    else:
        amount_paid     = 0.00
        amount_expected = total

    # ── Resolve account and vendor before entering the transaction ────────────
    try:
        bank_account = chart_of_account.objects.using(db).get(account_id='2067-Purchase')
    except chart_of_account.DoesNotExist:
        messages.error(request, "Purchase Account not found in chart of accounts.")
        return None

    if not vendor_name:
        messages.error(request, "Vendor is required.")
        return None

    try:
        ven = vendor_table.objects.using(db).get(id=vendor_name)
    except vendor_table.DoesNotExist:
        messages.error(request, "Vendor not found.")
        return None

    transaction_source = "Purchase"
    check_outlet = User.objects.get(id=request.user.id).outlet

    try:
        with transaction.atomic(using=db):

            for i in range(len(itemcode)):

                if str(itemcode[i]) != "0":
                    if not quantities[i] or int(quantities[i]) == 0:
                        quantities[i] = 1

                    vendor_invoice_form_data = {
                        'cusID':             ven.custID,
                        'vendor_name':       ven.name,
                        'invoiceID':         invoice_id,
                        'orderID':           order_id,
                        'Gdescription':      Gdescription,
                        'invoice_date':      invoice_date,
                        'due_date':          due_date,
                        'amount_paid':       amount_paid,
                        'amount_expected':   amount_expected,
                        'item_name':         item_name[i],
                        'itemcode':          itemcode[i],
                        'item_descriptions': item_descriptions[i],
                        'qty':               quantities[i],
                        'unit_p':            unit[i],
                        'discount':          discount[i],
                        'amount':            amount[i],
                        'total':             total,
                    }

                    vendor_form = VendorInovoiceForm(vendor_invoice_form_data)

                    if not vendor_form.is_valid():
                        messages.error(request, f"Invalid data on item {i + 1}: {vendor_form.errors}")
                        raise ValueError(f"Form invalid on item {i + 1}")

                    # ── Save invoice line ─────────────────────────────────────
                    form_i = vendor_form.save(commit=False)
                    form_i.Userlogin = request.user.username
                    form_i.save(using=db)

                    # ── Stock updates ─────────────────────────────────────────
                    try:
                        if warehouse and outlet:
                            try:
                                CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
                                saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)
                            except CreateStockIn.DoesNotExist:
                                pass

                            try:
                                stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode[i])
                                stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                                stock_in_outlet_query.save(using=db)
                            except CreateOutletStockIn.DoesNotExist:
                                saveOutlet(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                            saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, warehouse)

                        elif not warehouse and not outlet:
                            if check_outlet:
                                try:
                                    stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=check_outlet, item_code=itemcode[i])
                                    stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                                    stock_in_outlet_query.save(using=db)
                                except CreateOutletStockIn.DoesNotExist:
                                    saveOutlet(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                                saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)

                        else:
                            if warehouse:
                                try:
                                    stock_in_query = CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
                                    stock_in_query.quantity += int(quantities[i])
                                    stock_in_query.save(using=db)
                                except CreateStockIn.DoesNotExist:
                                    saveStockin(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)
                                saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)

                            if outlet:
                                try:
                                    stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode[i])
                                    stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                                    stock_in_outlet_query.save(using=db)
                                except CreateOutletStockIn.DoesNotExist:
                                    saveOutlet(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                                saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)

                    except Exception as e:
                        messages.error(request, f"Stock update failed for item {i + 1}: {e}")
                        raise  # triggers rollback

                    # ── Accounting — runs once per invoice, not per line ──────
                    if not message_displayed:
                        try:
                            if p_method == "Cash":
                                DebitPayable(request, db, ven, invoice_date, Gdescription, p_method, bank_account.account_id, total)
                                account_log.objects.using(db).create(
                                    transaction_source = transaction_source,
                                    amount             = total,
                                    date               = invoice_date,
                                    account            = bank_account.account_id,
                                    account_type       = bank_account.account_type,
                                    Userlogin          = request.user.username,
                                )
                                CreateLog(db, bank_account, total)
                            else:
                                bank_account.actual_balance += decimal.Decimal(total)
                                bank_account.save(using=db)
                                CreateLog(db, bank_account, total)
                                account_log.objects.using(db).create(
                                    transaction_source = transaction_source,
                                    amount             = total,
                                    date               = invoice_date,
                                    account            = bank_account.account_id,
                                    account_type       = bank_account.account_type,
                                    Userlogin          = request.user.username,
                                )

                            create_add_vat(db, invoice_id, vat)
                            messages.success(request, "Purchase Invoice was added successfully")
                            message_displayed = True

                        except Exception as e:
                            messages.error(request, f"Accounting entry failed: {e}")
                            raise  # triggers rollback

    except Exception as e:
        # Atomic block rolled back — log and return
        if not message_displayed:
            if not any(m for m in messages.get_messages(request)):
                messages.error(request, "Purchase Invoice could not be saved. All changes have been rolled back.")
        return None




def saveStockin(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i):
    stock_in = CreateStockIn(
        supplier=vendor_name,
        invoice_no=invoice_id,
        order_no=order_id,
        warehouse=warehouse,
        description=Gdescription,
        item=item_name[i],
        item_decription=item_descriptions[i],
        quantity=int(quantities[i]),
        manufacture_date=invoice_date,
        expiry_date=due_date,
        item_code=itemcode[i],
        Userlogin = request.user.username
    )
    stock_in.save(using=db)


def saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i):
    stock_in = CreateStockInLog(
        supplier=vendor_name,
        invoice_no=invoice_id,
        order_no=order_id,
        outlet=warehouse,
        description=Gdescription,
        item=item_name[i],
        item_decription=item_descriptions[i],
        quantity=int(quantities[i]),
        manufacture_date=invoice_date,
        expiry_date=due_date,
        item_code=itemcode[i],
        Userlogin = request.user.username
    )
    stock_in.save(using=db)


def saveOutlet(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i):
    outlet_stockin = CreateOutletStockIn(
            datetx = invoice_date,
            supplier = vendor_name,
            invoice_no=invoice_id,
            order_no=order_id,
            outlet = check_outlet,
            description = Gdescription,
            item = item_name[i],
            item_decription = item_descriptions[i],
            quantity = int(quantities[i]),
            item_code = itemcode[i],
            Userlogin = request.user.username
        )
    outlet_stockin.save(using=db)

def saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, ware):

    warehouse = None
    if ware is not None:
        warehouse = ware
    outlet_stockin_log = CreateOutletStockInLog(
        datetx = invoice_date,
        supplier = vendor_name,
        invoice_no=invoice_id,
        order_no=order_id,
        outlet = check_outlet,
        warehouse = warehouse,
        description = Gdescription,
        item = item_name[i],
        item_decription = item_descriptions[i],
        quantity = quantities[i],
        item_code = itemcode[i],
        Userlogin = request.user.username
    )
    outlet_stockin_log.save(using=db)