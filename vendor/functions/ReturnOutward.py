from vendor.models import *
from vendor.forms import VendorReturnForm
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from customer.functions.generalFunction import *
from customer.functions.newsalesfunc import *
from account.models import *

def add_return_item(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
    executed = False
   
    refund_date = request.POST['refund_date']
    invoiceID = request.POST['invoiceID']
    reference_ID = "request.POST['reference_ID']"
    Gdescription = request.POST['Gdescription']
    warehouse = request.POST['warehouse']
    genby = request.POST['genby']
    account = request.POST.get('account')
    item_name = request.POST.getlist('item_name')
    itemcode = request.POST.getlist('item[]')
    item_description = request.POST.getlist('desc[]')
    quantities = request.POST.getlist('qty[]')
    unit = request.POST.getlist('unit[]')
    discount = request.POST.getlist('discount[]')
    amount = request.POST.getlist('amount[]')
    total = request.POST['total']
    vat = request.POST.get('vat')
    initial_total = request.POST['initial_total']
    p_method = request.POST['p_method']
    
    
    if genby:
        customer = vendor_table.objects.using(db).get(custID=genby)
        customer_id =customer.custID
        customer_name = customer.name

    
   
    # lookups = Q(amount_paid__iexact=initial_total) | Q(amount_expected__iexact=initial_total)
    # initial_invoice = Vendor_invoice.objects.using(db).filter(lookups, invoiceID=invoiceID)
    invoice2 = Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
            # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            form_data = {
                'genby': genby,
                'refundd_date': refund_date,
                'invoiceID': invoiceID,
                'reference_ID': reference_ID,
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
            
            form = VendorReturnForm(form_data)
            
            if form.is_valid():
                form_i = form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.save(using=db)
                
                #Reduce item quantity in stockin and outlet stickin quantity
                outlet= request.user.outlet
                ReduceStockinItemQuantity(db, warehouse, itemcode[i], quantities[i])
                ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])
                        
                
                # Display the success message only once
                if not message_displayed:
                    Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID, cusID=customer_id).update(invoiceID = invoiceID + "_returned", cancellation = "1")

                    ven = vendor_table.objects.using(db).get(custID=customer_id)
                    ven.refundInvoice += 1
                    ven.save()
                    if invoice2 is not None:
                        try:
                            debtor_account = chart_of_account.objects.using(db).get(account_id=account)
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                        except chart_of_account.MultipleObjectsReturned:
                            debtor_account = chart_of_account.objects.using(db).filter(account_bankname="Return Outward").first()
                        except chart_of_account.DoesNotExist:
                            debtor_account = chart_of_account.objects.using(db).filter(account_bankname="Return Outward").first()

                        if invoice2.amount_paid < invoice2.amount_expected:
                            
                            CreateLog(db, debtor_account, total)
                            #create account log
                            acc_log = account_log(
                                transaction_source  = "Return outward",
                                amount              = total,
                                date                = refund_date,
                                account             = debtor_account.account_id,
                                account_type        = debtor_account.account_type,
                                Userlogin           = request.user.username
                            )
                            # acc_log.save(using=db)
                        else:
                            CreditPayable(request, db, customer, refund_date, Gdescription, p_method, debtor_account.account_id, initial_total)
                            # DebitPayable(request, db, ven, refund_date, Gdescription, p_method, total)

                            CreateLog(db, debtor_account, total)
                            #create account log
                            acc_log = account_log(
                                transaction_source  = "Return outward",
                                amount              = total,
                                date                = refund_date,
                                account             = "",
                                account_type        = "",
                                Userlogin           = request.user.username
                            )
                            # acc_log.save(using=db)
                        create_minus_vat(db, invoiceID+"_returned", vat)
                        # messages.success(request, "Exist with changes")
                        messages.success(request, "Outward Return successfully")
                        message_displayed = True
                    else:
                        messages.error(request, "Invoice ID not found")

                else:
                    return form
            
            
            
            
