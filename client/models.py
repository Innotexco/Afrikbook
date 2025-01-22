from django.db import models
from main .models import User
# Create your models here.


class shipping_addr(models.Model):
    addr_id        = models.ForeignKey(User, on_delete=models.CASCADE)
    city           = models.CharField(max_length=250)
    state          = models.CharField(max_length=250)
    country        = models.CharField(max_length=250)
    address        = models.CharField(max_length=250)


    class Meta:
        db_table = 'shipping_addr'





class client_companies(models.Model):
    company_id      = models.CharField(max_length=256)
    company_name    = models.CharField(max_length=256)
    company_db      =  models.CharField(max_length=256)
    company_db_pass =  models.CharField(max_length=256, blank=True)
    company_db_user =  models.CharField(max_length=256)
    client_id       =  models.ForeignKey (User, on_delete=models.CASCADE)
    address         = models.CharField(max_length=256, default="none")
    phone           = models.CharField(max_length=256, default="none")
    email           = models.CharField(max_length=256, default="none")
    created_at      = models.DateTimeField(auto_now_add=True)		
    updated_at      = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = 'client_companies'