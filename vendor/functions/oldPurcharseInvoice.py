from vendor.forms import VendorInovoiceForm
from django.contrib import messages
from django.http import HttpResponse
from account.models import account_log, chart_of_account
from Stock.models import CreateStockIn, CreateStockInLog, CreateOutletStockIn, CreateOutletStockInLog
from settings.models import sales_outlet
from main.models import User

import decimal


def add_purchase_invoice(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    invoice_id = request.POST.get('invoiceID')
    order_id = request.POST.get('orderID')

    account_id = request.POST.get('account_id')
    warehouse = request.POST.get('warehouse')
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
    amount_paid = request.POST.get('amount_paid')
    amount_expected = request.POST.get('amount_expected')

    vat = request.POST['vat'][:-1]
    # total = float(request.POST['total'])
  
    if vat:
        amount_paid = (total - float(vat)) / 100
        amount_expected = total
    else:
        amount_paid = total
        amount_expected = total


    # Get Chart Of Account
    bank_account = chart_of_account.objects.using(db).get(account_id=account_id)
    vendor_name = vendor_name + "("+ bank_account.series_name + ")"
    
    transaction_source = "Purchase"
    source = "New Stock"

    # stock_in = Stock_In.objects.get(wa`rehouse=warehouse, item_code=itemcode)

    
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
                'vendor_name': vendor_name,
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
                
                # INSTANT TRANSFER
                # if warehouse is not None and outlet is not None:
                #     # save Item In Stockin table first
                #     try:
                #         stock_in_query = CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
                #         saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)
                #     except CreateStockIn.DoesNotExist:
                #         pass

                #     try:
                #         stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode[i])
                #         stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                #         stock_in_outlet_query.save(using=db)
                #     except CreateOutletStockIn.DoesNotExist:
                #         saveOutlet(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                #     saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, warehouse)



                # INSERT TO DEFAULT OUTLET IN USER TABLE
                # if warehouse is None and outlet is None:
                #     if check_outlet:
                #         try:
                #             stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=check_outlet, item_code=itemcode[i])
                #             stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                #             stock_in_outlet_query.save(using=db)
                #         except CreateOutletStockIn.DoesNotExist:
                #             saveOutlet(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                #         saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)

                # STOCK IN WAREHOUSE
                if warehouse is not None:
                    try:
                        stock_in_query = CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
                        stock_in_query.quantity += int(quantities[i])
                        stock_in_query.save(using=db)
                    except CreateStockIn.DoesNotExist:
                        saveStockin(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)
                    saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)


                # STOCK IN OUTLET
                # if outlet is not None:
                #     try:
                #         stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode[i])
                #         stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                #         stock_in_outlet_query.save(using=db)
                #     except CreateOutletStockIn.DoesNotExist:
                #         saveOutlet(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                #     saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)





                # stock_in_query = CreateStockIn.objects.using(db).filter(warehouse=warehouse, outlet=outlet, item_code=itemcode[i])
                # if stock_in_query.exists():
                #     # If the record exists, update the quantity
                #     stock_in = stock_in_query.first()
                #     stock_in.quantity += int(quantities[i])
                #     # stock_in.save()
                # else:
                #     # If the record does not exist, create a new one
                #     stock_in = CreateStockIn(
                #         supplier=vendor_name,
                #         invoice_no=invoice_id,
                #         order_no=order_id,
                #         warehouse=warehouse,
                #         outlet=outlet,
                #         description=Gdescription,
                #         item=item_name[i],
                #         item_decription=item_descriptions[i],
                #         quantity=int(quantities[i]),
                #         manufacture_date=invoice_date,
                #         expiry_date=due_date,
                #         item_code=itemcode[i],
                #         Userlogin = request.user.username
                #     )
                #     # stock_in.save()

                # stockin_log = CreateStockInLog(
                #     supplier = vendor_name,
                #     invoice_no=invoice_id,
                #     order_no=order_id,
                #     warehouse = warehouse,
                #     outlet = outlet,
                #     description = Gdescription,
                #     item = item_name[i],
                #     item_decription = item_descriptions[i],
                #     quantity = quantities[i],
                #     source = source,
                #     manufacture_date = invoice_date,
                #     expiry_date = due_date,
                #     item_code = itemcode[i],
                #     Userlogin = request.user.username
                # )
                # stockin_log.save(using=db)



                # Outlet_StockIn_Form

                # if check_outlet:
                # if outlet is None:
                #     print("There is exactly one record in Sales_Outlet.")

                #     stock_in_query = CreateStockIn.objects.using(db).filter(warehouse=warehouse, item_code=itemcode[i])
                #     if stock_in_query.exists():
                #         # If the record exists, update the quantity
                #         stock_in = stock_in_query.first()
                #         stock_in.quantity -= int(quantities[i])
                #         stock_in.save()



                #     outletstockin_query = CreateOutletStockIn.objects.using(db).filter(warehouse=warehouse, item_code=itemcode[i])
                #     if outletstockin_query.exists():
                #         # If the record exists, update the quantity
                #         outletstockin = outletstockin_query.first()
                #         outletstockin.quantity = int(outletstockin.quantity) + int(quantities[i])
                #         outletstockin.save()

                #     else:
            
                #         outlet_stockin = CreateOutletStockIn(
                #             datetx = invoice_date,
                #             supplier = vendor_name,
                #             invoice_no=invoice_id,
                #             order_no=order_id,
                #             # warehouse = warehouse,
                #             outlet = outlet,
                #             description = Gdescription,
                #             item = item_name[i],
                #             item_decription = item_descriptions[i],
                #             quantity = int(quantities[i]),
                #             item_code = itemcode[i],
                #             Userlogin = request.user.username
                #         )
                #         outlet_stockin.save(using=db)


                #     outlet_stockin_log = CreateOutletStockInLog(
                #         datetx = invoice_date,
                #         supplier = vendor_name,
                #         invoice_no=invoice_id,
                #         order_no=order_id,
                #         warehouse = warehouse,
                #         outlet = outlet,
                #         description = Gdescription,
                #         item = item_name[i],
                #         item_decription = item_descriptions[i],
                #         quantity = quantities[i],
                #         item_code = itemcode[i],
                #         Userlogin = request.user.username
                #     )
                #     outlet_stockin_log.save(using=db)

                    # elif outlet_count > 1:
                    #     print("There is more than one record in Sales_Outlet.")
                    #     pass
                # else:
                #     print("There are no records in Sales_Outlet.")
                #     stock_in_query = CreateStockIn.objects.using(db).filter(warehouse=warehouse, outlet=outlet, item_code=itemcode[i])
                #     if stock_in_query.exists():
                #         # If the record exists, update the quantity
                #         stock_in = stock_in_query.first()
                #         stock_in.quantity += int(quantities[i])
                #         stock_in.save()
                #     else:
                #         # If the record does not exist, create a new one
                #         stock_in = CreateStockIn(
                #             supplier=vendor_name,
                #             invoice_no=invoice_id,
                #             order_no=order_id,
                #             warehouse=warehouse,
                #             outlet=outlet,
                #             description=Gdescription,
                #             item=item_name[i],
                #             item_decription=item_descriptions[i],
                #             quantity=int(quantities[i]),
                #             manufacture_date=invoice_date,
                #             expiry_date=due_date,
                #             item_code=itemcode[i],
                #             Userlogin = request.user.username
                #         )
                #         stock_in.save(using=db)




                
                if not message_displayed:

                    bank_account.actual_balance += decimal.Decimal(total)
                    bank_account.save()

                    acct_log = account_log(
                        transaction_source  = transaction_source,
                        amount              = total,
                        date                = invoice_date,
                        account             = bank_account.account_id,
                        account_type        = bank_account.account_type,
                        Userlogin = request.user.username
                    )
                    acct_log.save(using=db)

                    messages.success(request, "Purchase Invoice was added successfully")
                    message_displayed = True  # Update the message_displayed variable
            else:
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