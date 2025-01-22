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


def add_purchase_invoice(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    invoice_id = request.POST.get('invoiceID')
    order_id = request.POST.get('orderID')

    account_id = request.POST.get('account_id')
    warehouse = request.POST.get('warehouse')
    p_method = request.POST.get('source')
    outlet = request.POST.get('outlet')
    vendor_name = request.POST.get('vendor_name')
    Gdescription = request.POST.get('Gdescription')
    invoice_date = request.POST.get('invoice_date')
    due_date = request.POST.get('due_date')
    item_name = request.POST.getlist('item_name')
    itemcode = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities = request.POST.getlist('qty[]')
    unit = request.POST.getlist('unit[]')
    discount = request.POST.getlist('discount[]')
    amount = request.POST.getlist('amount[]')
    total = request.POST.get('total')
    vat = request.POST.get('vat')
    amount_paid = request.POST.get('amount_paid')
    amount_expected = request.POST.get('amount_expected')
    


    # total = float(request.POST['total'])
  
    if p_method == "Cash":
        amount_paid = total
        amount_expected = total
    else:
        amount_paid = 0.00
        amount_expected = total

  
    # Get Chart Of Account
    bank_account = chart_of_account.objects.using(db).get(account_bankname='Purchase Account')
    # vendor_name = vendor_name + "("+ bank_account.series_name + ")"
    
    transaction_source = "Purchase"
    source = "New Stock"

    if vendor_name:
        ven = vendor_table.objects.using(db).get(id=vendor_name)
       

    
    # Count the number of records in the Sales_Outlet model
    # outlet_count = sales_outlet.objects.count()
    check_outlet = User.objects.get(id = request.user.id).outlet

    stock_in = CreateStockIn.objects.using(db).all()
    

    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0

        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            vendor_invoice_form_data = {
                'cusID': ven.custID,
                'vendor_name': ven.name,
                'invoiceID': invoice_id,
                'orderID': order_id,
                'Gdescription': Gdescription,
                'invoice_date': invoice_date,
                'due_date' : due_date,
                'amount_paid' : amount_paid,
                'amount_expected': amount_expected,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_descriptions': item_descriptions[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'total': total
            }
            
            vendor_form = VendorInovoiceForm(vendor_invoice_form_data)
            
            
            if vendor_form.is_valid():
                
                form_i = vendor_form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.save(using=db)

                
                # stock_in = Stock_In.objects.filter(warehouse=warehouse, item_code=itemcode).first()
                
                ## INSTANT TRANSFER
                if warehouse is not '' and outlet is not '':
                    # save Item In Stockin table first
                    try:
                        stock_in_query = CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
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
                ## INSERT TO DEFAULT OUTLET IN USER TABLE
                elif warehouse is '' and outlet is '':
                    if check_outlet:
                        try:
                            stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=check_outlet, item_code=itemcode[i])
                            stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                            stock_in_outlet_query.save(using=db)
                        except CreateOutletStockIn.DoesNotExist:
                            saveOutlet(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                        saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)

                else:
                    # STOCK IN WAREHOUSE
                    if warehouse is not '':
                        try:
                            stock_in_query = CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
                            stock_in_query.quantity += int(quantities[i])
                            stock_in_query.save(using=db)
                        except CreateStockIn.DoesNotExist:
                            saveStockin(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)
                        saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)


                    # STOCK IN OUTLET
                    if outlet is not '':
                        try:
                            stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode[i])
                            stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                            stock_in_outlet_query.save(using=db)
                        except CreateOutletStockIn.DoesNotExist:
                            saveOutlet(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                        saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)



                



                if not message_displayed:
                    if p_method == "Cash":
                 
                        DebitPayable(request, db, ven, invoice_date, Gdescription, p_method, bank_account.account_id,  total)
                        
                        acct_log = account_log(
                        transaction_source  = transaction_source,
                        amount              = total,
                        date                = invoice_date,
                        account             = bank_account.account_id,
                        account_type        = bank_account.account_type,
                        Userlogin = request.user.username
                        )
                        # acct_log.save(using=db)
                        CreateLog(db, bank_account, total)
                    
                    else:
                        

                        bank_account.actual_balance += decimal.Decimal(total)
                        # bank_account.save()

                        CreateLog(db, bank_account, total)

                        acct_log = account_log(
                            transaction_source  = transaction_source,
                            amount              = total,
                            date                = invoice_date,
                            account             = bank_account.account_id,
                            account_type        = bank_account.account_type,
                            Userlogin = request.user.username
                        )
                        # acct_log.save(using=db)
                    create_add_vat(db, invoice_id, vat)
                    messages.success(request, "Purchase Invoice was added successfully")
                    message_displayed = True  # Update the message_displayed variable
            else:
                print(vendor_form.errors)
                return HttpResponse('error')
            





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