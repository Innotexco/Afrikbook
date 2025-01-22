from account.forms import AccountTransfer, account_log_view, InsertDataForm
from account.models import account_log, transfer_account
from django.contrib import messages
from django.db import transaction
import decimal
import uuid

def new_inter_account_transfer(data):
    shared_data = {
        'amount': data['amount'],  
        'token_id': data['token_id'],  
    }

    # Create and save the instance for Table1
    transfer_account_instance = transfer_account(**shared_data)
    transfer_account_instance.save()

    # Create and save the instance for Table2
    account_log_instance = account_log(**shared_data)
    account_log_instance.save()

    if request.method == 'POST':
        form = InsertDataForm(request.POST)
        if form.is_valid():
            date_tx = form.cleaned_data['date_tx']
            description = form.cleaned_data['description']
            paid_from = form.cleaned_data['paid_from']
            amount = form.cleaned_data['amount']
            received_in = form.cleaned_data['received_in']
            token_id = form.cleaned_data['token_id']
            user = form.cleaned_data['user']
            status = form.cleaned_data['status']
            # Retrieve other form data as needed

            # Insert data into Table1
            transfer_account_instance = transfer_account(date_tx=date_tx, description=description, paid_from=paid_from, amount=amount, received_in=received_in, token_id=token_id, user=user, status=status)
            transfer_account_instance.save()

            # Insert data into Table2
            account_log_instance = account_log(transactionId=transactionId, transaction_source="INTER ACCOUNT TRANSFER", amount=amount, date=date_tx, timestamp=timestamp, token_id=token_id, account=account, account_type=account_type, dateTimeSt=date_tx, cancellation_status=cancellation_status, Userlogin="Admin")
            account_log_instance.save()

          
            return render(request, 'account/InterAccountTransfer.html')  # Redirect to a success page
    else:
        form = InsertDataForm()







def new_inter(request):
    if request.method == 'POST':
        transactionId = request.POST.get('TRS_.transactionId')
        transaction_source = request.POST.get('transaction_source')
        amount = request.POST.get("amount")
        date = request.POST.get("date")
        timestamp = request.POST.get("timestamp")
        token_id = request.POST.get("token_id")
        account = request.POST.get("account")
        account_type = request.POST.get("account_type")
        dateTimeSt = request.POST.get("dateTimeSt")
        cancellation_status = request.POST.get("cancellation_status")
        Userlogin = request.POST.get("Userlogin")
        
        date_tx = request.POST.get('date_tx')
        description = request.POST.get('description')
        paid_from = request.POST.get('paid_from')
        amount = request.POST.get('amount')
        received_in = request.POST.get('received_in')
        token_id = request.POST.get('token_id')
        user = request.POST.get('user')
        status = request.POST.get('status')

        with transaction.atomic():
            transfer_account_instance = transfer_account(date_tx=date_tx, description=description, paid_from=paid_from, amount=amount, received_in=received_in, token_id=token_id, user=user, status=status)
            transfer_account_instance.save()

            account_log_instance = account_log(transactionId=transactionId, transaction_source=transaction_source, amount=amount, date=date, timestamp=timestamp, token_id=token_id, account=account, account_type=account_type, dateTimeSt=dateTimeSt, cancellation_status=cancellation_status, Userlogin=Userlogin)
            account_log_instance.save()

























def add_new_sales(request):
    
    message_displayed = False  # Initialize the message_displayed variable
    executed = False  
   
    cusID = request.POST['cusID']
    venID = request.POST['venID']
    acountType = request.POST['accountType']
    customer_name = request.POST['genby']
    invoice_date = request.POST['invoice_date']
    due_date = request.POST['due_date']
    invoiceID = request.POST['invoiceID']
    order_id = request.POST['order_id']
    Gdescription = request.POST['Gdescription']
    invoice_state = request.POST.get('invoice_state')
    credit_sales = request.POST.get('credit_sales')
    item_name = request.POST.getlist('item_name')
    purchaseP = request.POST.getlist('purchaseP')
    itemcode = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities = request.POST.getlist('qty[]')
    unit = request.POST.getlist('unit[]')
    discount = request.POST.getlist('discount[]')
    amount = request.POST.getlist('amount[]')
    vat = request.POST['vat'][:-1]
    total = float(request.POST['total'])
    
    if invoice_state:
        invoice_state = "Pending"
    else:
        invoice_state = "Suplied"
    
    if vat:
        amount_paid = (total - float(vat)) / 100
        amount_expected = total
    else:
        amount_paid = total
        amount_expected = total
    
    
    int_purchaseP = [int(num) if num.isdigit() else 0 for num in purchaseP ]

    total_purchaseP = sum(int_purchaseP)
  
    for i in range(len(item_descriptions)):

            # Check if the itemcode (value) is equal to 0
        if i < len(itemcode) and str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            form_data = {
                'cusID': cusID,
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
                "status":1,
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
            
            if credit_sales:
                receivable_form = ReceivableForm({"date":invoice_date,	"description":Gdescription,"type": "Debite",	"amount": amount_paid, "payment_method": "Transfer","account_posted":"","invoice_status": "Unused"})
                
                if acountType == "Customer": 
                    if not executed:
                        # check if invoice number exists
                        if customer_invoice.objects.filter(invoiceID=invoiceID).exists():
                            if not message_displayed:
                                messages.error(request, "Invoice Number already exist")
                                message_displayed = True
                        # check if customer is selected
                        if not cusID or int(cusID) < 1:
                            if not message_displayed:
                                messages.error(request, "Select Customer")
                                message_displayed = True
                        # fetch selected customer
                        cus = customer_table.objects.get(id=cusID)
                        # check if customer balance is sufficient
                        if total > cus.Balance:
                            if not message_displayed:
                                messages.error(request, "Insufficient fund")
                                message_displayed = True
                        executed = True
                    if executed:
                        if cus_form.is_valid() and receivable_form.is_valid():
                           cus_form.save()
                           if not message_displayed:
                                if invoice_state == "Suplied":
                                    # make changes in the customer balance and invoice
                                    cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                    cus.invoice = cus.invoice + 1
                                    cus.save()

                                    # make changes in the default account

                                    # insert into recievable
                                    # Generate a new transaction ID
                                    transaction_id = uuid.uuid4()
                                    
                                    r_form = receivable_form.save(commit=False)
                                    r_form.customer_id = cus.customer_code
                                    r_form.customer_name = cus.name
                                    r_form.initial_amount = cus.Balance
                                    r_form.balance = cus.Balance - decimal.Decimal(amount_paid)
                                    r_form.account_posted = "default account" # default account
                                    r_form.transaction_id = transaction_id
                                    r_form.save()
                                    messages.success(request, "Invoice supplied")
                                    message_displayed = True  # Update the message_displayed variable
                                else:
                                    cus.invoice = cus.invoice + 1
                                    # cus.save()
                                    messages.success(request, "Invoice Pending")
                                    message_displayed = True  # Update the message_displayed variable

                                messages.success(request, "New Sales Invoice was added successfully")
                                message_displayed = True  # Update the message_displayed variable
                        else:
                            pass
                            # print("Customer form error", cus_form.errors)
                            # print("Receivable form error", receivable_form.errors)
                if acountType == "Vendor":
                    if not executed:
                        # check if invoice number exists
                        if customer_invoice.objects.filter(invoiceID=invoiceID).exists():
                            if not message_displayed:
                                messages.error(request, "Invoice Number already exist")
                                message_displayed = True
                        # check if customer is selected
                        if not cusID or int(cusID) < 1:
                            if not message_displayed:
                                messages.error(request, "Select Customer")
                                message_displayed = True
                        # fetch selected customer
                        cus = customer_table.objects.get(id=cusID)
                        # check if customer balance is sufficient
                        if total > cus.Balance:
                            if not message_displayed:
                                messages.error(request, "Insufficient fund")
                                message_displayed = True
                        executed = True
                    if executed:
                        if cus_form.is_valid() and receivable_form.is_valid():
                           cus_form.save()
                           if not message_displayed:
                                if invoice_state == "Suplied":
                                    # make changes in the customer balance and invoice
                                    cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                    cus.invoice = cus.invoice + 1
                                    cus.save()

                                    # make changes in the default account

                                    # insert into recievable
                                    # Generate a new transaction ID
                                    transaction_id = uuid.uuid4()
                                    
                                    r_form = receivable_form.save(commit=False)
                                    r_form.customer_id = cus.customer_code
                                    r_form.customer_name = cus.name
                                    r_form.initial_amount = cus.Balance
                                    r_form.balance = cus.Balance - decimal.Decimal(amount_paid)
                                    r_form.account_posted = "default account" # default account
                                    r_form.transaction_id = transaction_id
                                    r_form.save()
                                    messages.success(request, "Invoice supplied")
                                    message_displayed = True  # Update the message_displayed variable
                                else:
                                    cus.invoice = cus.invoice + 1
                                    # cus.save()
                                    messages.success(request, "Invoice Pending")
                                    message_displayed = True  # Update the message_displayed variable

                                messages.success(request, "New Sales Invoice was added successfully")
                                message_displayed = True  # Update the message_displayed variable
                        else:
                            pass
                            # print("Customer form error", cus_form.errors)
                            # print("Receivable form error", receivable_form.errors)
                # messages.success(request, 'Credit Sales')
            else:
                if acountType == "Customer":
                    if not cusID or int(cusID) < 1:
                        if not message_displayed:
                            messages.error(request, "Select Customer")
                            message_displayed = True
                    else:
                        cus = customer_table.objects.get(id=cusID)
                        if total > cus.Balance:
                            if not message_displayed:
                                messages.error(request, "Insufficient fund")
                                message_displayed = True
                        else:
                            if cus_form.is_valid():
                                cus_form.save()
                                
                                if not message_displayed:
                                    if invoice_state == "Suplied":
                                        # cus = cus.save(commit=False)
                                        cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                        cus.invoice = cus.invoice + 1
                                        cus.save()
                                        messages.success(request, "Invoice supplied")
                                        message_displayed = True  # Update the message_displayed variable
                                    else:
                                        cus.invoice = cus.invoice + 1
                                        cus.save()
                                        messages.success(request, "Invoice Pending")
                                        message_displayed = True  # Update the message_displayed variable

                                    messages.success(request, "New Sales Invoice was added successfully")
                                    message_displayed = True  # Update the message_displayed variable
                            else:
                                pass
                                # print("Customer form error", cus_form.errors)
                if acountType == "Vendor":
                    if not venID or int(cusID) < 1:
                        if not message_displayed:
                            messages.error(request, "Select Vendor")
                            message_displayed = True
                    else:
                        cus = customer_table.objects.get(id=venID)
                        if total > cus.Balance:
                            if not message_displayed:
                                messages.error(request, "Insufficient fund")
                                message_displayed = True
                        else:
                            if cus_form.is_valid():
                                cus_form.save(commit=False)
                                
                                if not message_displayed:
                                    if invoice_state == "Suplied":
                                        # cus = cus.save(commit=False)
                                        cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                        cus.invoice = cus.invoice + 1
                                        cus.save()
                                        messages.success(request, "Invoice supplied")
                                        message_displayed = True  # Update the message_displayed variable
                                    else:
                                        cus.invoice = cus.invoice + 1
                                        cus.save()
                                        messages.success(request, "Invoice Pending")
                                        message_displayed = True  # Update the message_displayed variable
                                    messages.success(request, "New Sales Invoice was added successfully")
                                    message_displayed = True  # Update the message_displayed variable
                            else:
                                pass
                                # print("Vendor form error", cus_form.errors)