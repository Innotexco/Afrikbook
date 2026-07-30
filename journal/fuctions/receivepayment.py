from customer.models import customer_table, payable, receivable
from customer.forms import ReceivableForm, PayableForm
from account.models import chart_of_account, account_log
from vendor.models import vendor_table
from django.contrib import messages
import decimal, uuid
from customer.functions.generalFunction import *
from django.conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)


def amount_to_words(amount):
    try:
        amount = float(amount)
        naira  = int(amount)
        kobo   = round((amount - naira) * 100)

        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
                'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen',
                'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
                'Sixty', 'Seventy', 'Eighty', 'Ninety']

        def words(n):
            if n == 0:   return ''
            if n < 20:   return ones[n]
            if n < 100:  return tens[n // 10] + ((' ' + ones[n % 10]) if n % 10 else '')
            if n < 1000:
                remainder = n % 100
                return ones[n // 100] + ' Hundred' + ((' and ' + words(remainder)) if remainder else '')
            if n < 1_000_000:
                remainder = n % 1000
                return words(n // 1000) + ' Thousand' + ((' ' + words(remainder)) if remainder else '')
            if n < 1_000_000_000:
                remainder = n % 1_000_000
                return words(n // 1_000_000) + ' Million' + ((' ' + words(remainder)) if remainder else '')
            remainder = n % 1_000_000_000
            return words(n // 1_000_000_000) + ' Billion' + ((' ' + words(remainder)) if remainder else '')

        result = (words(naira) or 'Zero') + ' Naira'
        if kobo:
            result += f' and {words(kobo)} Kobo'
        return result + ' Only'

    except Exception:
        return ''


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

    receivable_form = ReceivableForm({
        "date":           date,
        "description":    description,
        "amount":         amount,
        "payment_method": payment_method,
        "type":           "Debit",
        "invoice_status": "Unused"
    })

    conditions = required_fields(request, invoice_no, customer_id, vendor_id, account_id)

    if conditions:
        if receivable_form.is_valid():

            # ── Resolve account object ────────────────────────────────────
            try:
                account = chart_of_account.objects.using(db).get(id=account_id)
            except chart_of_account.DoesNotExist:
                messages.error(request, "Selected account not found.")
                return receivable_form

            amount_decimal = decimal.Decimal(str(amount))

            customer_name  = ""
            customer_email = ""
            customer_code  = ""

            if accountype == "Customer":
                try:
                    customer = customer_table.objects.using(db).get(id=customer_id)
                except customer_table.DoesNotExist:
                    messages.error(request, "Customer not found.")
                    return receivable_form

                customer_name  = customer.name
                customer_email = customer.email
                customer_code  = customer.customer_code

                # ── Resolve the invoice to get invoice_total and current_paid ─
                try:
                    inv = customer_invoice.objects.using(db).filter(
                        invoiceID=invoice_no, cusID=customer.customer_code
                    ).first()
                    invoice_total = decimal.Decimal(str(inv.amount_expected)) if inv else amount_decimal
                    current_paid  = decimal.Decimal(str(inv.amount_paid))     if inv else decimal.Decimal('0.00')
                except Exception:
                    invoice_total = amount_decimal
                    current_paid  = decimal.Decimal('0.00')

                # Debit → bank/cash account (money arrives)
                DebitReceivable(
                    request, db, customer, date, description,
                    payment_method, account.account_id, amount_decimal,
                    invoiceID=invoice_no
                )
                # Credit → receivable (debt reduced)
                CreditReceivable(
                    request, db, customer, date, description,
                    payment_method, account.account_id, amount_decimal,
                    invoice_no, invoice_total, current_paid
                )

                # ── Update invoice amount_paid ────────────────────────────
                if inv:
                    inv.amount_paid = min(
                        current_paid + amount_decimal,
                        invoice_total
                    )
                    inv.save(using=db)

            elif accountype == "Vendor":
                try:
                    vendor = vendor_table.objects.using(db).get(id=vendor_id)
                except vendor_table.DoesNotExist:
                    messages.error(request, "Vendor not found.")
                    return receivable_form

                customer_name  = vendor.name
                customer_email = vendor.email
                customer_code  = getattr(vendor, 'custID', '')

                CreditPayable(
                    request, db, vendor, date, description,
                    payment_method, account.account_id, amount_decimal
                )

            # ── Update account balance and log ────────────────────────────
            account.actual_balance += amount_decimal
            account.save(using=db)
            CreateLog(db, account, amount_decimal)

            # ── Account log ───────────────────────────────────────────────
            account_log.objects.using(db).create(
                transaction_source = "Receive Payment",
                amount             = amount_decimal,
                date               = date,
                account            = account.account_id,
                account_type       = account.account_type,
                Userlogin          = request.user.username,
            )

            messages.success(request, "Payment received successfully")

            # ── Email receipt (Celery) ────────────────────────────────────
            if customer_email:
                try:
                    from main.tasks import send_receipt_email_task

                    company_name = ""
                    try:
                        company_name = request.user.company_id.company_name
                    except Exception:
                        pass

                    try:
                        base_url = request.build_absolute_uri("/")
                    except Exception:
                        base_url = getattr(settings, "SITE_URL", "https://console.afrikbook.com")

                    amount_in_words = amount_to_words(amount)

                    send_receipt_email_task.delay(
                        db_name=db,
                        customer_email=customer_email,
                        customer_name=customer_name or "",
                        invoice_no=str(invoice_no),
                        customer_code=str(customer_code or ""),
                        date_str=str(date),
                        amount=str(amount),
                        amount_in_words=str(amount_in_words),
                        description=description or "",
                        payment_method=payment_method or "",
                        company_display_name=company_name or "",
                        base_url=base_url,
                    )
                    logger.info(
                        f"[receive_payment] Receipt email queued | invoice_no={invoice_no} | to={customer_email}"
                    )

                except Exception as e:
                    logger.error(f"[receive_payment] Receipt email queue failed | invoice_no={invoice_no} | {e}\n{traceback.format_exc()}")
                    messages.warning(request, "Payment recorded but receipt email could not be queued.")

        else:
            return receivable_form
    else:
        messages.error(request, "All the fields must be filled in to submit")


# def receive_payment(request, db):
#     date           = request.POST['date']
#     invoice_no     = request.POST['invoice_no']
#     description    = request.POST['description']
#     customer_id    = request.POST.get('customer_id')
#     vendor_id      = request.POST.get('vendor_id')
#     accountype     = request.POST.get('accountType')
#     payment_method = request.POST['payment_method'] 
#     account_id     = request.POST.get('account_id')
#     amount         = request.POST['amount']


#     receivable_form = ReceivableForm({"date":date,	"description":description,"amount": amount, "payment_method": payment_method,"type": "Debit", "invoice_status": "Unused"})

   
#     conditions = required_fields(request, invoice_no, customer_id, vendor_id, account_id)
    
#     if conditions:

#         if receivable_form.is_valid():
#             if accountype == "Customer":
#                 customer = customer_table.objects.using(db).get(id=customer_id)
#                 CreditReceivable(request, db, customer, date, description, payment_method, account_id, amount)
#             elif accountype == "Vendor":
#                 vendor = vendor_table.objects.using(db).get(id=vendor_id)
#                 CreditPayable(request, db, vendor, date, description, payment_method, account_id, amount)
        
            
#             #update selected account balance
#             account = chart_of_account.objects.using(db).get(id=account_id)
#             account.actual_balance += decimal.Decimal(amount)
#             # account.save()
#             CreateLog(db, account, amount)
            
#             # create account log
#             acc_log = account_log(
#                 transaction_source  = "Receive Payment",
#                 amount              = amount,
#                 date                = date,
#                 account             = account.account_id,
#                 account_type        = account.account_type,
#                 Userlogin = request.user.username
#             )
#             # acc_log.save(using=db)
#             messages.success(request, "Payment received successfully")
#         else:
           
#             return receivable_form
#     else:
#         messages.error(request, "All the feilds must be filled in to submit")
        
        
        


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
    
    
