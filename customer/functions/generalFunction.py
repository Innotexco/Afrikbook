from customer.models import *  
import decimal, uuid
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog, CreateStockIn, CreateStockInLog
from django.db.models import Q



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
    
    

def DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total, invoiceID=None):
    transaction_id = uuid.uuid4()

    if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
        initial_bal = receivable.objects.using(db).filter(
            customer_id=cus.customer_code
        ).last().balance
    else:
        initial_bal = decimal.Decimal('0.00')

    balance = decimal.Decimal(str(initial_bal)) + decimal.Decimal(str(total))

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


from decimal import Decimal

def CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account, amount_paid_now, invoiceID, invoice_total, current_paid_before):
    transaction_id = uuid.uuid4()

    new_total_paid = current_paid_before + Decimal(str(amount_paid_now))

    balance = Decimal(str(invoice_total)) - new_total_paid
    if balance < 0:
        balance = Decimal('0.00')

    create_receivable = receivable(
        date           = refund_date,
        description    = Gdescription,
        type           = "Credit",
        amount         = amount_paid_now,
        payment_method = p_method,
        invoice_status = "Unused",
        customer_id    = cus.customer_code,
        customer_name  = cus.name,
        initial_amount = invoice_total,
        balance        = balance,
        account_posted = account,
        transaction_id = transaction_id,
        token_id       = invoiceID,
        Userlogin      = request.user.username,
    )
    create_receivable.save(using=db)


def restore_extra_payment_debits(db):
    """Recreate Debit twins that remove_extra_payment_debits deleted.

    For each Credit, if there is no unused Debit with the same customer,
    invoice, description and amount, insert a Debit copied from that Credit.
    Safe to run more than once.
    """
    from collections import defaultdict

    credits = list(receivable.objects.using(db).filter(type="Credit").order_by("id"))
    if not credits:
        return 0

    debits = list(receivable.objects.using(db).filter(type="Debit").order_by("id"))

    used = set()
    by_key = defaultdict(list)
    has_debit_for = set()
    for debit in debits:
        token = debit.token_id or ""
        by_key[(debit.customer_id, token, debit.description or "")].append(debit)
        has_debit_for.add((debit.customer_id, token))

    to_create = []
    for credit in credits:
        token = credit.token_id or ""
        desc = credit.description or ""
        candidates = [
            debit for debit in by_key.get((credit.customer_id, token, desc), [])
            if debit.id not in used and Decimal(str(debit.amount)) == Decimal(str(credit.amount))
        ]
        if candidates:
            twin = next((d for d in candidates if d.date == credit.date), candidates[0])
            used.add(twin.id)
            continue

        is_payment_text = desc.startswith(("Payment Received", "Discount Allowed"))
        has_original_debit = (credit.customer_id, token) in has_debit_for
        if not (is_payment_text or has_original_debit):
            continue

        to_create.append(receivable(
            date=credit.date,
            description=credit.description,
            type="Debit",
            amount=credit.amount,
            payment_method=credit.payment_method,
            invoice_status=credit.invoice_status or "Unused",
            customer_id=credit.customer_id,
            customer_name=credit.customer_name,
            initial_amount=credit.amount,
            balance=Decimal('0.00'),
            account_posted=credit.account_posted,
            transaction_id=str(uuid.uuid4()),
            token_id=credit.token_id,
            Userlogin=credit.Userlogin,
        ))
        has_debit_for.add((credit.customer_id, token))

    if not to_create:
        return 0
    receivable.objects.using(db).bulk_create(to_create)
    return len(to_create)


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