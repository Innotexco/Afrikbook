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
    account_id     = request.POST.get('account_id')
    amount         = request.POST['amount']


    receivable_form = ReceivableForm({"date":date,	"description":description,"amount": amount, "payment_method": payment_method,"type": "Debit", "invoice_status": "Unused"})

   
    conditions = required_fields(request, invoice_no, customer_id, vendor_id, account_id)
    
    if conditions:

        if receivable_form.is_valid():
            if accountype == "Customer":
                customer = customer_table.objects.using(db).get(id=customer_id)
                CreditReceivable(request, db, customer, date, description, payment_method, account_id, amount)
            elif accountype == "Vendor":
                vendor = vendor_table.objects.using(db).get(id=vendor_id)
                CreditPayable(request, db, vendor, date, description, payment_method, account_id, amount)
        
            
            #update selected account balance
            account = chart_of_account.objects.using(db).get(id=account_id)
            account.actual_balance += decimal.Decimal(amount)
            # account.save()
            CreateLog(db, account, amount)
            
            # create account log
            acc_log = account_log(
                transaction_source  = "Receive Payment",
                amount              = amount,
                date                = date,
                account             = account.account_id,
                account_type        = account.account_type,
                Userlogin = request.user.username
            )
            # acc_log.save(using=db)
            messages.success(request, "Payment received successfully")
        else:
           
            return receivable_form
    else:
        messages.error(request, "All the feilds must be filled in to submit")
        
        
        


def required_fields(request,invoice_no, customer_id, vendor_id, account_id):
    conditions = False
    if invoice_no:
        conditions = True
    else:
        conditions = False
        # messages.error(request, "Invoice number cannot be empty")
    if customer_id or vendor_id:
        conditions = True
    else:
        conditions= False
        # messages.error(request, "Select Customer or Vendor")
    if account_id:
        conditions = True
    else:
        conditions= False
        # messages.error(request, "Select Valid account")
    return conditions
    
    