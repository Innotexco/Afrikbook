from vendor.forms import VendorInovoiceForm
from django.contrib import messages
from django.http import HttpResponse
from account.models import account_log, chart_of_account
from Stock.models import CreateStockIn, CreateStockInLog, CreateOutletStockIn, CreateOutletStockInLog
from settings.models import sales_outlet
from main.models import User
from Stock.functions.functionHub.functionHub import resolve_item_name, _seq_at, fill_stock_row_item

import decimal


def add_stockin(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    invoice_id = request.POST.get('invoiceID')
    
    warehouse = request.POST.get('warehouse')
    outlet = request.POST.get('outlet')
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
    

    

    stock_in = CreateStockIn.objects.all()
    source = "Stockin"
    

    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1

            if warehouse != "":
             
                stock_in_query = CreateStockIn.objects.using(db).filter(warehouse=warehouse, item_code=itemcode[i])
                resolved_name = resolve_item_name(db, itemcode[i], _seq_at(item_name, i))
                if stock_in_query.exists():
                    # If the record exists, update the quantity
                    stock_in = stock_in_query.first()
                    stock_in.quantity += int(quantities[i])
                    fill_stock_row_item(stock_in, db, resolved_name)
                    stock_in.save(using=db)
                else:
                    # If the record does not exist, create a new one
                    stock_in = CreateStockIn(
                        supplier=vendor_name,
                        invoice_no=invoice_id,
                        warehouse=warehouse,
                        outlet="",
                        description=Gdescription,
                        item=resolved_name,
                        item_decription=item_descriptions[i],
                        quantity=int(quantities[i]),
                        manufacture_date=invoice_date,
                        expiry_date=due_date,
                        item_code=itemcode[i]
                    )
                    stock_in.save(using=db)

                stockin_log = CreateStockInLog(
                    supplier = vendor_name,
                    invoice_no=invoice_id,
                    warehouse = warehouse,
                    outlet = "",
                    description = Gdescription,
                    item = resolved_name,
                    item_decription = item_descriptions[i],
                    quantity = quantities[i],
                    source = source,
                    manufacture_date = invoice_date,
                    expiry_date = due_date,
                    item_code = itemcode[i]
                )
                stockin_log.save(using=db)
                if not message_displayed:
                    messages.success(request, "Stockin successful")
                    message_displayed = True
            else:
               if not message_displayed:
                    messages.error(request, "Select Warehouse")
                    message_displayed = True



               
