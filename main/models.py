from django.db import models
from django.contrib.auth.models import AbstractUser, User

from django.utils import timezone

from .managers import CustomUserManager
from Stockin.models import company_table



import random
import string

 
def generate_unique_id(length=10):
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for i in range(length))
    return unique_id


class User(AbstractUser):
    email   = models.EmailField(
        max_length=150,
        unique=True,
        error_messages={
        "unique": "Your email must be unique"
        }
    )

    outlet   = models.CharField(max_length=250, blank=True)
    priviledge = models.CharField(max_length=250)
    company_id = models.ForeignKey(company_table,  on_delete=models.CASCADE, blank=True, null=True)
    Token_ID = models.CharField(max_length=12, default=generate_unique_id())
    Userlogin = models.CharField(max_length=250, blank=True)
    
    class Meta:
        db_table = "user"

    REQUIRED_FIELDS = ["email"]
    objects = CustomUserManager()

    def __str__(self):
        return self.username



class Privilege(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="privilege", null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    date_created = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "privilege"



class Pages(models.Model):
    page_name = models.CharField(max_length=255)
    token_id = models.CharField(max_length = 255, default=generate_unique_id())


    def __str__(self):
        return self.page_name
    
    class Meta:
        db_table = "pages"

class currency(models.Model):
    Country  = models.CharField(max_length=255)
    Currency = models.CharField(max_length = 255)
   
    class Meta:
        db_table = "Currency"


class states(models.Model):
    country  = models.ForeignKey(currency, on_delete=models.CASCADE)
    state = models.CharField(max_length = 255)
   
    class Meta:
        db_table = "States"


class Billing(models.Model):
    company  = models.ForeignKey(company_table, on_delete=models.CASCADE)
    country = models.CharField(max_length = 255)
    card_number = models.CharField(max_length = 255, default='0')
    month = models.CharField(max_length = 255)
    year = models.CharField(max_length = 255)
    code = models.CharField(max_length = 255, default='0')
    holders_name = models.CharField(max_length = 255)
    address = models.CharField(max_length = 255)
    plan = models.CharField(max_length = 255)
    subscription = models.CharField(max_length = 255)
    amount = models.DecimalField(decimal_places=2, max_digits=65, default=0.00)
    date   = models.DateTimeField(null=True)
    users = models.CharField(max_length = 255)
    reference = models.CharField(max_length = 255, blank=True)
    payment_status = models.CharField(max_length = 255)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)		
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        db_table = "Billing"


class SubHistory(models.Model):
    company  = models.ForeignKey(company_table, on_delete=models.CASCADE)
    plan = models.CharField(max_length = 255)
    subscription = models.CharField(max_length = 255)
    amount = models.DecimalField(decimal_places=2, max_digits=65, default=0.00)
    date   = models.DateTimeField()
    users = models.CharField(max_length = 255)
    payment_status = models.CharField(max_length = 255)
    reference = models.CharField(max_length = 255, blank=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)		
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        db_table = "SubHistory"
