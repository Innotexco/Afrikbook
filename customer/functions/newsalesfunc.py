from customer.forms import CustomerSalesForm, ReceivableForm, PayableForm
from customer.models import customer_table, customer_invoice, receivable, payable, Vat #CreateOutletStockIn, CreateOutletStockInLog, 
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
from datetime import datetime
from settings.models import shipping_cost
from settings.models import CreateProfile

def invoiceExist(request, invoiceID):
    db = request.user.company_id.db_name
    # check if invoice number exists          
    if customer_invoice.objects.using(db).filter(invoiceID=invoiceID).exists() or Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).exists():
        return JsonResponse(True, safe=False)
    else:
        return JsonResponse(False, safe=False)
    
def billing_shipping_address(request, name):
    shipping = request.POST.get('shipping_address')
    method = request.POST.get('shipping_method')
    if shipping and method:
        return True
    else:
        # messages.error(request, name+" has no Shipping and Billing address")
        return False   
    
    
def billing_shipping_reference(db, invoice, cusID, shipping, method, cost):
    
    try:
        order_invoice_reference_address.objects.using(db).get(reference=invoice)
    except order_invoice_reference_address.DoesNotExist:
        order_invoice_reference_address.objects.using(db).create(source=method, reference=invoice, shipping_addr=shipping) 
   # order_invoice_billing_address.objects.using(db).create(source="", reference=invoice, billing_addr=billing) 
        
    try:
       shipping_cost.objects.using(db).get(invoiceID=invoice)
    except shipping_cost.DoesNotExist:
        shipping_cost.objects.using(db).create(invoiceID=invoice, amount=cost, custID=cusID)
        


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import tempfile
import os
import logging
from django.db import connection
from customer.models import Vat
# from django.db.models import Sum

def email_invoice_to_customer(request, db, invoiceID, customer_email, customer_name):
    try:
        invoice_items = customer_invoice.objects.using(db).filter(invoiceID=invoiceID)
        if not invoice_items.exists():
            return False, "Invoice not found"

        invoice = invoice_items.first()

        try:
            company = CreateProfile.objects.using(db).first()
        except CreateProfile.DoesNotExist:
            company = None

        subtotal    = sum(item.amount for item in invoice_items)
        vat_items   = Vat.objects.using(db).filter(source=invoiceID)
        vat_total   = sum(v.amount for v in vat_items)
        grand_total = subtotal + vat_total
        balance_due = grand_total - (invoice.amount_paid or 0)

        # ── Company footer details ───────────────────────────────────────────
        company_name    = company.CompanyName if company and company.CompanyName else request.user.company_id.company_name
        company_address = company.address     if company and company.address     else ""
        company_email   = company.email       if company and company.email       else ""
        company_phone   = company.phone       if company and company.phone       else ""
        company_rc      = company.Rc          if company and company.Rc          else ""

        # ── PDF attachment ───────────────────────────────────────────────────
        html_content = render_to_string('customer/invoice_pdf.html', {
            'invoice':       invoice,
            'invoice_items': invoice_items,
            'company':       company,
            'subtotal':      subtotal,
            'vat_items':     vat_items,
            'vat_total':     vat_total,
            'grand_total':   grand_total,
            'balance_due':   balance_due,
        })
        pdf_file = HTML(
            string=html_content,
            base_url=request.build_absolute_uri()
        ).write_pdf()

        # ── Compose email ────────────────────────────────────────────────────
        footer_lines = [company_name]
        if company_address: footer_lines.append(company_address)
        if company_email:   footer_lines.append(company_email)
        if company_rc:      footer_lines.append(f"RC {company_rc}")

        footer = "\n".join(footer_lines)

        email = EmailMessage(
            subject    = f"Invoice {invoiceID} from {company_name}",
            body       = (
                f"Dear {customer_name},\n\n"
                f"Here is your invoice {invoiceID} .We appreciate your business!\n"
                f"Please find the attached document for your invoice details.\n"
                f"──────────────────────────\n"
                f"{footer}\n"
                f"──────────────────────────"
            ),
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [customer_email],
        )
        email.attach(f"Invoice_{invoiceID}.pdf", pdf_file, 'application/pdf')
        email.send()

        logger.info(f"[email_invoice_to_customer] Sent | invoiceID={invoiceID} | to={customer_email}")
        return True, "Invoice emailed successfully"

    except Exception as e:
        logger.error(f"[email_invoice_to_customer] Failed | invoiceID={invoiceID} | {e}\n{traceback.format_exc()}")
        return False, str(e)




def send_whatsapp_invoice(phone_number, invoiceID, customer_name, grand_total, company_name):
    """
    Generates a wa.me link that opens WhatsApp with a pre-filled message.
    Works universally — mobile opens the app, desktop opens WhatsApp Web.
    """
    try:
        from urllib.parse import quote

        # Clean phone — digits only, no +, spaces, dashes or brackets
        clean_phone = (
            str(phone_number)
            .replace(' ', '')
            .replace('-', '')
            .replace('(', '')
            .replace(')', '')
            .replace('+', '')   # wa.me requires no + prefix
            .strip()
        )

        # Ensure it has a country code — if it starts with 0, assume Nigeria (+234)
        if clean_phone.startswith('0'):
            clean_phone = '234' + clean_phone[1:]

        message = (
            f"Dear {customer_name},\n\n"
            f"Your invoice *{invoiceID}* from *{company_name}* is ready.\n"
            f"Total Amount: *{grand_total}*\n\n"
            f"Thank you for your business! 🙏"
        )

        encoded_message = quote(message)
        whatsapp_url    = f"https://wa.me/{clean_phone}?text={encoded_message}"

        logger.info(
            f"[send_whatsapp_invoice] URL generated | invoiceID={invoiceID} | "
            f"phone={clean_phone}"
        )
        return True, whatsapp_url

    except Exception as e:
        logger.error(
            f"[send_whatsapp_invoice] Failed | invoiceID={invoiceID} | "
            f"phone={phone_number} | {e}\n{traceback.format_exc()}"
        )
        return False, str(e)


# def add_new_sales(request, db):
    
#     message_displayed = False  # Initialize the message_displayed variable
#     executed = False  
#     user = False  
   
#     cusID             = request.POST['cusID']
#     venID             = request.POST['venID']
#     acountType        = request.POST['accountType']
#     customer_name     = request.POST['genby']
#     invoice_date      = request.POST['invoice_date']
#     due_date          = request.POST['due_date']
#     invoiceID         = request.POST['invoiceID']
#     order_id          = request.POST['order_id']
#     Gdescription      = request.POST['Gdescription']
#     invoice_state     = request.POST.get('invoice_state')
#     credit_sales      = request.POST.get('credit_sales')
#     item_name         = request.POST.getlist('item_name')
#     purchaseP         = request.POST.getlist('purchaseP')
#     itemcode          = request.POST.getlist('item[]')
#     item_descriptions = request.POST.getlist('desc[]')
#     quantities        = request.POST.getlist('qty[]')
#     unit              = request.POST.getlist('unit[]')
#     discount          = request.POST.getlist('discount[]')
#     amount            = request.POST.getlist('amount[]')
#     vat               = request.POST.get('vat') #[:-1]
#     sub_total         = request.POST['sub-total']
#     total             = request.POST['total']
#     account_ID = request.POST.get('t_account')
#     transfer = request.POST.get('transfer_amount')
#     cash = request.POST.get('cash_amount')
#     payment_method = request.POST.get('payment_method')
#     method = request.POST.get('shipping_method')
#     shipping = request.POST.get('shipping_address')
#     shipping_cost = request.POST.get('shipping_cost')

#     instant_stockout = request.session.get('IN_STOCKOUT', 'Yes')
    
    
#     if instant_stockout == "Yes":
#         status = 1
#     else:
#         status = 0
  
#     if invoice_state:
#         invoice_state = "Pending"
#     else:
#         invoice_state = "Supplied"
    
#     # Note if any changes in this statement you have to make same chabges on return inward function
#     if credit_sales:
#         amount_paid = 0.00
#         amount_expected = total
#     else:
#         amount_paid = total
#         amount_expected = total

#     # amount_paid = total
#     # amount_expected = sub_total
    
    
    
#     int_purchaseP = [int(num) if num.isdigit() else 0 for num in purchaseP ]

#     total_purchaseP = sum(int_purchaseP)

#     if cusID:
#         res = billing_shipping_address(request, customer_name)    
#         customer_code = customer_table.objects.using(db).get(id=cusID).customer_code

#     elif venID:
#         res = False
#         customer_code = vendor_table.objects.using(db).get(id=venID).custID
#     else:        
#         customer_code = None

    
#     date_ = datetime.strptime(invoice_date, "%Y-%m-%d").date()
#     current_time = datetime.now().time()

#     date_time = datetime.combine(date_, current_time)
   
#     for i in range(len(itemcode)):
#             # Check if the itemcode (value) is equal to 0
#         if i < len(itemcode) and str(itemcode[i]) != "0":
#              # Check if quantity (value) is equal to 0 or empty 
#             if not quantities[i] or int(quantities[i]) == 0:
#                 #Automatically change the quantity to 1
#                 quantities[i] = 1
        
#             form_data = {
#                 'cusID': customer_code,
#                 'customer_name':customer_name,
#                 'invoice_date':date_time,
#                 'due_date': due_date,
#                 'invoiceID':invoiceID ,
#                 'order_ID':order_id ,
#                 'Gdescription': Gdescription,
#                 'item_name': item_name[i],
#                 'itemcode': itemcode[i],
#                 'item_description': item_descriptions[i],
#                 'qty': quantities[i],
#                 'unit_p': unit[i],
#                 'discount': discount[i],
#                 'amount': amount[i],
#                 'amount_paid': amount_paid,
#                 'amount_expected': amount_expected,

#                 "cancellation_status":0,
#                 "status":status,
#                 "Transfer":0,
#                 "POS":0,
#                 "Cash":0,
#                 "Customer_account":0,
#                 "Cheque":0,
#                 "invoice_state":invoice_state,
#                 "purchaseP":purchaseP[i],
#                 "total_purchaseP":total_purchaseP,
#                 "outlet": request.user.outlet
#             }
#             cus_form = CustomerSalesForm(form_data)
      
#             receivable_form = ReceivableForm({"date":invoice_date,	"description":Gdescription,"type": "Debit",	"amount": amount_paid, "payment_method": "Transfer","account_posted":"","invoice_status": "Unused"})
            
                
#             if cus_form.is_valid() and receivable_form.is_valid():
#                 form  = cus_form.save(commit=False)
#                 form.Userlogin = request.user.username
#                 form.save(using=db)
                
#                 #Reduce stock quantity
#                 if invoice_state == "Supplied":
#                     outlet= request.user.outlet
                   
#                     ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])

#                 if not message_displayed:
#                     if acountType == "Customer":
#                         cus = customer_table.objects.using(db).get(id=cusID)
#                         cus.invoice = cus.invoice + 1
#                         cus.save()
                        
#                     elif acountType == "Vendor":
#                         ven = vendor_table.objects.using(db).get(id=venID)
#                         ven.invoices = int(ven.invoices) + 1
#                         ven.save()
#                     if credit_sales == None:
#                         # insert into recievable
#                         if account_ID:
#                             account = chart_of_account.objects.using(db).get(account_id=account_ID)
#                             if acountType == "Customer":
#                                 DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account_ID, total)  
#                             elif acountType == "Vendor":
#                                 DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account_ID, total) 
                            
                            
#                             if payment_method == "Transfer":
#                                 if acountType == "Customer":
#                                     CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account_ID, total)
#                                 elif acountType == "Vendor":
#                                     CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account_ID, total)
#                                 CreateLog(db, account, total) 
                               

#                             elif payment_method == "Transfer and Cash":
#                                 # Transfer 
#                                 if acountType == "Customer":
#                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, "Transfer", account_ID, transfer)
#                                 elif acountType == "Vendor":
#                                     CreditPayable(request, db, cus, invoice_date, Gdescription, "Transfer", account_ID, transfer)
#                                 CreateLog(db, account, transfer)
#                                 # Cash
#                                 cash_account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
#                                 if acountType == "Customer":
#                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, "Cash", cash_account.account_id, cash)
#                                 elif acountType == "Vendor":
#                                     CreditPayable(request, db, cus, invoice_date, Gdescription, "Cash", cash_account.account_id, cash)
#                                 CreateLog(db, cash_account, cash)

#                             elif payment_method == "Cheque":
#                                 account = chart_of_account.objects.using(db).get(account_bankname="Account Receivable")     
#                                 CreateLog(db, account, total)
#                             else:
#                                 account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
#                                 if acountType == "Customer":
#                                     CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
#                                 elif acountType == "Vendor":
#                                     CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total)
                                   
#                                 CreateLog(db, account, total)

#                         else:
#                             if acountType == "Customer":
#                                 account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
#                                 DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
#                                 CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
#                                 CreateLog(db, account, total)
#                             elif acountType == "Vendor":
#                                 account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
#                                 DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total)
#                                 CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total) 
#                                 CreateLog(db, account, total)
  
#                     else:
#                         if acountType == "Customer":
#                             account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
#                             account.actual_balance += decimal.Decimal(total)
#                             # account.save()
#                             DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
#                             CreateLog(db, account, total)
#                         elif acountType == "Vendor":
#                             account = chart_of_account.objects.using(db).get(account_bankname="Purchase Account")
#                             account.actual_balance += decimal.Decimal(total)
#                             # account.save()
#                             DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total)
#                             CreateLog(db, account, total)
                        
#                         acc_log = account_log(
#                                 transaction_source  = "Sales",
#                                 amount              = total,
#                                 date                = invoice_date,
#                                 account             = account.account_id,
#                                 account_type        = account.account_type,
#                                 Userlogin = request.user.username
#                             )
#                         # acc_log.save(using=db)

#                     if res:
#                         billing_shipping_reference(db, invoiceID, cusID, shipping, method, shipping_cost)
#                     else:
#                         pass
#                     create_add_vat(db, invoiceID, vat)

#                     messages.success(request, "New Sales Invoice was added successfully")
#                     message_displayed = True
#             else:
#                 messages.error(request, "New Sales Invoice was not added  successfully")
#                 return cus_form
#         elif len(itemcode) == 1 and itemcode[i] == "0":
#             if not executed:
#                 messages.error(request, "Select at least one item")
#                 executed = True

#     if message_displayed:
#         if acountType == "Customer":
#             customer = customer_table.objects.using(db).get(id=cusID)
#             if customer.email:
#                 success, msg = email_invoice_to_customer(
#                     request, db, invoiceID, customer.email, customer_name
#                 )
#                 if success:
#                     messages.success(request, f"Invoice emailed to {customer.email}")
#                 else:
#                     messages.warning(request, f"Invoice saved but email failed: {msg}")
        
#         elif acountType == "Vendor":
#             vendor = vendor_table.objects.using(db).get(id=venID)
#             if vendor.email:
#                 success, msg = email_invoice_to_customer(
#                     request, db, invoiceID, vendor.email, customer_name
#                 )
   




import logging
import traceback
import decimal
from datetime import datetime

logger = logging.getLogger(__name__)


def clean_decimal(value):
    """Strip commas, whitespace, convert to Decimal and quantize to 2dp."""
    try:
        cleaned = str(value).replace(',', '').replace(' ', '').strip()
        return decimal.Decimal(cleaned).quantize(
            decimal.Decimal('0.01'), 
            rounding=decimal.ROUND_HALF_UP
        )
    except (decimal.InvalidOperation, TypeError, ValueError) as e:
        logger.error(f"[clean_decimal] Failed to convert value={value!r} | {e}")
        return decimal.Decimal('0.00')


def add_new_sales(request, db):
 
    message_displayed = False
    executed = False
    user = False
 
    # ── 1. Parse POST data ───────────────────────────────────────────────────
    try:
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
        vat               = request.POST.get('vat')
        sub_total         = request.POST['sub-total']
        total             = request.POST['total']
        account_ID        = request.POST.get('t_account')
        transfer          = request.POST.get('transfer_amount')
        cash              = request.POST.get('cash_amount')
        payment_method    = request.POST.get('payment_method')
        method            = request.POST.get('shipping_method')
        shipping          = request.POST.get('shipping_address')
        shipping_cost     = request.POST.get('shipping_cost')
 
        logger.info(
            f"[add_new_sales] START | invoiceID={invoiceID} | db={db} | "
            f"user={request.user.username} | acountType={acountType} | "
            f"cusID={cusID} | venID={venID} | total={total} | "
            f"credit_sales={credit_sales} | invoice_state={invoice_state} | "
            f"payment_method={payment_method} | items={len(itemcode)}"
        )
 
    except KeyError as e:
        logger.error(f"[add_new_sales] Missing POST field: {e}")
        messages.error(request, f"Missing required field: {e}")
        return None
 
    # ── 2. Clean & compute monetary values ──────────────────────────────────
    try:
        total_decimal     = clean_decimal(total)
        sub_total_decimal = clean_decimal(sub_total)
        transfer_decimal  = clean_decimal(transfer) if transfer else decimal.Decimal('0.00')
        cash_decimal      = clean_decimal(cash)     if cash     else decimal.Decimal('0.00')
 
        # Read part payment fields
        part_payment        = request.POST.get('part_payment')           # checkbox → 'on' or None
        part_payment_amount = request.POST.get('part_payment_amount', '').strip()
 
        if credit_sales:
            # Nothing paid yet — full balance outstanding
            amount_paid     = decimal.Decimal('0.00')
            amount_expected = total_decimal
 
        elif part_payment and part_payment_amount:
            # Partial payment: amount_paid < total
            part_decimal = clean_decimal(part_payment_amount)
            if part_decimal <= decimal.Decimal('0.00'):
                messages.error(request, "Part payment amount must be greater than zero.")
                return None
            if part_decimal >= total_decimal:
                messages.error(request, "Part payment amount must be less than the invoice total.")
                return None
            amount_paid     = part_decimal
            amount_expected = total_decimal   # full invoice amount is still owed
 
        else:
            # Full payment
            amount_paid     = total_decimal
            amount_expected = total_decimal
 
        # FIX: logger.debug is now INSIDE the try block (after values are assigned)
        logger.debug(
            f"[add_new_sales] Cleaned totals | total={total_decimal} | "
            f"sub_total={sub_total_decimal} | amount_paid={amount_paid} | "
            f"amount_expected={amount_expected} | transfer={transfer_decimal} | "
            f"cash={cash_decimal} | part_payment={part_payment} | "
            f"part_payment_amount={part_payment_amount if part_payment else 'N/A'}"
        )
 
    except Exception as e:
        # FIX: use locals().get() to safely reference variables that may not exist yet
        logger.error(
            f"[add_new_sales] Failed to clean monetary values | "
            f"part_payment_amount={locals().get('part_payment_amount', 'N/A')} | "
            f"{e}\n{traceback.format_exc()}"
        )
        messages.error(request, "Invalid amount format.")
        return None
 
    # ── 3. Misc setup ────────────────────────────────────────────────────────
    instant_stockout = request.session.get('IN_STOCKOUT', 'Yes')
    status = 1 if instant_stockout == "Yes" else 0
 
    if invoice_state:
        invoice_state = "Pending"
    else:
        invoice_state = "Supplied"
 
    logger.debug(
        f"[add_new_sales] Config | invoice_state={invoice_state} | "
        f"instant_stockout={instant_stockout} | status={status}"
    )
 
    try:
        int_purchaseP   = [int(num) if num.isdigit() else 0 for num in purchaseP]
        total_purchaseP = sum(int_purchaseP)
    except Exception as e:
        logger.error(f"[add_new_sales] Failed to compute purchaseP totals: {e}")
        total_purchaseP = 0
 
    # ── 4. Resolve customer / vendor ─────────────────────────────────────────
    try:
        if cusID:
            res           = billing_shipping_address(request, customer_name)
            customer_code = customer_table.objects.using(db).get(id=cusID).customer_code
            logger.debug(f"[add_new_sales] Customer resolved | cusID={cusID} | customer_code={customer_code}")
 
        elif venID:
            res           = False
            customer_code = vendor_table.objects.using(db).get(id=venID).custID
            logger.debug(f"[add_new_sales] Vendor resolved | venID={venID} | customer_code={customer_code}")
 
        else:
            res           = False
            customer_code = None
            logger.warning(f"[add_new_sales] No cusID or venID | invoiceID={invoiceID}")
 
    except customer_table.DoesNotExist:
        logger.error(f"[add_new_sales] Customer not found | cusID={cusID}")
        messages.error(request, f"Customer ID {cusID} not found.")
        return None
    except vendor_table.DoesNotExist:
        logger.error(f"[add_new_sales] Vendor not found | venID={venID}")
        messages.error(request, f"Vendor ID {venID} not found.")
        return None
    except Exception as e:
        logger.error(f"[add_new_sales] Error resolving customer/vendor: {e}\n{traceback.format_exc()}")
        messages.error(request, "Failed to resolve customer or vendor.")
        return None
 
    # ── 5. Parse date ────────────────────────────────────────────────────────
    try:
        date_       = datetime.strptime(invoice_date, "%Y-%m-%d").date()
        date_time   = datetime.combine(date_, datetime.now().time())
    except ValueError as e:
        logger.error(f"[add_new_sales] Invalid invoice_date={invoice_date!r} | {e}")
        messages.error(request, f"Invalid date format: {invoice_date}")
        return None
 
    # ── 6. Loop over line items ──────────────────────────────────────────────
    logger.debug(f"[add_new_sales] Processing {len(itemcode)} item(s) | invoiceID={invoiceID}")
 
    for i in range(len(itemcode)):
 
        logger.debug(
            f"[add_new_sales] Item [{i}] | itemcode={itemcode[i]} | "
            f"qty={quantities[i]} | unit={unit[i]} | "
            f"discount={discount[i]} | amount={amount[i]}"
        )
 
        # Single zero item → nothing selected
        if len(itemcode) == 1 and itemcode[i] == "0":
            if not executed:
                logger.warning(f"[add_new_sales] No item selected | invoiceID={invoiceID}")
                messages.error(request, "Select at least one item")
                executed = True
            continue
 
        # Skip zero-itemcode rows in multi-item lists
        if str(itemcode[i]) == "0":
            logger.debug(f"[add_new_sales] Skipping itemcode=0 at index {i}")
            continue
 
        # Auto-fix zero/empty quantity
        if not quantities[i] or int(quantities[i]) == 0:
            quantities[i] = 1
            logger.debug(f"[add_new_sales] Auto-set qty=1 | item [{i}] | itemcode={itemcode[i]}")
 
        # Clean per-line monetary values
        try:
            clean_unit_p    = clean_decimal(unit[i])
            clean_discount  = clean_decimal(discount[i]) if discount[i] else decimal.Decimal('0.00')
            clean_amount    = clean_decimal(amount[i])
            clean_purchaseP = clean_decimal(purchaseP[i])
 
            logger.debug(
                f"[add_new_sales] Cleaned line [{i}] | unit_p={clean_unit_p} | "
                f"discount={clean_discount} | amount={clean_amount} | "
                f"purchaseP={clean_purchaseP}"
            )
        except Exception as e:
            logger.error(
                f"[add_new_sales] Failed to clean line values | item [{i}] | "
                f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
            )
            messages.error(request, f"Invalid amount on item {i + 1}.")
            return None
 
        # Build forms
        form_data = {
            'cusID':               customer_code,
            'customer_name':       customer_name,
            'invoice_date':        date_time,
            'due_date':            due_date,
            'invoiceID':           invoiceID,
            'order_ID':            order_id,
            'Gdescription':        Gdescription,
            'item_name':           item_name[i],
            'itemcode':            itemcode[i],
            'item_description':    item_descriptions[i],
            'qty':                 quantities[i],
            'unit_p':              clean_unit_p,
            'discount':            clean_discount,
            'amount':              clean_amount,
            'amount_paid':         amount_paid,
            'amount_expected':     amount_expected,
            'cancellation_status': 0,
            'status':              status,
            'Transfer':            0,
            'POS':                 0,
            'Cash':                0,
            'Customer_account':    0,
            'Cheque':              0,
            'invoice_state':       invoice_state,
            'purchaseP':           clean_purchaseP,
            'total_purchaseP':     total_purchaseP,
            'outlet':              request.user.outlet,
        }
 
        cus_form = CustomerSalesForm(form_data)
        receivable_form = ReceivableForm({
            "date":           invoice_date,
            "description":    Gdescription,
            "type":           "Debit",
            "amount":         amount_paid,
            "payment_method": "Transfer",
            "account_posted": "",
            "invoice_status": "Unused",
        })
 
        if not cus_form.is_valid():
            logger.error(
                f"[add_new_sales] CustomerSalesForm invalid | item [{i}] | "
                f"invoiceID={invoiceID} | errors={cus_form.errors.as_json()}"
            )
 
        if not receivable_form.is_valid():
            logger.error(
                f"[add_new_sales] ReceivableForm invalid | item [{i}] | "
                f"invoiceID={invoiceID} | errors={receivable_form.errors.as_json()}"
            )
 
        if cus_form.is_valid() and receivable_form.is_valid():
 
            # ── Save invoice line ────────────────────────────────────────────
            try:
                form            = cus_form.save(commit=False)
                form.Userlogin  = request.user.username
                form.save(using=db)
                logger.info(
                    f"[add_new_sales] Line saved | item [{i}] | "
                    f"invoiceID={invoiceID} | itemcode={itemcode[i]}"
                )
            except Exception as e:
                logger.error(
                    f"[add_new_sales] Failed to save line | item [{i}] | "
                    f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
                )
                messages.error(request, "New Sales Invoice was not added successfully")
                return cus_form
 
            # ── Reduce stock ─────────────────────────────────────────────────
            if invoice_state == "Supplied":
                try:
                    outlet = request.user.outlet
                    ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])
                    logger.info(
                        f"[add_new_sales] Stock reduced | outlet={outlet} | "
                        f"itemcode={itemcode[i]} | qty={quantities[i]}"
                    )
                except Exception as e:
                    logger.error(
                        f"[add_new_sales] Stock reduction failed | "
                        f"itemcode={itemcode[i]} | {e}\n{traceback.format_exc()}"
                    )
 
            if not message_displayed:
 
                # ── Increment invoice counter ────────────────────────────────
                try:
                    if acountType == "Customer":
                        cus         = customer_table.objects.using(db).get(id=cusID)
                        cus.invoice += 1
                        cus.save()
                        logger.debug(f"[add_new_sales] Customer invoice count incremented | cusID={cusID}")
 
                    elif acountType == "Vendor":
                        ven          = vendor_table.objects.using(db).get(id=venID)
                        ven.invoices = int(ven.invoices) + 1
                        ven.save()
                        logger.debug(f"[add_new_sales] Vendor invoice count incremented | venID={venID}")
 
                except Exception as e:
                    logger.error(
                        f"[add_new_sales] Failed to increment invoice count | "
                        f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
                    )
 
                # ── Accounting entries ───────────────────────────────────────
                try:
                    if credit_sales is None:
                        if account_ID:
                            account = chart_of_account.objects.using(db).get(account_id=account_ID)
                            logger.debug(
                                f"[add_new_sales] Account resolved | "
                                f"account_ID={account_ID} | payment_method={payment_method}"
                            )
 
                            if acountType == "Customer":
                                DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account_ID, total_decimal)
                            elif acountType == "Vendor":
                                DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account_ID, total_decimal)
 
                            if payment_method == "Transfer":
                                if acountType == "Customer":
                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account_ID, total_decimal)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account_ID, total_decimal)
                                CreateLog(db, account, total_decimal)
                                logger.debug(f"[add_new_sales] Transfer posted | total={total_decimal}")
 
                            elif payment_method == "Transfer and Cash":
                                if acountType == "Customer":
                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, "Transfer", account_ID, transfer_decimal)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, cus, invoice_date, Gdescription, "Transfer", account_ID, transfer_decimal)
                                CreateLog(db, account, transfer_decimal)
 
                                cash_account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                                if acountType == "Customer":
                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, "Cash", cash_account.account_id, cash_decimal)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, cus, invoice_date, Gdescription, "Cash", cash_account.account_id, cash_decimal)
                                CreateLog(db, cash_account, cash_decimal)
                                logger.debug(
                                    f"[add_new_sales] Transfer+Cash split posted | "
                                    f"transfer={transfer_decimal} | cash={cash_decimal}"
                                )
 
                            elif payment_method == "Cheque":
                                account = chart_of_account.objects.using(db).get(account_bankname="Account Receivable")
                                CreateLog(db, account, total_decimal)
                                logger.debug(f"[add_new_sales] Cheque posted | total={total_decimal}")
 
                            else:
                                account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
                                if acountType == "Customer":
                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                                CreateLog(db, account, total_decimal)
                                logger.debug(f"[add_new_sales] Other payment posted | method={payment_method}")
 
                        else:
                            # No account_ID — fall back to default Sales Account
                            logger.warning(
                                f"[add_new_sales] No account_ID provided, using default Sales Account | "
                                f"invoiceID={invoiceID}"
                            )
                            account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                            if acountType == "Customer":
                                DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                                CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                            elif acountType == "Vendor":
                                DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                                CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                            CreateLog(db, account, total_decimal)
 
                    else:
                        # Credit sales path
                        logger.debug(
                            f"[add_new_sales] Credit sale | acountType={acountType} | "
                            f"total={total_decimal}"
                        )
                        if acountType == "Customer":
                            account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                            account.actual_balance += total_decimal
                            DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                            CreateLog(db, account, total_decimal)
 
                        elif acountType == "Vendor":
                            account = chart_of_account.objects.using(db).get(account_bankname="Purchase Account")
                            account.actual_balance += total_decimal
                            DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total_decimal)
                            CreateLog(db, account, total_decimal)
 
                        acc_log = account_log(
                            transaction_source = "Sales",
                            amount             = total_decimal,
                            date               = invoice_date,
                            account            = account.account_id,
                            account_type       = account.account_type,
                            Userlogin          = request.user.username,
                        )
                        logger.debug(f"[add_new_sales] account_log built (not saved) | invoiceID={invoiceID}")
 
                except chart_of_account.DoesNotExist as e:
                    logger.error(
                        f"[add_new_sales] Chart of account not found | "
                        f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
                    )
                    messages.error(request, "Accounting entry failed: account not found.")
                    return None
                except Exception as e:
                    logger.error(
                        f"[add_new_sales] Accounting entry failed | "
                        f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
                    )
                    messages.error(request, "Accounting entry failed.")
                    return None
 
                # ── Shipping reference ───────────────────────────────────────
                try:
                    if res:
                        billing_shipping_reference(db, invoiceID, cusID, shipping, method, shipping_cost)
                        logger.debug(f"[add_new_sales] Shipping reference saved | invoiceID={invoiceID}")
                except Exception as e:
                    logger.error(
                        f"[add_new_sales] Shipping reference failed | "
                        f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
                    )
 
                # ── VAT ──────────────────────────────────────────────────────
                try:
                    create_add_vat(db, invoiceID, vat)
                    logger.debug(f"[add_new_sales] VAT recorded | invoiceID={invoiceID} | vat={vat}")
                except Exception as e:
                    logger.error(
                        f"[add_new_sales] VAT creation failed | "
                        f"invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
                    )
 
                messages.success(request, "New Sales Invoice was added successfully")
                message_displayed = True
                logger.info(f"[add_new_sales] Invoice saved successfully | invoiceID={invoiceID}")
 
        else:
            logger.error(
                f"[add_new_sales] Form validation failed | item [{i}] | "
                f"invoiceID={invoiceID} | "
                f"cus_form_errors={cus_form.errors.as_json()} | "
                f"receivable_form_errors={receivable_form.errors.as_json()}"
            )
            messages.error(request, "New Sales Invoice was not added successfully")
            return cus_form
 
 
    # ── 7. Email & WhatsApp invoice ──────────────────────────────────────────
    if message_displayed:
        try:
            # ── Calculate grand_total for WhatsApp message ───────────────
            from decimal import Decimal
            try:
                vat_items   = Vat.objects.using(db).filter(source=invoiceID)
                vat_total   = sum(v.amount for v in vat_items)
                subtotal    = Decimal(str(total_decimal))
                grand_total = subtotal + vat_total
            except Exception as e:
                logger.warning(f"[add_new_sales] Could not compute grand_total | {e}")
                grand_total = total_decimal  # fallback to subtotal if VAT lookup fails
            # ─────────────────────────────────────────────────────────────
 
            company       = CreateProfile.objects.using(db).get(CompanyName=request.user.company_id.company_name)
            send_email    = company.send_email_invoice
            send_whatsapp = company.send_whatsapp_invoice
 
            if acountType == "Customer":
                customer = customer_table.objects.using(db).get(id=cusID)
 
                # Email
                if send_email and customer.email:
                    success, msg = email_invoice_to_customer(request, db, invoiceID, customer.email, customer_name)
                    if success:
                        messages.success(request, f"Invoice emailed to {customer.email}")
                    else:
                        messages.warning(request, f"Invoice saved but email failed: {msg}")
 
                # WhatsApp
                if send_whatsapp and customer.phone:
                    success, whatsapp_url = send_whatsapp_invoice(
                        customer.phone, invoiceID, customer_name,
                        f"{grand_total:,.2f}", request.user.company_id.company_name
                    )
                    if success:
                        request.session['whatsapp_url'] = whatsapp_url
                        logger.info(f"[add_new_sales] WhatsApp URL stored | invoiceID={invoiceID} | to={customer.phone}")
                    else:
                        messages.warning(request, f"Could not generate WhatsApp link: {whatsapp_url}")
 
            elif acountType == "Vendor":
                vendor = vendor_table.objects.using(db).get(id=venID)
 
                # Email
                if send_email and vendor.email:
                    success, msg = email_invoice_to_customer(request, db, invoiceID, vendor.email, customer_name)
                    if success:
                        messages.success(request, f"Invoice emailed to {vendor.email}")
                    else:
                        messages.warning(request, f"Invoice saved but email failed: {msg}")
 
                # WhatsApp
                if send_whatsapp and vendor.phone:
                    success, whatsapp_url = send_whatsapp_invoice(
                        vendor.phone, invoiceID, customer_name,
                        f"{grand_total:,.2f}", request.user.company_id.company_name
                    )
                    if success:
                        request.session['whatsapp_url'] = whatsapp_url
                        logger.info(f"[add_new_sales] WhatsApp URL stored | invoiceID={invoiceID} | to={vendor.phone}")
                    else:
                        messages.warning(request, f"Could not generate WhatsApp link: {whatsapp_url}")
 
        except Exception as e:
            logger.error(
                f"[add_new_sales] Notification step failed | invoiceID={invoiceID} | {e}\n{traceback.format_exc()}"
            )


def create_add_vat(db, invoiceID, vat):
   
    if vat:
        try:
            Vat.objects.using(db).get(source=invoiceID, amount=vat)
        except Vat.DoesNotExist:
            Vat.objects.using(db).create(source=invoiceID, amount=vat)
            vat_account = chart_of_account.objects.using(db).get(account_bankname="Vat Account")
            vat_account.actual_balance += decimal.Decimal(vat)
            vat_account.save()

def create_minus_vat(db, invoiceID, vat):
    
    if vat:
        try:
            Vat.objects.using(db).get(source=invoiceID, amount=-abs(decimal.Decimal(vat)))
        except Vat.DoesNotExist:
            Vat.objects.using(db).create(source=invoiceID, amount=-abs(decimal.Decimal(vat)))
            vat_account = chart_of_account.objects.using(db).get(account_bankname="Vat Account")
            vat_account.actual_balance -= decimal.Decimal(vat)
            vat_account.save()
