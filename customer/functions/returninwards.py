from customer.forms import CustomerSalesForm, ReceivableForm, PayableForm
from django.contrib import messages
from django.http import HttpResponse
from customer.models import *                                                                                         
import uuid, decimal
from vendor.models import vendor_table
from account.models import *
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog, StockAdjustmentLog
from customer.functions.generalFunction import *
from django.db.models import Q

from customer.functions.generalFunction import *
from customer.functions.newsalesfunc import create_add_vat, create_minus_vat



def new_return_inwards(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
    executed = False
   
    refund_date       = request.POST['refund_date']
    order_no          = request.POST['order_no']
    p_method          = request.POST.get('method')
    cusID             = request.POST.get('cusID')
    venID             = request.POST.get('venID')
    customer_name     = request.POST['genby']  
    invoiceID         = request.POST['invoiceID']
    Gdescription      = request.POST['Gdescription']
    accountType       = request.POST['accountType']

    item_name         = request.POST.getlist('item_name')  
    itemcode          = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')    
    quantities        = request.POST.getlist('qty[]')
    unit              = request.POST.getlist('unit[]')
    discount          = request.POST.getlist('discount[]')
    amount            = request.POST.getlist('amount[]')
    vat               = request.POST.get('vat')
    purchaseP         = request.POST.getlist('purchaseP')

    total = request.POST['total']
    initial_total = request.POST['initial_total']
   
 
    int_purchaseP = [int(num) if num.isdigit() else 0 for num in purchaseP ]

    total_purchaseP = sum(int_purchaseP)

    if accountType == "Customer":
        customer = customer_table.objects.using(db).get(customer_code = cusID)
        customer_id =customer.customer_code
        customer_name = customer.name
    elif accountType == "Vendor":
        customer = vendor_table.objects.using(db).get(custID=venID)
        customer_id =customer.custID
        customer_name = customer.name

    invoice2 = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).first()

    lookups = Q(amount_paid__iexact=initial_total) | Q(amount_expected__iexact=initial_total)
    initial_invoice = customer_invoice.objects.using(db).filter(lookups, invoiceID=invoiceID)

    

      
    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or quantities[i] == "0":
                #Automatically change the quantity to 1
                quantities[i] = 1
            
            form_data = {
                'cusID': customer_id,
                'customer_name': customer_name,
                'invoice_date':refund_date,
                'due_date': invoice2.due_date,
                'invoiceID':invoiceID ,
                'order_ID':order_no ,
                'Gdescription': Gdescription,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_description': item_descriptions[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'amount_paid': total,
                'amount_expected': total,
                "invoice_state": "Supplied",
                "cancellation_status":0,
                "status":1,
                "payment_method": p_method,
                "Transfer":0,
                "POS":0,
                "Cash":0,
                "Customer_account":0,
                "Cheque":0,
                "purchaseP":purchaseP[i],
                "total_purchaseP":total_purchaseP,
                "outlet": invoice2.outlet
            }
            invoice_form = CustomerSalesForm(form_data)
           
           
             
            receivable_form = ReceivableForm({"date":refund_date,	"description":Gdescription,"type": "Debit",	"amount": total, "payment_method": p_method,"invoice_status": "Unused"})
            if invoice_form.is_valid() and receivable_form.is_valid():
                
                form_instance = invoice_form.save(commit=False)

                if  str(p_method).lower() == "transfer":
                    form_instance.Transfer = 1
                if  str(p_method).lower() == "pos":
                    form_instance.POS = 1    
                if  str(p_method).lower() == "cash":
                    form_instance.Cash = 1     
                if  str(p_method).lower() == "cheque":
                    form_instance.Cheque = 1

                form_instance.Userlogin = request.user.username 
                # form_instance.save(using=db) 
            
                

                outlet= invoice2.outlet
                # Increase outlet stockin returned quatity
                IncreaseOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])
                
                CreateOutletStockinLog(db, refund_date, invoiceID, order_no, customer_name, " ", outlet, Gdescription, item_name[i], item_descriptions[i], quantities[i], invoice2.token_id, invoice2.Userlogin, itemcode[i], unit[i], "")
                
                            
                
                if not message_displayed:
                    #update customer invoice
                    customer_invoice.objects.using(db).filter(invoiceID=invoiceID, cusID=customer_id).update(invoiceID = invoiceID + "_returned", invoice_state = "Cancelled", cancellation_status = "1", payment_method = p_method)
                    if accountType == "Customer":
                        cus = customer_table.objects.using(db).get(customer_code=cusID)
                        cus.refund_invoice += 1
                        cus.save()
                    elif accountType == "Vendor":
                        ven = vendor_table.objects.using(db).get(CustID=venID)
                        ven.refundInvoice += 1
                        ven.save()
                    
                    if invoice2.amount_paid < invoice2.amount_expected:
                        if accountType == "Customer":
                            debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Inward")
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                            CreateLog(db, debtor_account, total)
                        elif accountType == "Vendor":
                            debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Outward")
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                            CreateLog(db, debtor_account, total)
                        

                        #create account log
                        acc_log = account_log(
                            transaction_source  = "Sales",
                            amount              = total,
                            date                = refund_date,
                            account             = debtor_account.account_id,
                            account_type        = debtor_account.account_type,
                            Userlogin           = request.user.username
                        )
                        # acc_log.save(using=db)
                    else:
                        account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")

                        if accountType == "Customer":
                            CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account.account_id, initial_total)
                            # DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, total)
                        elif accountType == "Vendor":
                            CreditPayable(request, db, ven, refund_date, Gdescription, p_method, account.account_id, initial_total)
                            # DebitPayable(request, db, ven, refund_date, Gdescription, p_method, total)
                        
                       
                        CreateLog(db, account, total)
                        #create account log
                        acc_log = account_log(
                            transaction_source  = "Sales",
                            amount              = total,
                            date                = refund_date,
                            account             = "",
                            account_type        = "",
                            Userlogin           = request.user.username
                        )
                        # acc_log.save(using=db)
                    create_minus_vat(db, invoiceID+ "_returned", vat)
                    # messages.success(request, "Exist with changes")
                    messages.success(request, "Inward Return successfully")
                    message_displayed = True
            else:
                
                return invoice_form
            




def edit(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
    executed = False
   
    refund_date       = request.POST['refund_date']
    order_no          = request.POST['order_no']
    p_method          = request.POST.get('method')
    cusID             = request.POST.get('cusID')
    venID             = request.POST.get('venID')
    customer_name     = request.POST['genby']  
    invoiceID         = request.POST['invoiceID']
    Gdescription      = request.POST['Gdescription']
    accountType       = request.POST['accountType']

    item_name         = request.POST.getlist('item_name')  
    itemcode          = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')    
    quantities        = request.POST.getlist('qty[]')
    unit              = request.POST.getlist('unit[]')
    discount          = request.POST.getlist('discount[]')
    amount            = request.POST.getlist('amount[]')
    vat               = request.POST.get('vat')
    purchaseP         = request.POST.getlist('purchaseP')

    total = request.POST['total']
    initial_total = request.POST['initial_total']
   
 
    int_purchaseP = [int(num) if num.isdigit() else 0 for num in purchaseP ]

    total_purchaseP = sum(int_purchaseP)

    if accountType == "Customer":
        customer = customer_table.objects.using(db).get(customer_code = cusID)
        customer_id =customer.customer_code
        customer_name = customer.name
    elif accountType == "Vendor":
        customer = vendor_table.objects.using(db).get(custID=venID)
        customer_id =customer.custID
        customer_name = customer.name

    invoice2 = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).first()

    lookups = Q(amount_paid__iexact=initial_total) | Q(amount_expected__iexact=initial_total)
    initial_invoice = customer_invoice.objects.using(db).filter(lookups, invoiceID=invoiceID)

    

      
    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0
        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
            
            form_data = {
                'cusID': customer_id,
                'customer_name': customer_name,
                'invoice_date':refund_date,
                'due_date': invoice2.due_date,
                'invoiceID':invoiceID ,
                'order_ID':order_no ,
                'Gdescription': Gdescription,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_description': item_descriptions[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'amount_paid': total,
                'amount_expected': total,
                "invoice_state": "Supplied",
                "cancellation_status":0,
                "status":1,
                "payment_method": p_method,
                "Transfer":0,
                "POS":0,
                "Cash":0,
                "Customer_account":0,
                "Cheque":0,
                "purchaseP":purchaseP[i],
                "total_purchaseP":total_purchaseP
            }
            invoice_form = CustomerSalesForm(form_data)
           

             
            receivable_form = ReceivableForm({"date":refund_date,	"description":Gdescription,"type": "Debit",	"amount": total, "payment_method": p_method,"invoice_status": "Unused"})
            if invoice_form.is_valid() and receivable_form.is_valid():
                
                form_instance = invoice_form.save(commit=False)

                if  str(p_method).lower() == "transfer":
                    form_instance.Transfer = 1
                if  str(p_method).lower() == "pos":
                    form_instance.POS = 1    
                if  str(p_method).lower() == "cash":
                    form_instance.Cash = 1     
                if  str(p_method).lower() == "cheque":
                    form_instance.Cheque = 1

                form_instance.Userlogin = request.user.username 
                
            
                
                outlet= request.user.outlet
                for invoice in initial_invoice:
                    # Increase outlet stockin returned quatity
                    IncreaseOutletStockinItemQuantity(db, outlet, invoice.itemcode, invoice.qty)
                    
                    CreateOutletStockinLog(db, refund_date, invoiceID, order_no, customer_name, " ", outlet, invoice.Gdescription, invoice.item_name, invoice.item_descriptions, invoice.quantities, invoice.token_id, invoice.Userlogin, invoice.itemcode, invoice.unit, "")
                
                ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])  

                CreateAdjLog(request, db,refund_date, invoiceID, itemcode[i], quantities[i], initial_invoice)         
                
                if not message_displayed:
                    #update customer invoice
                    customer_invoice.objects.using(db).filter(invoiceID=invoiceID, cusID=customer_id).update(invoiceID = invoiceID + "_returned", invoice_state = "Cancelled", cancellation_status = "1", payment_method = p_method)
                    if accountType == "Customer":
                        cus = customer_table.objects.using(db).get(customer_code=cusID)
                        cus.refund_invoice += 1
                        cus.invoice += 1
                        cus.save()
                    elif accountType == "Vendor":
                        ven = vendor_table.objects.using(db).get(CustID=venID)
                        ven.refundInvoice += 1
                        ven.invoices += 1
                        ven.save()
                    
                    if invoice2.amount_paid < invoice2.amount_expected:
                        if accountType == "Customer":
                            debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Inward")
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                            CreateLog(db, debtor_account, total)
                        elif accountType == "Vendor":
                            debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Outward")
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                            CreateLog(db, debtor_account, total)
                        
                    else:
                        account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                        if accountType == "Customer":
                            CreditReceivable(request, db, cus, invoice2.refund_date, "Edited invoice", p_method, account.account_id, initial_total)
                            DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account.account_id, total)
                        elif accountType == "Vendor":
                            CreditPayable(request, db, ven, invoice2.invoice_date, "Edited invoice", p_method, account.account_id, initial_total)
                            DebitPayable(request, db, ven, refund_date, Gdescription, p_method, account.account_id, total)
                        
                       
                        CreateLog(db, account, total)

                    create_minus_vat(db, invoiceID+ "_returned", vat)    
                    create_add_vat(db, invoiceID, vat)    
                    messages.success(request, "Inward Return successfully")
                    message_displayed = True
                    
                form_instance.save(using=db) 
            else:
                
                return invoice_form
        
def CreateAdjLog(request, db, date, invoiceID, itemcode, new_qty,  initial_invoice):

    initial_qty = 0
     
    for invoice in initial_invoice:
        if invoice.itemcode == itemcode:
            initial_qty = invoice.qty

    StockAdjustmentLog.objects.using(db).create(
        invoice_no  =  invoiceID,                
        initial_qty = initial_qty,
        new_qty = new_qty,
        item_code = itemcode,
        type = "Sales",
        Userlogin = request.user.username
    )



