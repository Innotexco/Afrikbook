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

from django.db import transaction
import logging
import decimal

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




def new_return_inwards(request, db):

    message_displayed = False

    try:
        refund_date       = request.POST['refund_date']
        order_no          = request.POST.get('order_no', '')
        p_method          = request.POST.get('method')
        cusID             = request.POST.get('cusID')
        venID             = request.POST.get('venID')
        customer_name     = request.POST['genby']
        invoiceID         = request.POST['invoiceID']
        Gdescription      = request.POST.get('Gdescription', '')
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
        total             = request.POST['total']
        initial_total     = request.POST.get('initial_total', total)

    except KeyError as e:
        messages.error(request, f"Missing required field: {e}")
        return None

    
    try:
        total_purchaseP = sum(
            float(p) if p and str(p).strip() not in ('', '0') else 0
            for p in purchaseP
        )
    except Exception:
        total_purchaseP = 0

    
    try:
        if accountType == "Customer":
            cus           = customer_table.objects.using(db).get(customer_code=cusID)
            customer_id   = cus.customer_code
            customer_name = cus.name
        elif accountType == "Vendor":
            ven           = vendor_table.objects.using(db).get(custID=venID)
            customer_id   = ven.custID
            customer_name = ven.name
        else:
            messages.error(request, "Invalid account type.")
            return None
    except (customer_table.DoesNotExist, vendor_table.DoesNotExist) as e:
        messages.error(request, f"Customer/Vendor not found: {e}")
        return None

    
    invoice2 = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
    if not invoice2:
        messages.error(request, f"Invoice {invoiceID} not found.")
        return None


    try:
        total_decimal         = clean_decimal(total)
        initial_total_decimal = clean_decimal(initial_total)
    except Exception as e:
        messages.error(request, f"Invalid amount format: {e}")
        return None

    returned_invoiceID = invoiceID + "_returned"

    # ── 6. Get the payment account used at sale time ──────────────────────────
    # This was stored on the invoice when the sale was created.
    # Falls back to '4001-Sales' for old invoices created before this field existed.
    original_payment_account = invoice2.payment_account or '4001-Sales'

    # ── 7. Main transaction block ─────────────────────────────────────────────
    try:
        with transaction.atomic(using=db):

            for i in range(len(itemcode)):

                if str(itemcode[i]) == "0":
                    continue

                if not quantities[i] or quantities[i] == "0":
                    quantities[i] = 1

                try:
                    clean_unit_p   = clean_decimal(unit[i])
                    clean_discount = clean_decimal(discount[i]) if discount[i] else decimal.Decimal('0.00')
                    clean_amount   = clean_decimal(amount[i])
                    clean_purchase = clean_decimal(purchaseP[i]) if i < len(purchaseP) and purchaseP[i] else decimal.Decimal('0.00')
                except Exception as e:
                    messages.error(request, f"Invalid amount on item {i + 1}: {e}")
                    raise

                form_data = {
                    'cusID':               customer_id,
                    'customer_name':       customer_name,
                    'invoice_date':        refund_date,
                    'due_date':            invoice2.due_date,
                    'invoiceID':           returned_invoiceID,
                    'order_ID':            order_no,
                    'Gdescription':        Gdescription,
                    'item_name':           item_name[i],
                    'itemcode':            itemcode[i],
                    'item_description':    item_descriptions[i],
                    'qty':                 quantities[i],
                    'unit_p':              clean_unit_p,
                    'discount':            clean_discount,
                    'amount':              clean_amount,
                    'amount_paid':         total_decimal,
                    'amount_expected':     total_decimal,
                    'invoice_state':       'Cancelled',
                    'cancellation_status': 0,
                    'status':              1,
                    'payment_method':      p_method,
                    'Transfer':            1 if p_method == 'Transfer' else 0,
                    'POS':                 1 if p_method == 'POS'      else 0,
                    'Cash':                1 if p_method == 'Cash'     else 0,
                    'Customer_account':    0,
                    'Cheque':              1 if p_method == 'Cheque'   else 0,
                    'purchaseP':           clean_purchase,
                    'total_purchaseP':     total_purchaseP,
                    'outlet':              invoice2.outlet,
                    'payment_account':     original_payment_account,
                }

                invoice_form    = CustomerSalesForm(form_data)
                receivable_form = ReceivableForm({
                    "date":           refund_date,
                    "description":    Gdescription,
                    "type":           "Debit",
                    "amount":         total_decimal,
                    "payment_method": p_method,
                    "invoice_status": "Unused",
                })

                if not invoice_form.is_valid() or not receivable_form.is_valid():
                    messages.error(request, f"Invalid form data on item {i + 1}: {invoice_form.errors}")
                    raise ValueError("Form validation failed")

                # ── Save return invoice line ───────────────────────────────────
                form_instance           = invoice_form.save(commit=False)
                form_instance.Userlogin = request.user.username
                form_instance.save(using=db)

                # ── Return stock to outlet ─────────────────────────────────────
                try:
                    IncreaseOutletStockinItemQuantity(db, invoice2.outlet, itemcode[i], quantities[i])
                except Exception as e:
                    messages.error(request, f"Stock update failed for item {i + 1}: {e}")
                    raise

                # ── Create outlet stock log ────────────────────────────────────
                CreateOutletStockinLog(
                    db, refund_date, returned_invoiceID, order_no,
                    customer_name, " ", invoice2.outlet, Gdescription,
                    item_name[i], item_descriptions[i], quantities[i],
                    invoice2.token_id, invoice2.Userlogin, itemcode[i],
                    clean_unit_p, ""
                )

                # ── Once-per-invoice operations ────────────────────────────────
                if not message_displayed:

                    # Cancel original invoice
                    customer_invoice.objects.using(db).filter(
                        invoiceID=invoiceID, cusID=customer_id
                    ).update(
                        invoiceID           = returned_invoiceID,
                        invoice_state       = "Cancelled",
                        cancellation_status = "1",
                        payment_method      = p_method,
                    )

                    # Increment refund counter
                    try:
                        if accountType == "Customer":
                            cus.refund_invoice += 1
                            cus.save(using=db)
                        elif accountType == "Vendor":
                            ven.refundInvoice += 1
                            ven.save(using=db)
                    except Exception as e:
                        messages.error(request, f"Failed to update refund counter: {e}")
                        raise

                    # ── Accounting ─────────────────────────────────────────────
                    try:
                        was_fully_paid = invoice2.amount_paid >= invoice2.amount_expected

                        if not was_fully_paid:
                            # Unpaid/partial — debit the return account only
                            if accountType == "Customer":
                                debtor_account = chart_of_account.objects.using(db).get(
                                    account_id='2001-ReturnInward'
                                )
                            else:
                                debtor_account = chart_of_account.objects.using(db).get(
                                    account_id='1001-ReturnOutward'
                                )
                            debtor_account.actual_balance += total_decimal
                            debtor_account.save(using=db)
                            CreateLog(db, debtor_account, total_decimal)

                            account_log.objects.using(db).create(
                                transaction_source = "Return Inward",
                                amount             = total_decimal,
                                date               = refund_date,
                                account            = debtor_account.account_id,
                                account_type       = debtor_account.account_type,
                                Userlogin          = request.user.username,
                            )

                        else:
                            # Fully paid — reverse using the exact account from the original sale
                            try:
                                pay_account = chart_of_account.objects.using(db).get(
                                    account_id=original_payment_account
                                )
                            except chart_of_account.DoesNotExist:
                                # Fallback if stored account no longer exists
                                pay_account = chart_of_account.objects.using(db).get(
                                    account_id='4001-Sales'
                                )

                            if accountType == "Customer":
                                CreditReceivable(
                                    request, db, cus, refund_date,
                                    Gdescription, p_method,
                                    pay_account.account_id,
                                    initial_total_decimal,
                                    returned_invoiceID,
                                    initial_total_decimal,
                                    decimal.Decimal('0.00'),
                                )
                            elif accountType == "Vendor":
                                CreditPayable(
                                    request, db, ven, refund_date,
                                    Gdescription, p_method,
                                    pay_account.account_id,
                                    initial_total_decimal,
                                    returned_invoiceID,
                                    initial_total_decimal,
                                    decimal.Decimal('0.00'),
                                )

                            # Reverse the balance on the original payment account
                            pay_account.actual_balance -= total_decimal
                            pay_account.save(using=db)
                            CreateLog(db, pay_account, total_decimal)

                            account_log.objects.using(db).create(
                                transaction_source = "Return Inward",
                                amount             = total_decimal,
                                date               = refund_date,
                                account            = pay_account.account_id,
                                account_type       = pay_account.account_type,
                                Userlogin          = request.user.username,
                            )

                    except chart_of_account.DoesNotExist as e:
                        messages.error(request, f"Account not found: {e}")
                        raise
                    except Exception as e:
                        messages.error(request, f"Accounting entry failed: {e}")
                        raise

                    # ── VAT reversal ───────────────────────────────────────────
                    try:
                        create_minus_vat(db, returned_invoiceID, vat)
                    except Exception as e:
                        messages.error(request, f"VAT reversal failed: {e}")
                        raise

                    messages.success(request, "Inward Return processed successfully")
                    message_displayed = True

    except Exception as e:
        if not message_displayed:
            if not any(messages.get_messages(request)):
                messages.error(request, "Return could not be saved. All changes have been rolled back.")
        return None


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
                            debtor_account = chart_of_account.objects.using(db).get(account_id='2001-ReturnInward')
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                            CreateLog(db, debtor_account, total)
                        elif accountType == "Vendor":
                            debtor_account = chart_of_account.objects.using(db).get(account_id='1001-ReturnOutward')
                            debtor_account.actual_balance += decimal.Decimal(total)
                            # debtor_account.save()
                            CreateLog(db, debtor_account, total)
                        
                    else:
                        account = chart_of_account.objects.using(db).get(account_id='4001-Sales')
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



