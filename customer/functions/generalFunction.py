from customer.models import *  
import decimal, uuid
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog, CreateStockIn, CreateStockInLog
from django.db.models import Q



def CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total):

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
        initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
    else: 
        initial_bal = decimal.Decimal(0.00)
    
    if initial_bal > 0:
        balance = decimal.Decimal(initial_bal) - decimal.Decimal(total)
    else:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

    create_receivable = receivable(
        date=refund_date,
        description= Gdescription,
        type = "Credit",
        amount = total, 
        payment_method =p_method,
        invoice_status ="Unused",
        customer_id = cus.customer_code,
        customer_name = cus.name,
        initial_amount = initial_bal,
        balance = balance,
        account_posted = account, # default account
        transaction_id = transaction_id,
        Userlogin = request.user.username)
    create_receivable.save(using=db)


def DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total):

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
        initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
    else: 
        initial_bal = decimal.Decimal(0.00)
    
    if initial_bal > 0:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)
    else:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

    create_receivable = receivable(
        date=refund_date,
        description= Gdescription,
        type = "Debit",
        amount = total, 
        payment_method = p_method,
        invoice_status ="Unused",
        customer_id = cus.customer_code,
        customer_name = cus.name,
        initial_amount = initial_bal,
        balance = balance,
        account_posted = account, # default account
        transaction_id = transaction_id,
        Userlogin = request.user.username)
    create_receivable.save(using=db)



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
    new_qty = decimal.Decimal(stock.quantity) -  decimal.Decimal(qty)
    stock.quantity = new_qty
    stock.save()
    
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