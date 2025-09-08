from django.db import models

from .managers import CustomVendorManager

from vendor.utils import generate_customer_id, generate_unique_id, generate_order_id


class Vendor_invoice(models.Model):
    cusID               = models.CharField(max_length = 25, default=generate_customer_id, blank=True)
    vendor_name         = models.CharField(max_length=255)
    invoiceID           = models.CharField(max_length = 255)
    orderID             = models.CharField(max_length = 255, blank=True, null=True)
    Gdescription        = models.TextField(blank="True", null="True")
    invoice_date        = models.DateTimeField()
    due_date            = models.DateField(max_length=250, auto_now_add=True)
    itemcode            = models.CharField(max_length = 255)
    item_name           = models.CharField(max_length = 255)
    item_descriptions   = models.CharField(max_length = 255, blank=True)
    qty                 = models.IntegerField(default=0.00)
    unit_p              = models.CharField(max_length = 255)
    discount_price      = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, blank=True)
    amount              = models.DecimalField(max_digits=65, decimal_places=2, default=0.00)
    token_id            = models.CharField(max_length = 255, default=generate_unique_id, blank=True)
    amount_paid         = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, blank=True)
    amount_expected     = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, blank=True)
    cancellation        = models.IntegerField(default=0, blank=True)
    Userlogin           = models.CharField(max_length=255, null="True", blank="True")

    class Meta:
        db_table = "vendor_invoice"




class Vendor_Quote(models.Model):
    genby               = models.CharField(max_length = 255)
    quote_ID            = models.CharField(max_length = 255, default=generate_order_id, blank=True, null=True)
    referenceID         = models.CharField(max_length = 255, blank=True, null=True)
    Gdescription        = models.TextField()
    quote_date          = models.DateField(max_length=250, auto_now_add=True)
    itemcode            = models.CharField(max_length = 255, blank=True, null=True)
    item_name           = models.CharField(max_length = 255, blank=True, null=True)
    item_descriptions   = models.CharField(max_length = 255, blank=True, null=True)
    qty                 = models.IntegerField( blank=True, null=True)	
    unit_p              = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    discount            = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    amount              = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    total               = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    token_id            = models.CharField(max_length = 25, default=generate_customer_id, blank=True, null=True)
    custID              = models.CharField(max_length = 25, default=generate_unique_id, blank=True, null=True)
    Userlogin           = models.CharField(max_length = 255, blank=True, null=True)

    class Meta:
        db_table = "vendor_quote"


class Vendor_Order(models.Model):
    genby               = models.CharField(max_length = 255)
    order_ID            = models.CharField(max_length = 25, default=generate_order_id, blank=True, null=True)
    referenceID         = models.CharField(max_length = 255, blank=True, null=True)
    Gdescription        = models.TextField()
    order_date          = models.DateField(max_length=250, auto_now_add=True)
    itemcode            = models.CharField(max_length = 255, blank=True, null=True)
    item_name           = models.CharField(max_length = 255, blank=True, null=True)
    item_description    = models.CharField(max_length = 255)
    qty                 = models.IntegerField( blank=True, null=True)	
    unit_p              = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    discount            = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    amount              = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    total               = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    token_id            = models.CharField(max_length = 25, default=generate_customer_id, blank=True, null=True)
    custID              = models.CharField(max_length = 25, default=generate_unique_id, blank=True, null=True)

    class Meta:
        db_table = "vendor_order"


class Vendor_Return(models.Model):
    genby               = models.CharField(max_length = 255, blank=True)
    cusID               = models.CharField(max_length = 255, blank=True, default=generate_unique_id)
    invoiceID           = models.CharField(max_length = 255, blank=True)
    reference_ID        = models.CharField(max_length = 255, blank=True, null=True)
    Gdescription        = models.TextField(blank=True)
    refund_date         = models.DateField(max_length=250, auto_now_add=True)
    itemcode            = models.CharField(max_length = 255, blank=True)
    item_name           = models.CharField(max_length = 255, blank=True)
    item_description    = models.CharField(max_length = 255, blank=True)
    qty                 = models.IntegerField( blank=True, null=True)	
    unit_p              = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    discount            = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    amount              = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    token_id            = models.CharField(max_length = 25, default=generate_customer_id, blank=True, null=True)
    amount_paid         = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)
    amount_expected     = models.DecimalField(decimal_places=2, max_digits=62, blank=True, null=True)	
    cur_date            = models.DateField(max_length=250, auto_now_add=True)
    Userlogin           = models.CharField(max_length=100, default="Admin", blank=True, null=True)


    class Meta:
        db_table = "vendor_return"


class vendor_table(models.Model):
    name            = models.CharField(max_length=100)
    phone           = models.CharField(max_length=50)
    email   = models.EmailField(
        max_length=150,
        blank=True,
        unique=True,
        error_messages={
        "unique": "Your email must be unique"
        }
    )
    address         = models.CharField(max_length=255, blank=True)
    company_name    = models.CharField(max_length=255, blank=True)
    token_id        = models.CharField(max_length=255, blank=True)
    custID          = models.CharField(max_length=255, blank=True)
    invoices        = models.IntegerField(null=True, default=1, blank=True)
    account_payable = models.CharField(max_length=255, null=True, default=0, blank=True)
    vate_rate       = models.CharField(max_length=255, null=True, default=1, blank=True)
    refundInvoice   = models.IntegerField(null=True, default=0, blank=True)
    Userlogin       = models.CharField(max_length=255, null=True, default=1, blank=True)
    
    class Meta:
        db_table = "vendor_table"

    # REQUIRED_FIELDS = ["email"]
    objects = CustomVendorManager()

    def __str__(self):
        return self.name
    

    # Generate customer ID
    def save(self, *args, **kwargs):
        if self.custID == "":
            self.custID = generate_customer_id()
        return super().save(*args, **kwargs)







