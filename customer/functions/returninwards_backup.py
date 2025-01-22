from customer.forms import CustomerSalesForm, ReceivableForm, PayableForm
from django.contrib import messages
from django.http import HttpResponse
from customer.models import *                                                                                         
import uuid, decimal
from vendor.models import vendor_table
from account.models import *
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog
from customer.functions.newsales import ReduceOutletStockinItemQuantity
from django.db.models import Q



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
    purchaseP         = request.POST.getlist('purchaseP')

    total = request.POST['total']
    initial_total = request.POST['initial_total']
   
    # print(purchaseP)
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

    # due_date = initial_invoice.first().due_date
    # for i in invoice2:
    #     print(i.due_date, "invoice2.due_dateinvoice2.due_dateinvoice2.due_dateinvoice2.due_date")

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    # Generate refrence number
    ref_no = "REF"+generate_order_id()
      
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
           
          
            if not executed:
                lookup = Q(amount_paid__iexact=total) | Q(amount_expected__iexact=total)

                invoices = customer_invoice.objects.using(db).filter(lookup, invoiceID=invoiceID, cusID=customer_id)
                if invoices:
                    for invoice in invoices:
                            # Perform the required updates or actions on each invoice
                            invoice.invoiceID = invoiceID + "_returned"
                            invoice.invoice_state = "Cancelled"
                            invoice.cancellation_status = "1"
                            invoice.payment_method = p_method
                            invoice.save()

                            # Increase outlet stockin quantity
                            stock = CreateOutletStockIn.objects.using(db).filter(outlet=request.user.outlet, item_code=itemcode[i]).first()
                            new_qty = decimal.Decimal(stock.quantity) +  decimal.Decimal(quantities[i])
                            stock.quantity = new_qty
                            stock.save()
                        
                        #    Create new CreateOutletStockIn Log
                            stockout_log = CreateOutletStockInLog(
                                            datetx = stock.datetx,
                                            invoice_no = stock.invoice_no,	
                                            order_no = stock.order_no,	
                                            supplier = stock.supplier,
                                            warehouse = stock.warehouse,
                                            outlet = stock.outlet,	
                                            description = stock.description,	
                                            item = stock.item,	
                                            item_decription =stock.item_decription,
                                            quantity = new_qty,
                                            token_id = stock.token_id,	
                                            Userlogin = stock.Userlogin,	
                                            item_code = stock.item_code,	
                                            ref_no = ref_no,	
                                            selling_price = stock.selling_price,
                                            wholesale_price = stock.wholesale_price,
                                        )
                            # stockout_log.save()
                            if not message_displayed:
                                if accountType == "Customer":
                                    cus = customer_table.objects.using(db).get(customer_code=cusID)
                                    cus.refund_invoice += 1
                                    cus.save()

                                    if invoice2.amount_paid > invoice2.amount_expected:
                                        debtor_account = chart_of_account.objects.using(db).get(series_name="Debtor account")
                                        debtor_account.actual_balance -= decimal.Decimal(total)
                                        debtor_account.save()

                                        #create account log
                                        acc_log = account_log(
                                            transaction_source  = "Sales",
                                            amount              = total,
                                            date                = refund_date,
                                            account             = debtor_account.account_id,
                                            account_type        = debtor_account.account_type,
                                            Userlogin           = request.user.username
                                        )
                                        acc_log.save(using=db)
                                    else:
                                        # insert into receivable
                                        if receivable.objects.using(db).filter(customer_id=cusID).exists():
                                            initial_bal = receivable.objects.using(db).filter(customer_id=cusID).last().balance
                                        else: 
                                            initial_bal = decimal.Decimal(0.00)
                                        
                                        if initial_bal > 0:
                                            balance = decimal.Decimal(initial_bal) - decimal.Decimal(total)
                                        else:
                                            balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

                                        create_receivable = receivable(
                                            date=refund_date,
                                            description= Gdescription,
                                            type = "Credit",
                                            amount = total, 
                                            payment_method ="Transfer",
                                            invoice_status ="Unused",
                                            customer_id = cus.customer_code,
                                            customer_name = cus.name,
                                            initial_amount = initial_bal,
                                            balance = balance,
                                            account_posted = "default account", # default account
                                            transaction_id = transaction_id,
                                            Userlogin = request.user.username)
                                        create_receivable.save(using=db)

                                        #create account log
                                        acc_log = account_log(
                                            transaction_source  = "Sales",
                                            amount              = total,
                                            date                = refund_date,
                                            account             = "",
                                            account_type        = "",
                                            Userlogin           = request.user.username
                                        )
                                        acc_log.save(using=db)
                                if accountType == "Vendor":
                                    ven = vendor_table.objects.using(db).get(custID=venID)
                                    ven.refundInvoice = int(ven.refundInvoice) + 1
                                    ven.save()

                                    if invoice2.amount_paid > invoice2.amount_expected:
                                        debtor_account = chart_of_account.objects.using(db).get(series_name="Debtor account")
                                        debtor_account.actual_balance -= decimal.Decimal(total)
                                        debtor_account.save()

                                        #create account log
                                        acc_log = account_log(
                                            transaction_source  = "Sales",
                                            amount              = total,
                                            date                = refund_date,
                                            account             = debtor_account.account_id,
                                            account_type        = debtor_account.account_type,
                                            Userlogin           = request.user.username
                                        )
                                        acc_log.save(using=db)
                                    else:
                                        if payable.objects.using(db).filter(vendor_id=cusID).exists():
                                            initial_bal = payable.objects.using(db).filter(vendor_id=cusID).last().balance
                                        else: 
                                            initial_bal = decimal.Decimal(0.00)

                                        if initial_bal > 0:
                                            balance = decimal.Decimal(initial_bal) - decimal.Decimal(amount)
                                        else:
                                            balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount)

                                        # insert into payable
                                        create_payable = payable(
                                            date=refund_date,
                                            description= Gdescription,
                                            type = "Credit",
                                            amount = total, 
                                            payment_method =p_method,
                                            vendor_id = ven.custID,
                                            vendor_name = ven.name,
                                            initial_amount = initial_bal,
                                            balance = balance,
                                            account_posted = "",
                                            transaction_id = transaction_id,
                                            Userlogin = request.user.username)
                                        create_payable.save(using=db)

                                        #create account log
                                        acc_log = account_log(
                                            transaction_source  = "Sales",
                                            amount              = total,
                                            date                = refund_date,
                                            account             = "",
                                            account_type        = "",
                                            Userlogin           = request.user.username
                                        )
                                        acc_log.save(using=db)
                                # messages.success(request, "Exist with no changes")
                                messages.success(request, "Return Inward was successfully")
                                message_displayed = True  # Update the message_displayed variable
                    executed = False
                else:            
                    executed = True
                   
            if executed:
                if accountType == "Customer":  
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
                        form_instance.save(using=db) 
                    
                        for invoice in initial_invoice:
                            # Perform the required updates or actions on each invoice
                            invoice.invoice_state = "Cancelled"
                            invoice.cancellation_status = "1"
                            invoice.invoiceID = invoiceID + "_returned"
                            invoice.save()

                            outlet= request.user.outlet
                            # Increase outlet stockin returned quatity
                            IncreaseOutletStockinItemQuantity(db, outlet, invoice.item_code, invoice.quantity)

                            # Reduce outlet stockin quatity
                            ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])
                            
                           
                        
                        if not message_displayed:
                            cus = customer_table.objects.using(db).get(customer_code=cusID)
                            cus.refund_invoice += 1
                            cus.invoice += 1
                            cus.save()
                            
                            if invoice2.amount_paid > invoice2.amount_expected:
                                debtor_account = chart_of_account.objects.using(db).get(series_name="Debtor account")
                                debtor_account.actual_balance -= decimal.Decimal(initial_total)
                                debtor_account.actual_balance += decimal.Decimal(total)
                                debtor_account.save()

                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = refund_date,
                                    account             = debtor_account.account_id,
                                    account_type        = debtor_account.account_type,
                                    Userlogin           = request.user.username
                                )
                                acc_log.save(using=db)
                            else:
                                # Credit Sales
                                #get customer last recievable balance 
                                if receivable.objects.using(db).filter(customer_id=cusID).exists():
                                    initial_bal = receivable.objects.using(db).filter(customer_id=cusID).last().balance
                                else: 
                                    initial_bal = 0.00

                                # insert into recievable
                                r_form = receivable_form.save(commit=False)
                                r_form.customer_id = cus.customer_code
                                r_form.customer_name = cus.name
                                r_form.initial_amount = initial_bal
                                r_form.balance = initial_bal + decimal.Decimal(total)
                                r_form.account_posted = "" # default account
                                r_form.transaction_id = transaction_id
                                r_form.Userlogin = request.user.username
                                r_form.save(using=db)

                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = refund_date,
                                    account             = "",
                                    account_type        = "",
                                    Userlogin           = request.user.username
                                )
                                acc_log.save(using=db)
                            # messages.success(request, "Exist with changes")
                            messages.success(request, "New Invoice was created successfully")
                            message_displayed = True
                    else:
                        pass
                        # print(invoice_form.errors)
                if accountType == "Vendor":  
                    payable_form = PayableForm({"date":refund_date,	"description":Gdescription,"type": "Debit",	"amount": total, "payment_method": p_method,"invoice_status": "Unused"})
                    if invoice_form.is_valid() and payable_form.is_valid():
                    
                        for invoice in initial_invoice:
                            # Perform the required updates or actions on each invoice
                            invoice.invoice_state = "Cancelled"
                            invoice.cancellation_status = "1"
                            invoice.invoiceID = invoiceID + "_returned"
                            invoice.save()

                            outlet= request.user.outlet
                            # Increase outlet stockin returned quatity
                            IncreaseOutletStockinItemQuantity(db, outlet, invoice.item_code, invoice.quantity)

                            # Reduce outlet stockin new quatity
                            ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])
                            
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
                        form_instance.save(using=db)    
                        
                        if not message_displayed:
                            ven = vendor_table.objects.using(db).get(CustID=venID)
                            ven.refundInvoice += 1
                            ven.invoice += 1
                            ven.save()

                            if invoice2.amount_paid > invoice2.amount_expected:
                                debtor_account = chart_of_account.objects.using(db).get(series_name="Debtor account")
                                debtor_account.actual_balance += decimal.Decimal(total)
                                debtor_account.save()

                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = refund_date,
                                    account             = debtor_account.account_id,
                                    account_type        = debtor_account.account_type,
                                    Userlogin           = request.user.username
                                )
                                acc_log.save(using=db)
                            else:

                                # insert into recievable
                                if payable.objects.using(db).filter(vendor_id=cusID).exists():
                                        initial_bal = payable.objects.using(db).filter(vendor_id=cusID).last().balance
                                else: 
                                    initial_bal = 0.00

                                # insert into payable
                                p_form = payable_form.save(commit=False)
                                p_form.vendor_id = ven.custID
                                p_form.vendor_name = ven.name
                                p_form.initial_amount = initial_bal
                                p_form.balance = initial_bal + decimal.Decimal(total)
                                p_form.account_posted = "" 
                                p_form.transaction_id = transaction_id
                                p_form.Userlogin  = request.user.username
                                p_form.save(using=db)

                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = refund_date,
                                    account             = "",
                                    account_type        = "",
                                    Userlogin           = request.user.username
                                )
                                acc_log.save(using=db)
                            # messages.success(request, "Exist with changes")
                            messages.success(request, "New Invoice was created successfully")
                            message_displayed = True
                    else:
                        pass
                        # print(invoice_form.errors)
           
            
           


def IncreaseOutletStockinItemQuantity(db, outlet, itemcode, qty):
    stock = CreateOutletStockIn.objects.using(db).filter(outlet=outlet, item_code=itemcode).first()
    new_qty = decimal.Decimal(stock.quantity) +  decimal.Decimal(qty)
    stock.quantity = new_qty
    stock.save()



