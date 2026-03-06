from customer.models import customer_table, payable, receivable
from customer.forms import ReceivableForm, PayableForm
from account.models import chart_of_account, account_log
from vendor.models import vendor_table
from django.contrib import messages
import decimal, uuid
from customer.functions.generalFunction import *
from django.core.mail import EmailMessage
from weasyprint import HTML
from django.template.loader import render_to_string
from settings.models import CreateProfile
import logging
import traceback

logger = logging.getLogger(__name__)


def amount_to_words(amount):
    """Convert a decimal amount to words e.g. 15000.00 → Fifteen Thousand Naira Only"""
    try:
        amount      = float(amount)
        naira       = int(amount)
        kobo        = round((amount - naira) * 100)

        ones  = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
                 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen',
                 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens  = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
                 'Sixty', 'Seventy', 'Eighty', 'Ninety']

        def words(n):
            if n == 0:   return ''
            if n < 20:   return ones[n]
            if n < 100:  return tens[n // 10] + ((' ' + ones[n % 10]) if n % 10 else '')
            if n < 1000: return ones[n // 100] + ' Hundred' + ((' ' + words(n % 100)) if n % 100 else '')
            if n < 1_000_000:
                return words(n // 1000) + ' Thousand' + ((' ' + words(n % 1000)) if n % 1000 else '')
            if n < 1_000_000_000:
                return words(n // 1_000_000) + ' Million' + ((' ' + words(n % 1_000_000)) if n % 1_000_000 else '')
            return words(n // 1_000_000_000) + ' Billion' + ((' ' + words(n % 1_000_000_000)) if n % 1_000_000_000 else '')

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

            customer_name  = ""
            customer_email = ""

            if accountype == "Customer":
                customer       = customer_table.objects.using(db).get(id=customer_id)
                customer_name  = customer.name
                customer_email = customer.email
                CreditReceivable(request, db, customer, date, description, payment_method, account_id, amount)

            elif accountype == "Vendor":
                vendor         = vendor_table.objects.using(db).get(id=vendor_id)
                customer_name  = vendor.name
                customer_email = vendor.email
                CreditPayable(request, db, vendor, date, description, payment_method, account_id, amount)

            # Update account balance
            account = chart_of_account.objects.using(db).get(id=account_id)
            account.actual_balance += decimal.Decimal(amount)
            CreateLog(db, account, amount)

            # Account log
            acc_log = account_log(
                transaction_source = "Receive Payment",
                amount             = amount,
                date               = date,
                account            = account.account_id,
                account_type       = account.account_type,
                Userlogin          = request.user.username,
            )

            messages.success(request, "Payment received successfully")

            # ── Email receipt ────────────────────────────────────────────────
            if customer_email:
                try:
                    company = CreateProfile.objects.using(db).first()

                    company_name    = company.CompanyName if company and company.CompanyName else request.user.company_id.company_name
                    company_address = company.address     if company and company.address     else ""
                    company_email_  = company.email       if company and company.email       else ""
                    company_phone   = company.phone       if company and company.phone       else ""
                    company_rc      = company.Rc          if company and company.Rc          else ""

                    amount_in_words = amount_to_words(amount)

                    # Render receipt HTML
                    html_content = render_to_string('journal/receipt_email.html', {
                        'company':        company,
                        'customer_name':  customer_name,
                        'invoice_no':     invoice_no,
                        'date':           date,
                        'amount':         amount,
                        'amount_in_words': amount_in_words,
                        'description':    description,
                        'payment_method': payment_method,
                    })

                    # Convert to PDF
                    pdf_file = HTML(
                        string=html_content,
                        base_url=request.build_absolute_uri()
                    ).write_pdf()

                    # Footer
                    footer_lines = [company_name]
                    if company_address: footer_lines.append(company_address)
                    if company_email_:  footer_lines.append(company_email_)
                    if company_phone:   footer_lines.append(company_phone)
                    if company_rc:      footer_lines.append(f"RC {company_rc}")
                    footer = "\n".join(footer_lines)

                    email = EmailMessage(
                        subject    = f"Payment Receipt — Invoice {invoice_no}",
                        body       = (
                            f"Dear {customer_name},\n\n"
                            f"Thank you for your payment of {amount} for invoice {invoice_no}.\n"
                            f"Please find your receipt attached.\n\n"
                            f"──────────────────────────\n"
                            f"{footer}\n"
                            f"──────────────────────────"
                        ),
                        from_email = settings.DEFAULT_FROM_EMAIL,
                        to         = [customer_email],
                    )
                    email.attach(f"Receipt_{invoice_no}.pdf", pdf_file, 'application/pdf')
                    email.send()

                    logger.info(f"[receive_payment] Receipt emailed | invoice_no={invoice_no} | to={customer_email}")

                except Exception as e:
                    logger.error(f"[receive_payment] Receipt email failed | invoice_no={invoice_no} | {e}\n{traceback.format_exc()}")
                    messages.warning(request, "Payment recorded but receipt email could not be sent.")
            else:
                logger.debug(f"[receive_payment] No email address | skipping receipt | invoice_no={invoice_no}")

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
    
    
