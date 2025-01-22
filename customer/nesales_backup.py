from customer.forms import CustomerSalesForm, ReceivableForm, PayableForm
from customer.models import customer_table, customer_invoice, receivable, payable #CreateOutletStockIn, CreateOutletStockInLog, 
from vendor.models import vendor_table, Vendor_invoice
from account.models import *
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog
from django.contrib import messages
import decimal
import uuid
from Stock.models import Item
from customer.utils import generate_order_id
from main.models import User
from customer.functions.generalFunction import *
from django.http import JsonResponse

def invoiceExist(request, invoiceID):
    db = request.user.company_id.db_name
    # check if invoice number exists          
    if customer_invoice.objects.using(db).filter(invoiceID=invoiceID).exists() or Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).exists():
        return JsonResponse(True, safe=False)
    else:
        return JsonResponse(False, safe=False)
    
    
    
    


def add_new_sales(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
    executed = False  
    user = False  
   
    cusID             = request.POST['cusID']
    venID             = request.POST['venID']
    acountType        = request.POST['accountType']
    customer_name     = request.POST['genby']
    invoice_date      = request.POST['invoice_date']
    due_date          = request.POST['due_date']
    invoiceID         = request.POST['invoiceID']
    order_id          = request.POST['order_id']
    Gdescription      = request.POST['Gdescription']
    invoice_state     = request.POST.get('invoice_state')
    credit_sales      = request.POST.get('credit_sales')
    item_name         = request.POST.getlist('item_name')
    purchaseP         = request.POST.getlist('purchaseP')
    itemcode          = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities        = request.POST.getlist('qty[]')
    unit              = request.POST.getlist('unit[]')
    discount          = request.POST.getlist('discount[]')
    amount            = request.POST.getlist('amount[]')
    vat               = request.POST['vat'][:-1]
    sub_total         = request.POST['sub-total']
    total             = request.POST['total']

    instant_stockout = request.session.get('IN_STOCKOUT', 'Yes')
    
    
    if instant_stockout == "Yes":
        status = 1
    else:
        status = 0

    if invoice_state:
        invoice_state = "Pending"
    else:
        invoice_state = "Supplied"
    
    # Note if any changes in this statement you have to make same chabges on return inward function
    if credit_sales:
        amount_paid = 0.00
        amount_expected = total
    else:
        amount_paid = total
        amount_expected = 0.00

    # amount_paid = total
    # amount_expected = sub_total
    

    
    
    int_purchaseP = [int(num) if num.isdigit() else 0 for num in purchaseP ]

    total_purchaseP = sum(int_purchaseP)
    # Generate a new transaction ID
    transaction_id = uuid.uuid4()
    
    # Generate refrence number
    ref_no = "REF"+generate_order_id()
    customer_code = None
    if acountType == "Customer":
        if cusID:
            customer_code = customer_table.objects.using(db).get(id=cusID).customer_code
                
    elif acountType == "Vendor":
        if venID:
           customer_code = vendor_table.objects.using(db).get(id=venID).custID
            

  
    for i in range(len(itemcode)):
            # Check if the itemcode (value) is equal to 0
        if i < len(itemcode) and str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            form_data = {
                'cusID': customer_code,
                'customer_name':customer_name,
                'invoice_date':invoice_date,
                'due_date': due_date,
                'invoiceID':invoiceID ,
                'order_ID':order_id ,
                'Gdescription': Gdescription,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_description': item_descriptions[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'amount_paid': amount_paid,
                'amount_expected': amount_expected,

                "cancellation_status":0,
                "status":status,
                "Transfer":0,
                "POS":0,
                "Cash":0,
                "Customer_account":0,
                "Cheque":0,
                "invoice_state":invoice_state,
                "purchaseP":purchaseP[i],
                "total_purchaseP":total_purchaseP
            }
            cus_form = CustomerSalesForm(form_data)

            
                
            if credit_sales == None:
                if acountType == "Customer": 
                    receivable_form = ReceivableForm({"date":invoice_date,	"description":Gdescription,"type": "Debit",	"amount": amount_paid, "payment_method": "Transfer","account_posted":"","invoice_status": "Unused"})

                    if not executed:
                        # check if customer is selected
                        if not user:
                            if not cusID or int(cusID) < 1:
                                messages.error(request, "Select Customer")
                                user = True
                                executed = False
                                
                        # fetch selected customer
                        # check if customer balance is sufficient
                        # if total > cus.Balance:
                        #     if not message_displayed:
                        #         messages.error(request, "Insufficient fund")
                        #         message_displayed = True
                        executed = True
                    if executed:
                        if cus_form.is_valid() and receivable_form.is_valid():
                            cus = customer_table.objects.using(db).get(id=cusID)
                            form  = cus_form.save(commit=False)
                            form.Userlogin = request.user.username
                            form.save(using=db)
        
                            #Reduce stock quantity
                            if invoice_state == "Supplied":
                                outlet= request.user.outlet
                                ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])

                            if not message_displayed:
                                if invoice_state == "Supplied":
                                    # cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                    cus.invoice = cus.invoice + 1
                                    # cus.save()
                                    message_displayed = True  # Update the message_displayed variable
                                else:
                                    cus.invoice = cus.invoice + 1
                                    # cus.save()
                                    message_displayed = True  # Update the message_displayed variable
                                    
                                # insert into recievable
                                p_method="Transfer"
                                # DebitReceivable(request, db, cus, invoice_date, Gdescription, p_method, total)
                                
                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = invoice_date,
                                    account             = "",
                                    account_type        = "",
                                    Userlogin = request.user.username
                                )
                                # acc_log.save(using=db)
                                messages.success(request, "New Sales Invoice was added successfully")
                        else:
                            pass
                            # print("Customer form error", cus_form.errors)
                            # print("Receivable form error", receivable_form.errors)
                            return cus_form
                if acountType == "Vendor":
                    payable_form = PayableForm({"date":invoice_date,	"description":Gdescription,"type": "Credit",	"amount": amount_paid, "payment_method": "Transfer","account_posted":"","invoice_status": "Unused"})
                    if not executed:
                        # check if customer is selected
                        if not venID or int(venID) < 1:
                            if not message_displayed:
                                messages.error(request, "Select Vendor")
                                message_displayed = True
                                executed = False
                        # fetch selected vendor
                        ven = vendor_table.objects.using(db).get(id=venID)
                        
                        executed = True
                    if executed:
                        if cus_form.is_valid() and payable_form.is_valid():
                            form  =cus_form.save(commit=False)
                            form.Userlogin = request.user.username
                            form.save(using=db)

                                #Reduce stock quantity
                            if invoice_state == "Supplied":
                                outlet= request.user.outlet
                                ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])

                            if not message_displayed:
                                if invoice_state == "Supplied":
                                    # make changes in the Vendor invoice
                                    ven.invoices = cus.invoice + 1
                                    ven.save()                       
                                    message_displayed = True  # Update the message_displayed variable
                                else:
                                    ven.invoices = ven.invoices + 1
                                    ven.save()
                                    message_displayed = True  # Update the message_displayed variable
                                # insert into payable
                                p_method="Transfer"
                                DebitPayable(request, db, ven, invoice_date, Gdescription, p_method, total) 
                                
                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = invoice_date,
                                    account             = "",
                                    account_type        = "",
                                    Userlogin = request.user.username
                                )
                                acc_log.save(using=db)
                                messages.success(request, "New Sales Invoice was added successfully")
                                message_displayed = True  # Update the message_displayed variable
                        else:
                            pass
                            # print("Customer form error", cus_form.errors)
                            # print("Receivable form error", receivable_form.errors)
                # messages.success(request, 'Credit Sales')
            else:
                credit_account = chart_of_account.objects.using(db).filter(series_name="Debtor account")
                if credit_account.exists():
                    debtor_account = chart_of_account.objects.using(db).get(series_name="Debtor account")
                    if acountType == "Customer": 
                        if not executed:
                            # check if customer is selected
                            if not cusID or int(cusID) < 1:
                                if not message_displayed:
                                    messages.error(request, "Select Customer")
                                    message_displayed = True
                                    executed = False
                            # fetch selected customer
                            cus = customer_table.objects.using(db).get(id=cusID)
                            # check if customer balance is sufficient
                            # if total > cus.Balance:
                            #     if not message_displayed:
                            #         messages.error(request, "Insufficient fund")
                            #         message_displayed = True
                            executed = True
                        if executed:
                            if cus_form.is_valid():
                                form  = cus_form.save(commit=False)
                                form.Userlogin = request.user.username
                                form.save(using=db)
            
                                #Reduce stock quantity
                                if invoice_state == "Supplied":
                                    outlet= request.user.outlet
                                    ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])

                                if not message_displayed:
                                        # make changes in the default account
                                        debtor_account.actual_balance += decimal.Decimal(total)
                                        debtor_account.save()

                                        if invoice_state == "Supplied":
                                            # make changes in the customer balance and invoice
                                            # cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                            cus.invoice = cus.invoice + 1
                                            cus.save()

                                            # messages.success(request, "Invoice supplied")
                                            message_displayed = True  # Update the message_displayed variable
                                        else:
                                            cus.invoice = cus.invoice + 1
                                            cus.save()
                                            # messages.success(request, "Invoice Pending")
                                            message_displayed = True  # Update the message_displayed variable
                                        #create account log
                                        acc_log = account_log(
                                            transaction_source  = "Sales",
                                            amount              = total,
                                            date                = invoice_date,
                                            account             = debtor_account.account_id,
                                            account_type        = debtor_account.account_type,
                                            Userlogin = request.user.username
                                        )
                                        acc_log.save(using=db)
                                        messages.success(request, "New Sales Invoice was added successfully")
                                        message_displayed = True  # Update the message_displayed variable
                            else:
                                pass
                                # print("Customer form error", cus_form.errors)

                    if acountType == "Vendor":
                        if not executed:
                            # check if invoice number exists
                            if Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).exists():
                                if not message_displayed:
                                    messages.error(request, "Invoice Number already exist")
                                    message_displayed = True
                            # check if customer is selected
                            if not venID or int(venID) < 1:
                                if not message_displayed:
                                    messages.error(request, "Select Vendor")
                                    message_displayed = True
                            # fetch selected vendor
                            ven = vendor_table.objects.using(db).get(id=venID)
                            
                            executed = True
                        if executed:
                            if cus_form.is_valid():
                                form  =cus_form.save(commit=False)
                                form.Userlogin = request.user.username
                                form.save(using=db)

                                    #Reduce stock quantity
                                if invoice_state == "Supplied":
                                    outlet= request.user.outlet
                                    ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])

                                if not message_displayed:
                                        # make changes in the default account
                                        debtor_account.actual_balance += decimal.Decimal(total)
                                        debtor_account.save()

                                        if invoice_state == "Supplied":
                                            # make changes in the Vendor invoice
                                            # cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                            ven.invoices = int(ven.invoices) + 1
                                            ven.save()
                                            message_displayed = True  # Update the message_displayed variable
                                        else:
                                            ven.invoices = int(ven.invoices) + 1
                                            ven.save()
                                            message_displayed = True  # Update the message_displayed variable
                                        #create account log
                                        acc_log = account_log(
                                            transaction_source  = "Sales",
                                            amount              = total,
                                            date                = invoice_date,
                                            account             = debtor_account.account_id,
                                            account_type        = debtor_account.account_type,
                                            Userlogin = request.user.username
                                        )
                                        acc_log.save(using=db)
                                        messages.success(request, "New Sales Invoice was added successfully")
                                        message_displayed = True  # Update the message_displayed variable
                            else:
                                pass
                                # print("Vendor form error", cus_form.errors)
                else:
                    if not message_displayed:
                        messages.error(request, "Create account for credit sales")
                        message_displayed = True




def ReduceOutletStockinItemQuantity(db, outlet, itemcode, qty):
    stock = CreateOutletStockIn.objects.using(db).filter(outlet=outlet, item_code=itemcode).first()
    new_qty = decimal.Decimal(stock.quantity) -  decimal.Decimal(qty)
    stock.quantity = new_qty
    # stock.save()

    # StockinStatus(db, itemcode, qty)
    # CreatOutletStockinLog(stock, new_qty)


def CreatOutletStockinLog(stock, new_qty):
    # Generate refrence number
    ref_no = "REF"+generate_order_id()

    CreateOutletStockInLog.objects.create(
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
    

def StockinStatus(db, outlet, itemcode, qty):
    items = CreateOutletStockInLog.objects.using(db).filter(item_code=itemcode).order_by('id').exclude(status="Sold")[:qty]

    items.update(status="Sold")


