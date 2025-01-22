from customer.models import customer_table, evidentPayment
from customer.forms import ReceivableForm, PayableForm
from account.models import chart_of_account, account_log
from customer.functions.generalFunction import *
import decimal, uuid
from datetime import date

def verify_payment(request, db):
    payment_id = request.GET.get('payment_id')
    customer_id = request.GET.get('client_id')
    amount = request.GET.get('amount')
    account_id = request.GET.get('account_id')
    description = request.GET.get('description')
    today = date.today()

    try:
        customer = customer_table.objects.using(db).get(customer_code=customer_id)
        account = chart_of_account.objects.using(db).get(account_id=account_id)

        receivable_form = ReceivableForm({"date":today,	"description":description,"amount": amount, "payment_method": "Transfer","type": "Debit", "invoice_status": "Unused"})


        if receivable_form.is_valid():
            account.actual_balance += decimal.Decimal(amount)

            CreditReceivable(request, db, customer, today, description, "Transfer", account.account_id, amount)
            
            
            CreateLog(db, account, amount)
            
            # create account log
            acc_log = account_log(
                transaction_source  = "Receive Payment",
                amount              = amount,
                date                = today,
                account             = account.account_id,
                account_type        = account.account_type,
                Userlogin = request.user.username
            )
            # acc_log.save(using=db)

            payment = evidentPayment.objects.using(db).get(client_ref=customer_id, amount=amount)

            payment.state = "Verified"
            payment.save()


            return True
        
    except customer_table.DoesNotExist:
        return False