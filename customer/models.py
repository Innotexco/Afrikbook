from django.db import models
from .utils import *
from main.models import User

# Create your models here.
CATEGORY_CHOICES = (
    ('Whole Sale', 'Whole Sale'),
    ('Retail', 'Retail')
)

TRANSACTION_TYPE = (
    ('Credit', 'Credit'),
    ('Debit', 'Debit')
)
OPERATING_ACCOUNT = (
    ('Uba', 'Uba'),
    ('Fidelity', 'Fidelity')
)

class customer_table(models.Model):
    name           = models.CharField(max_length=100)
    customer_code  = models.CharField(max_length=50, unique=True)
    phone          = models.CharField(max_length=100, unique=True)
    instant_email  = models.CharField(max_length=10, default=1)
    email          = models.EmailField(max_length=100, blank=True)
    token_id       = models.IntegerField( blank=True, null=True)
    Balance        = models.DecimalField(decimal_places=2, max_digits=65, default=0.00)
    invoice        = models.IntegerField(blank=True, default=0)
    company_name   = models.CharField(max_length=100)
    category       = models.CharField(max_length=20, choices = CATEGORY_CHOICES, default='RETAIL')
    refund_invoice = models.IntegerField( blank=True, default=0)
    Userlogin      = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        db_table = "customer_table"

    # Generate customer code
    def save(self, *args, **kwargs):
        if self.customer_code == "":
            self.customer_code = generate_customer_id()
        return super().save(*args, **kwargs)
    





class sales_quote(models.Model):
    genby            = models.CharField(max_length=20)
    quote_ID         = models.CharField(max_length=50, default=generate_order_id, blank=True, null=True)	
    referenceID      = models.CharField(max_length=50, blank=True, null=True)
    Gdescription     = models.CharField(max_length=225, blank=True, null=True)	
    quote_date       = models.DateField()
    itemcode         = models.CharField(max_length=50, blank=True, null=True)	
    item_name        = models.CharField(max_length=200, blank=True, null=True)	
    item_description = models.CharField(max_length=225, blank=True, null=True)	
    qty              = models.IntegerField( blank=True, null=True)	
    unit_p           = models.DecimalField(decimal_places=2, max_digits=60, blank=True, null=True)	
    discount         = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)	
    amount           = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)	
    total            = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)	
    token_id         = models.CharField(max_length=50, blank=True, null=True)	
    custID           = models.CharField(max_length=50, blank=True, null=True)	
    Userlogin        = models.CharField(max_length=60, blank=True, null=True)	

    class Meta:
        db_table = "sales_qoute"


class sales_order(models.Model):
    genby            = models.CharField(max_length=20)
    order_ID         = models.CharField(max_length=50, default=generate_order_id, blank=True, null=True)	
    referenceID      = models.CharField(max_length=50,blank=True, null=True)
    Gdescription     = models.CharField(max_length=225, blank=True, null=True)	
    order_date       = models.DateField()
    itemcode         = models.CharField(max_length=50)	
    item_name        = models.CharField(max_length=200, blank=True, null=True)	
    item_description = models.CharField(max_length=225, blank=True, null=True)	
    qty              = models.IntegerField( blank=True, null=True)	
    unit_p           = models.DecimalField(decimal_places=2, max_digits=12)	
    discount         = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)	
    amount           = models.DecimalField(decimal_places=2, max_digits=12)	
    total            = models.DecimalField(decimal_places=2, max_digits=12)	
    token_id         = models.CharField(max_length=50, blank=True, null=True)	
    custID           = models.CharField(max_length=50, blank=True, null=True)	
    Userlogin        = models.CharField(max_length=60, blank=True, null=True)	

    class Meta:
        db_table = "sales_order"


class customer_invoice(models.Model):
    cusID               = models.CharField(max_length=225)	
    customer_name       = models.CharField(max_length=225, blank=True, null=True)	
    invoiceID           = models.CharField(max_length=225, blank=True, null=True)	
    order_ID            = models.CharField(max_length=225, blank=True, null=True)	
    Gdescription        = models.CharField(max_length=225)	
    invoice_date        = models.DateTimeField()	
    due_date            = models.DateField()	
    itemcode            = models.CharField(max_length=50)	
    item_name           = models.CharField(max_length=200, blank=True, null=True)	
    item_description    = models.CharField(max_length=225, blank=True, null=True)	
    qty                 = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)	
    unit_p              = models.DecimalField(decimal_places=2, max_digits=12)	
    discount            = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)	
    amount              = models.DecimalField(decimal_places=2, max_digits=12)	
    token_id            = models.CharField(max_length=50, blank=True)	
    amount_paid	        = models.DecimalField(decimal_places=2, max_digits=12)
    amount_expected	    = models.DecimalField(decimal_places=2, max_digits=12)
    cancellation_status = models.CharField(max_length=50, default="0")	
    status              = models.CharField(max_length=50, default="0")	
    Userlogin           = models.CharField(max_length=50, blank=True)	
    payment_method      = models.CharField(max_length=50, blank=True)	
    Transfer            = models.CharField(max_length=50, default="0")	
    POS                 = models.CharField(max_length=50, default="0")	
    Cash                = models.CharField(max_length=50, default="0")	
    Customer_account    = models.CharField(max_length=50, default="0")	
    Cheque              = models.CharField(max_length=50, default="0")		
    invoice_state       = models.CharField(max_length=50)		
    purchaseP           = models.DecimalField(decimal_places=2, max_digits=12)	
    total_purchaseP     = models.DecimalField(decimal_places=2, max_digits=12)	
    outlet              = models.CharField(max_length=50, blank=False)	

    class Meta:
        db_table = "customer_invoice"

class Vat(models.Model):
    source = models.CharField(max_length=255)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    created_at     = models.DateTimeField(auto_now_add=True)		
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vat"

class receivable(models.Model):	
    date           = models.DateField()	
    description	   = models.CharField(max_length=255)
    type           = models.CharField(max_length=50)	
    amount         = models.DecimalField(decimal_places=2, max_digits=64, )		
    initial_amount = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)		
    balance        = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)		
    customer_id	   = models.CharField(max_length=50, blank=True)
    customer_name  = models.CharField(max_length=60, blank=True)	
    payment_method = models.CharField(max_length=50)	
    cur_datetime   = models.DateTimeField(auto_now_add=True)	
    account_posted = models.CharField(max_length=50, blank=True)	
    transaction_id = models.CharField(max_length=50, blank=True)	
    token_id       = models.CharField(max_length=50, blank=True)	
    Userlogin      = models.CharField(max_length=50, blank=True)	
    invoice_status = models.CharField(max_length=200)

    class Meta:
        db_table = "receivable"


class payable(models.Model):	
    date               = models.DateField(max_length=222, auto_now_add=True)	
    description        = models.CharField(max_length=255)
    type               = models.CharField(max_length=50)	
    amount             = models.DecimalField(decimal_places=2, max_digits=64, blank=True, default=0.00)		
    initial_amount     = models.DecimalField(decimal_places=2, max_digits=64, blank=True, default=0.00)		
    balance            = models.DecimalField(decimal_places=2, max_digits=64, blank=True, default=0.00)		
    vendor_id	       = models.CharField(max_length=50, blank=True)
    vendor_name        = models.CharField(max_length=60, blank=True)	
    payment_method     = models.CharField(max_length=50)	
    cur_datetime       = models.DateTimeField(auto_now_add=True)	
    account_posted     = models.CharField(max_length=50, blank=True)	
    transaction_id     = models.CharField(max_length=50, blank=True)	
    transaction_source = models.CharField(max_length=200, default=0, blank=True)
    token_id           = models.CharField(max_length=50, blank=True)	
    Userlogin          = models.CharField(max_length=50, blank=True)	

    class Meta:
        db_table = "payable"


class sales_return(models.Model):
    genby            = models.CharField(max_length=200)	
    cusID            = models.CharField(max_length=200)	
    invoiceID        = models.CharField(max_length=255)	
    refrence_ID      = models.CharField(max_length=255)	
    Gdescription     = models.CharField(max_length=255)	
    refund_date   	 = models.DateField(max_length=222, auto_now_add=True)
    itemcode         = models.CharField(max_length=255)	
    item_name        = models.CharField(max_length=255)	
    item_description = models.CharField(max_length=255)	
    qty              = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)	
    unit_p           = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)	
    discount         = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)	
    amount           = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)	
    token_id         = models.CharField(max_length=255, blank=True)	
    amount_paid      = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)	
    amount_expected  = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)	
    cur_date         = models.DateTimeField(auto_now_add=True)	
    Userlogin        = models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = "sales_return"


class customer_incentive(models.Model):	
    customer_id    = models.CharField(max_length=255)	
    customer_name  = models.CharField(max_length=255)	
    description    = models.CharField(max_length=255)	
    amount         = models.DecimalField(decimal_places=2, max_digits=64)	
    initial_amount = models.DecimalField(decimal_places=2, max_digits=64)	
    balance        = models.DecimalField(decimal_places=2, max_digits=64, default=0.00, blank=True)	
    type           = models.CharField(max_length=255, default="Credit")
    date           = models.DateField()	
    token_id       = models.CharField(max_length=255, blank=True)	

    class Meta:
        db_table = "customer_incentive"

    def save(self,*args, **kwargs):
        if self.balance is None:
            self.balance = self.initial_amount - self.amount
        return super().save(*args, **kwargs)



class evidentPayment(models.Model):	
    client_ref     = models.CharField(max_length=255)	
    amount         = models.DecimalField(decimal_places=2, max_digits=64)	
    file           = models.ImageField(null=True, blank=True, upload_to="payment_proov/", max_length=255)	
    description    = models.CharField(max_length=255)		
    state           = models.CharField(max_length=255)
    created_at     = models.DateTimeField(auto_now_add=True)		
    updated_at     = models.DateTimeField(auto_now=True)		

    class Meta:
        db_table = "evidentPayment"



    	



class  deposit_transfer(models.Model):
    cusID = models.CharField(max_length=256)
    customer_name = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=0.0)
    prove = models.CharField(max_length=256, default='none')
    created_at     = models.DateTimeField(auto_now_add=True)		
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deposit_transfer'


class  order_invoice_reference_address(models.Model):
    source = models.CharField(max_length=256)
    reference = models.CharField(max_length=256)
    shipping_addr = models.IntegerField()
    created_at     = models.DateTimeField(auto_now_add=True)		
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_invoice_reference_address'

class  order_invoice_billing_address(models.Model):
    source = models.CharField(max_length=256)
    reference = models.CharField(max_length=256)
    billing_addr = models.IntegerField()
    created_at     = models.DateTimeField(auto_now_add=True)		
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_invoice_billing_address'

# class  remark(models.Model):
#     source = models.CharField(max_length=256)
#     text = models.TextField()
#     created_at = models.DateTimeField(default=default_date)
#     updated_at = models.DateTimeField(default=default_date)

#     class Meta:
#         db_table = 'remark'
        

class billing_addr(models.Model):
    addr_id       = models.ForeignKey(customer_table, on_delete=models.CASCADE)
    city           = models.CharField(max_length=250)
    state          = models.CharField(max_length=250)
    country        = models.CharField(max_length=250)
    address        = models.CharField(max_length=250)


    class Meta:
        db_table = 'billing_addr'


