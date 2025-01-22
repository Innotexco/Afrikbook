


from customer.models import customer_table, payable, receivable
from customer.forms import ReceivableForm, PayableForm
from account.models import chart_of_account, account_log
from vendor.models import vendor_table
from django.contrib import messages
import decimal, uuid
from customer.functions.generalFunction import *


def receive_payment(request, db):
    date           = request.POST['date']
    invoice_no     = request.POST['invoice_no']
    description    = request.POST['description']
    customer_id    = request.POST.get('customer_id')
    vendor_id      = request.POST.get('vendor_id')
    accountype     = request.POST.get('accountType')
    payment_method = request.POST['payment_method'] 
    account_id     = request.POST['account_id']
    amount         = request.POST['amount']

    
    if accountype == "Customer":
        if customer_id is None:
            messages.error(request, "Select Customer")
        else:
            customer = customer_table.objects.using(db).get(id=customer_id)
            account = chart_of_account.objects.using(db).get(id=account_id)

            receivable_form = ReceivableForm({"date":date,	"description":description,"amount": amount, "payment_method": payment_method,"type": "Debit", "invoice_status": "Unused"})

        
            if receivable_form.is_valid():
                
                CreditReceivable(request, db, customer, date, description, payment_method, account_id, amount)
                
                # transaction_id = uuid.uuid4()

                
                # if receivable.objects.using(db).filter(customer_id=customer.customer_code).exists():
                #     initial_bal = receivable.objects.using(db).filter(customer_id=customer.customer_code).last().balance    
                # else:
                #     initial_bal = 0.00 

                # if initial_bal > 0:
                #         balance = decimal.Decimal(initial_bal) - decimal.Decimal(amount)
                # else:
                #     balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount) 
                                        
                # r_form = receivable_form.save(commit=False)
                # r_form.customer_id = customer.customer_code
                # r_form.customer_name = customer.name
                # r_form.initial_amount = initial_bal
                # balance = balance
                # r_form.balance = balance
                # if balance == 0.00:
                #     transaction_type = "Credit"
                # else:
                #     transaction_type = "Debit"
                # r_form.type = transaction_type

                # r_form.account_posted = account.series_name  # default account
                # r_form.transaction_id = transaction_id
                # r_form.Userlogin = request.user.username
                # r_form.save(using=db)
                
                #update selected account balance
                account.actual_balance += decimal.Decimal(amount)
                account.save()
                
                # create account log
                acc_log = account_log(
                    transaction_source  = "Receive Payment",
                    amount              = amount,
                    date                = date,
                    account             = account.account_id,
                    account_type        = account.account_type,
                    Userlogin = request.user.username
                )
                acc_log.save(using=db)
                messages.success(request, "Payment received successfully ")
            else:
                pass
                
    if accountype == "Vendor":
        if vendor_id is None:
            messages.error(request, "Select vendor")
        else:
            vendor = vendor_table.objects.using(db).get(id=vendor_id)
            account = chart_of_account.objects.using(db).get(id=account_id)
            
            payable_form = PayableForm({"date":date,	"description":description,"type": "Debit",	"amount": amount, "payment_method": payment_method})

        
            if payable_form.is_valid():
                CreditPayable(request, db, vendor, date, description, payment_method, account_id, amount)
                # transaction_id = uuid.uuid4()

                # #get customer last payable balance 
                # if payable.objects.using(db).filter(vendor_id=vendor.custID).exists():
                #     initial_bal = payable.objects.using(db).filter(vendor_id=vendor.custID).last().balance    
                # else:
                #     initial_bal = 0.00 

                # if initial_bal > 0:
                #         balance = decimal.Decimal(initial_bal) - decimal.Decimal(amount)
                # else:
                #     balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount)  

                # p_form = payable_form.save(commit=False)
                # p_form.vendor_id = vendor.custID
                # p_form.vendor_name = vendor.name
                # p_form.initial_amount = initial_bal
                # p_form.balance = balance
                # p_form.account_posted = account.series_name  # default account
                # p_form.transaction_id = transaction_id
                # p_form.Userlogin = request.user.username
                # p_form.save(using=db)
                
                #update selected account balance
                account.actual_balance += decimal.Decimal(amount)
                account.save()

                # create account log
                acc_log = account_log(
                    transaction_source  = "Receive Payment",
                    amount              = amount,
                    date                = date,
                    account             = account.account_id,
                    account_type        = account.account_type,
                    Userlogin = request.user.username
                )
                acc_log.save(using=db)
                messages.success(request, "Payment received successfully ")