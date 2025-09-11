from vendor.forms import VendorOrderForm
from django.contrib import messages
from django.http import HttpResponse


def add_purchase_order(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    quote_dates = request.POST['order_date']
    referenceID = request.POST['referenceID']
    Gdescription = request.POST['Gdescription']
    genby = request.POST['genby']
    item_name = request.POST.getlist('item_name')
    itemcode = request.POST.getlist('item[]')
    item_description = request.POST.getlist('desc[]')
    quantities = request.POST.getlist('qty[]')
    unit = request.POST.getlist('unit[]')
    discount = request.POST.getlist('discount[]')
    amount = request.POST.getlist('amount[]')
    total = request.POST['total']
    

    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            form_data = {
                'genby': genby,
                'order_date': quote_dates,
                'referenceID': referenceID,
                'Gdescription': Gdescription,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_description': item_description[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'total': total
            }
            
            form = VendorOrderForm(form_data)
            if form.is_valid():
                form_i = form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.save(using=db)
                # Display the success message only once
                if not message_displayed:
                    messages.success(request, "Sales Order was added successfully")
                    message_displayed = True  # Update the message_displayed variable
            else:
                #return HttpResponse('Error')
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
