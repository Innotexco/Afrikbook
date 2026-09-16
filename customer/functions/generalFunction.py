from customer.models import *  
import decimal, uuid
from decimal import Decimal
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog, CreateStockIn, CreateStockInLog
from django.db.models import Q
from django.db import transaction



# def CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total):

#     # Generate a new transaction ID
#     transaction_id = uuid.uuid4()

#     if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
#         initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
#     else: 
#         initial_bal = decimal.Decimal(0.00)
    
#     if initial_bal > 0:
#         balance = decimal.Decimal(initial_bal) - decimal.Decimal(total)
#     else:
#         balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

#     create_receivable = receivable(
#         date=refund_date,
#         description= Gdescription,
#         type = "Credit",
#         amount = total, 
#         payment_method =p_method,
#         invoice_status ="Unused",
#         customer_id = cus.customer_code,
#         customer_name = cus.name,
#         initial_amount = initial_bal,
#         balance = balance,
#         account_posted = account, # default account
#         transaction_id = transaction_id,
#         Userlogin = request.user.username)
#     create_receivable.save(using=db)


# def DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total):

#     # Generate a new transaction ID
#     transaction_id = uuid.uuid4()

#     if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
#         initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
#     else: 
#         initial_bal = decimal.Decimal(0.00)
    
#     if initial_bal > 0:
#         balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)
#     else:
#         balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

#     create_receivable = receivable(
#         date=refund_date,
#         description= Gdescription,
#         type = "Debit",
#         amount = total, 
#         payment_method = p_method,
#         invoice_status ="Unused",
#         customer_id = cus.customer_code,
#         customer_name = cus.name,
#         initial_amount = initial_bal,
#         balance = balance,
#         account_posted = account, # default account
#         transaction_id = transaction_id,
#         Userlogin = request.user.username)
#     create_receivable.save(using=db)



def CreditPayable(request, db, ven, refund_date, Gdescription, p_method, account, total):

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    if payable.objects.using(db).filter(vendor_id=ven.custID).exists():
        initial_bal = payable.objects.using(db).filter(vendor_id=ven.custID).last().balance
    else: 
        initial_bal = decimal.Decimal(0.00)
    
    if initial_bal > 0:
        balance = decimal.Decimal(initial_bal) - decimal.Decimal(total)
    else:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

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
        account_posted = account, # default account
        transaction_id = transaction_id,
        Userlogin = request.user.username)
    create_payable.save(using=db)


def DebitPayable(request, db, ven, refund_date, Gdescription, p_method, account,  total):

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    if payable.objects.using(db).filter(vendor_id=ven.custID).exists():
        initial_bal = payable.objects.using(db).filter(vendor_id=ven.custID).last().balance
    else: 
        initial_bal = decimal.Decimal(0.00)
    
    if initial_bal > 0:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)
    else:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

    create_payable = payable(
        date=refund_date,
        description= Gdescription,
        type = "Debit",
        amount = total, 
        payment_method = p_method,
        vendor_id = ven.custID,
        vendor_name = ven.name,
        initial_amount = initial_bal,
        balance = balance,
        account_posted = account, # default account
        transaction_id = transaction_id,
        Userlogin = request.user.username)
    create_payable.save(using=db)
    
    

def _last_receivable_balance(db, customer_code):
    prior = (
        receivable.objects.using(db)
        .filter(customer_id=customer_code)
        .order_by('date', 'id')
        .last()
    )
    if prior is None:
        return Decimal('0.00')
    return Decimal(str(prior.balance or 0))


def DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total, invoiceID=None):
    transaction_id = uuid.uuid4()

    initial_bal = _last_receivable_balance(db, cus.customer_code)
    balance = initial_bal + Decimal(str(total))

    create_receivable = receivable(
        date           = refund_date,
        description    = Gdescription,
        type           = "Debit",
        amount         = total,
        payment_method = p_method,
        invoice_status = "Unused",
        customer_id    = cus.customer_code,
        customer_name  = cus.name,
        initial_amount = initial_bal,
        balance        = balance,
        account_posted = account,
        transaction_id = transaction_id,
        token_id       = invoiceID or "",
        Userlogin      = request.user.username,
    )
    create_receivable.save(using=db)


def CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account, amount_paid_now, invoiceID, invoice_total, current_paid_before):
    transaction_id = uuid.uuid4()

    initial_bal = _last_receivable_balance(db, cus.customer_code)
    balance = initial_bal - Decimal(str(amount_paid_now))

    create_receivable = receivable(
        date           = refund_date,
        description    = Gdescription,
        type           = "Credit",
        amount         = amount_paid_now,
        payment_method = p_method,
        invoice_status = "Unused",
        customer_id    = cus.customer_code,
        customer_name  = cus.name,
        initial_amount = initial_bal,
        balance        = balance,
        account_posted = account,
        transaction_id = transaction_id,
        token_id       = invoiceID,
        Userlogin      = request.user.username,
    )
    create_receivable.save(using=db)


PAYMENT_DEBIT_PREFIXES = ("Payment Received", "Discount Allowed")


def spurious_payment_debit_qs(db):
    """Debits posted at payment/discount time — they must not live on the AR ledger."""
    lookup = Q()
    for prefix in PAYMENT_DEBIT_PREFIXES:
        lookup |= Q(description__startswith=prefix)
    return receivable.objects.using(db).filter(type="Debit").filter(lookup)


def recompute_receivable_running_balances(db, customer_ids=None):
    """Rewrite each remaining row's initial_amount/balance from a Debit+/Credit- walk."""
    if customer_ids is None:
        customer_ids = (
            receivable.objects.using(db)
            .values_list('customer_id', flat=True)
            .distinct()
        )

    updated = 0
    for customer_id in customer_ids:
        rows = list(
            receivable.objects.using(db)
            .filter(customer_id=customer_id)
            .order_by('date', 'id')
        )
        running = Decimal('0.00')
        for row in rows:
            amount = Decimal(str(row.amount or 0))
            initial = running
            if row.type == "Debit":
                running += amount
            else:
                running -= amount
            if row.initial_amount != initial or row.balance != running:
                row.initial_amount = initial
                row.balance = running
                row.save(using=db, update_fields=['initial_amount', 'balance'])
                updated += 1
    return updated


def repair_spurious_payment_debits(db, dry_run=False):
    """One-time repair: drop payment-echo Debits, then recompute every customer's running balance.

    Matching is description-based only (Payment Received / Discount Allowed Debits).
    Credits are kept. Does not run from a GET view.
    """
    junk = spurious_payment_debit_qs(db).order_by('date', 'id')
    preview = list(junk.values(
        'id', 'date', 'customer_id', 'customer_name', 'token_id',
        'description', 'amount', 'balance',
    ))
    delete_count = len(preview)

    if dry_run:
        return {
            'deleted': 0,
            'would_delete': delete_count,
            'recomputed': 0,
            'rows': preview,
        }

    with transaction.atomic(using=db):
        if delete_count:
            junk.delete()
        recomputed = recompute_receivable_running_balances(db)

    return {
        'deleted': delete_count,
        'would_delete': delete_count,
        'recomputed': recomputed,
        'rows': preview,
    }


def ReduceOutletStockinItemQuantity(db, outlet, itemcode, qty):
   
    stock = CreateOutletStockIn.objects.using(db).filter(outlet=outlet, item_code=itemcode).first()
    
    if stock is None:
        try:
            stock = CreateOutletStockIn.objects.using(db).get(item_code=itemcode).first()
            new_qty = decimal.Decimal(stock.quantity) -  decimal.Decimal(qty)
            stock.quantity = new_qty
            stock.save()
        except CreateOutletStockIn.DoesNotExist:
               pass
    else:
        new_qty = decimal.Decimal(stock.quantity) -  decimal.Decimal(qty)
        stock.quantity = new_qty
        stock.save()

    # StockinStatus(db, itemcode, qty)
    # CreatOutletStockinLog(stock, new_qty)


def CreateOutletStockinLog(db, datetx, invoice_no, order_no, supplier, warehouse, outlet, description, item, item_decription, item_qty, token_id, Userlogin, item_code, selling_price, wholesale_price):
    # Generate refrence number
    ref_no = "REF"+generate_order_id()
    
    CreateOutletStockInLog.objects.using(db).create(
                    datetx = datetx,
                    invoice_no = invoice_no,	
                    order_no = order_no,	
                    supplier = supplier,
                    warehouse = warehouse,
                    outlet = outlet,	
                    description = description,	
                    item = item,	
                    item_decription =item_decription,
                    quantity = item_qty,
                    token_id = token_id,	
                    Userlogin = Userlogin,	
                    item_code = item_code,	
                    ref_no = ref_no,	
                    selling_price = selling_price,
                    wholesale_price = wholesale_price,
                )
    

def StockinStatus(db,  itemcode, qty):
    items = CreateStockInLog.objects.using(db).filter(item_code=itemcode).order_by('id').exclude(status="Sold")[:qty]
    # CreateStockInLog.objects.using(db).filter(invoice_no=invoice_no, item_code=item_code).update(notification_status=status)

    items.update(status="Sold")



def IncreaseOutletStockinItemQuantity(db, outlet, itemcode, qty):
    stock = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode)
    new_qty = decimal.Decimal(stock.quantity) +  decimal.Decimal(qty)
    stock.quantity = new_qty
    stock.save()


def ReduceStockinItemQuantity(db, outlet, itemcode, qty):
    lookups = Q(outlet=outlet) | Q(warehouse=outlet)
    stock = CreateStockIn.objects.using(db).filter(lookups, item_code=itemcode).first()
    if stock is None:
        raise CreateStockIn.DoesNotExist(
            f"No CreateStockIn row found for warehouse/outlet={outlet}, item_code={itemcode}"
        )
    new_qty = decimal.Decimal(stock.quantity) - decimal.Decimal(str(qty))
    stock.quantity = new_qty
    stock.save(using=db)
    
from django.apps import apps
    
def CreateLog(db, account, total):
    model_name = account.series_name.title()+"_account"

     # Get the model dynamically
    AccountModel = apps.get_model(app_label='account', model_name=model_name)
    
 
    
    AccountModel.objects.using(db).create(
        account_id          = account.account_id,
        series_name         = account.series_name,
        account_bankname    = account.account_bankname,
        account_type        = account.account_type,
        amount              = total    
    )