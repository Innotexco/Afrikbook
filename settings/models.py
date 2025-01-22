from django.db import models
from .utils import generate_unique_id, generate_order_id
from main.models import User
from Stock.models import Item
from Stockin.models import company_table


# Create your models here.
class user_account(models.Model):
    username        = models.CharField(max_length=100)
    account         = models.CharField(max_length=250)
    outlet          = models.CharField(max_length=250)
    Userlogin       = models.CharField(max_length=250)
    account_type    = models.CharField(max_length=100)
    token_ID        = models.CharField(max_length=12, default=generate_unique_id())

    class Meta:
        db_table = "user_account"

class pricechange_history(models.Model):
    category = models.CharField(max_length=233)	
    productname	= models.CharField(max_length=233)	
    purchaseprice  = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)	
    initial_price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)	
    new_sellingprice = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)	
    updated_date = models.DateField(auto_now=True)	

    class Meta:
        db_table = "pricechange_history"

# class user(models.Model):
#     username = models.CharField(max_length=233)	
#     password = models.CharField(max_length=233)	
#     outlet  = models.CharField(max_length=60, blank=True)	
#     priviledge = models.CharField(max_length=60, blank=True)	
#     Userlogin = models.CharField(max_length=50, blank=True)	

#     class Meta:
#        db_table = "user"


class sales_outlet(models.Model):	
    outlet_name	 = models.CharField(max_length=233, unique=True)	
    phone	 = models.CharField(max_length=233)	
    address	 = models.CharField(max_length=233)	
    country	 = models.CharField(max_length=233)	
    currency= models.CharField(max_length=233, blank=True)	
    Userlogin = models.CharField(max_length=50, blank=True)	

    class Meta:
        db_table = "sales_outlet"

# class profile(models.Model):
#     ownerName = models.CharField(max_length=222)
#     phone = models.CharField(max_length=50)
#     phone2 = models.CharField(max_length=50, blank=True)
#     email = models.EmailField(max_length=225)
#     Rc = models.CharField(max_length=225, blank=True)
#     CompanyName = models.CharField(max_length=225)
#     services = models.CharField(max_length=233)
#     address = models.CharField(max_length=333)
#     country = models.CharField(max_length=222, blank=True)
#     currency = models.CharField(max_length=222, blank=True)
#     logo = models.ImageField(upload_to='static/logo')
#     show_customer_info = models.CharField(max_length=233, blank=True)
#     Token_ID = models.CharField(max_length=233, blank=True)
#     vat = models.CharField(max_length=33, blank=True)
#     Userlogin = models.CharField(max_length=233, blank=True)

#     class Meta:
#             db_table = "profile"

class Warehouse(models.Model):
    warehouse_name        = models.CharField(max_length=255)
    description           = models.CharField(max_length=255)
    code                  = models.CharField(max_length=255, default=generate_order_id())
    token_id              = models.CharField(max_length=255, default=generate_unique_id())
    Userlogin             = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "warehouse"




import random
import os
from django.db import models

# Create your models here.

def get_filename_ext(filepath):
    base_name       = os.path.basename(filepath)
    name, ext       = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    # print(instance, 'instance')
    # print(filename, 'filename')
    new_filename    = random.randint(1, 90877789234)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "profiles/{final_filename}".format(final_filename=final_filename)

class CreateProfile(models.Model):
    ownerName           = models.CharField(max_length=250,  blank=True)
    phone               = models.CharField(max_length=250)
    phone2              = models.CharField(max_length=250,  blank=True)
    email               = models.CharField(max_length=250)
    Rc                  = models.CharField(max_length=250,  blank=True)
    CompanyName         = models.CharField(max_length=250)
    services            = models.TextField(max_length=250,  blank=True)
    address             = models.CharField(max_length=250)
    country             = models.CharField(max_length=255, null=True, blank=True)
    currency            = models.CharField(max_length=250, null=True, blank=True)
    logo                = models.ImageField(upload_to='profiles', null=True, blank=True)
    show_customer_info  = models.CharField(max_length=250, null=True, blank=True)  
    Token_ID            = models.CharField(max_length=250, null=True, blank=True)  
    vat                 = models.CharField(max_length=250, null=True, blank=True)  
    Userlogin           = models.CharField(max_length=200, null=True, blank=True)  
   
    class Meta:
        db_table = 'profile'  # Specify the table name



class SalesInterface(models.Model):
    name           = models.CharField(max_length=250, null=True, blank=True)
    business_type  = models.CharField(max_length=250, null=True, blank=True)
    token          = models.CharField(max_length=200, null=True, blank=True)
    Userlogin      = models.CharField(max_length=250, null=True, blank=True)
   
   
    class Meta:
        db_table = 'sale_interface'  # Specify the table name

class SetItemNotification(models.Model):
    item               = models.ForeignKey(Item, on_delete=models.CASCADE)
    notification_days  = models.IntegerField(default=0)
    Userlogin          = models.CharField(max_length=250, null=True, blank=True)
   
   
    class Meta:
        db_table = 'SetItemNotification'  # Specify the table name

class ExpiryDate(models.Model):
    invoice_no         = models.CharField(max_length=250, null=True, blank=True)
    item               = models.CharField(max_length=250, null=True, blank=True)
    item_code          = models.CharField(max_length=250, null=True, blank=True)
    manufacture_date   = models.DateField()
    expiry_date        = models.DateField()
    days               = models.CharField(max_length=250, null=True, blank=True)
    Userlogin          = models.CharField(max_length=250, null=True, blank=True)
   
   
    class Meta:
        db_table = 'ExpiryDate'  # Specify the table name



class company_details(models.Model):
    company            = models.ForeignKey(company_table, on_delete=models.CASCADE)
    type               = models.CharField(max_length=50, unique=True)
    detail             = models.CharField(max_length=250)
    Userlogin          = models.CharField(max_length=250)


    class Meta:
        db_table = 'Company_details'


class  shipping_method(models.Model):
    method  = models.CharField(max_length=256)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'shipping_method'

class  pickupstation(models.Model):
    addr = models.CharField(max_length=256)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'pickupstation'

class  city(models.Model):
    country = models.CharField(max_length=256)
    city = models.CharField(max_length=256)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'city'
        
class  pickUpShippingPrice(models.Model):
    location = models.ForeignKey(pickupstation, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=256)
    generated_code = models.CharField(max_length=256)
    cost = models.DecimalField(max_digits=65, decimal_places=2, default=0.0)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'pickUpshippingprice'

class  addressShippingPrice(models.Model):
    country = models.CharField(max_length=256)
    city = models.CharField(max_length=256, default="none")
    item_name = models.CharField(max_length=256, default="none")
    generated_code = models.CharField(max_length=256, default="none")
    cost = models.DecimalField(max_digits=65, decimal_places=2, default=0.0)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'addressshippingprice'

class  shipping_cost(models.Model):
    invoiceID = models.CharField(max_length=256, default='none')
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=0.0)
    custID = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)		
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'shipping_cost' 
        


