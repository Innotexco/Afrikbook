from vendor.forms import VendorInovoiceForm
from django.contrib import messages
from django.http import HttpResponse
from account.models import account_log, chart_of_account
from Stock.models import CreateStockIn, CreateStockInLog, CreateOutletStockIn, CreateOutletStockInLog, CreateStockout, StockOutLog, CreateStockoutOrder
from settings.models import sales_outlet
from main.models import User

import decimal


def add_stockout(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    invoice_id = request.POST.get('invoiceID')

    warehouse = request.POST.get('warehouse')
    vendor_name = "Isdore"
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

   

    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            if warehouse != "": 
                  
                stock_out = CreateStockoutOrder(
                    invoice_no=invoice_id,
                    customer=vendor_name,
                    warehouse=warehouse,
                    description=Gdescription,
                    item_description=item_descriptions[i],
                    item_code=itemcode[i],
                    item=item_name[i],
                    quantity=int(quantities[i]),
                    stockout_status= "Pending"
                )
                stock_out.save(using=db)

               
                if not message_displayed:
                    messages.success(request, "Stockout Created successfully")
                    message_displayed = True
            else:
               if not message_displayed:
                    messages.error(request, "Select Warehouse")
                    message_displayed = True



def release_order(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    invoice_id = request.POST.get('invoiceID')

    warehouse = request.POST.get('warehouse')
    customer = request.POST.get('customer')
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

    
   

    source = "Stockout"

    # stock_in = Stock_In.objects.get(wa`rehouse=warehouse, item_code=itemcode)


    stock_in = CreateStockIn.objects.all()
    

    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or decimal.Decimal(quantities[i]) == 0.00:
                #Automatically change the quantity to 1
                quantities[i] = 1
                
        
            if invoice_id != "":
                if warehouse != "":   
                    stock_in_query = CreateStockIn.objects.using(db).filter(warehouse=warehouse, item_code=itemcode[i])
                    if stock_in_query.exists():
                        # If the record exists, update the quantity
                        stock_in = stock_in_query.first()
                        stock_in.quantity -= decimal.Decimal(quantities[i])
                        stock_in.save()

                        CreateStockoutOrder.objects.using(db).filter(invoice_no=invoice_id, warehouse=warehouse, item=item_name[i]).update(stockout_status="Supplied")

                        stock_out = CreateStockout(
                            invoice_no=invoice_id,
                            customer=customer,
                            warehouse=warehouse,
                            description=Gdescription,
                            item_description=item_descriptions[i],
                            item=item_name[i],
                            quantity=quantities[i],
                            stockout_status= "Supplied"
                        )
                        stock_out.save(using=db)
                    else:
                        # If the record does not exist, create a new one
                        stock_in = CreateStockIn(
                            supplier=customer,
                            invoice_no=invoice_id,
                            warehouse=warehouse,
                            outlet="",
                            description=Gdescription,
                            item=item_name[i],
                            item_decription=item_descriptions[i],
                            quantity=quantities[i],
                            manufacture_date=invoice_date,
                            expiry_date=due_date,
                            item_code=itemcode[i]
                        )
                        stock_in.save(using=db)

                        stockin_log = CreateStockInLog(
                            supplier = customer,
                            invoice_no=invoice_id,
                            warehouse = warehouse,
                            outlet = "",
                            description = Gdescription,
                            item = item_name[i],
                            item_decription = item_descriptions[i],
                            quantity = quantities[i],
                            source = source,
                            manufacture_date = invoice_date,
                            expiry_date = due_date,
                            item_code = itemcode[i]
                        )
                        stockin_log.save(using=db)

                        stock_in_query = CreateStockIn.objects.using(db).filter(warehouse=warehouse, item_code=itemcode[i])
                    
                        # If the record exists, update the quantity
                        if stock_in_query.exists():
                            stock_in = stock_in_query.first()
                            stock_in.quantity -= decimal.Decimal(quantities[i])
                            stock_in.save()
                        
                        CreateStockoutOrder.objects.using(db).filter(warehouse=warehouse, item_code=itemcode[i]).update(stockout_status="Supplied")

                        stock_out = CreateStockout(
                            invoice_no=invoice_id,
                            customer=customer,
                            warehouse=warehouse,
                            description=Gdescription,
                            item_description=item_descriptions[i],
                            item=item_name[i],
                            quantity=decimal.Decimal(quantities[i]),
                            stockout_status="Supplied"
                        )
                        stock_out.save(using=db)

                    stockout_log = StockOutLog(
                        invoice_no=invoice_id,
                        customer = customer,
                        warehouse = warehouse,
                        description = Gdescription,
                        item = item_name[i],
                        item_description = item_descriptions[i],
                        quantity = quantities[i],
                        stockout_status= "Supplied"
                    )
                    stockout_log.save(using=db)
                    if not message_displayed:
                        messages.success(request, "Stockout successful")
                        message_displayed = True
                else:
                    if not message_displayed:
                        messages.error(request, "Select Warehouse")
                        message_displayed = True
            else:
                if not message_displayed:
                    messages.error(request, "Select Release Order number")
                    message_displayed = True



               