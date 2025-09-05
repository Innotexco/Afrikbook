from django.db import models


from .utils import generate_unique_id, generate_token_id, generate_order_id
from django.utils import timezone


class Payment_method(models.Model):
    method  = models.CharField(max_length=255)

    class Meta:
        db_table = "payment_method"


class transfer_account(models.Model):
    date_tx         = models.DateTimeField(auto_now_add=False)
    description     = models.CharField(max_length=255)
    paid_from       = models.CharField(max_length=255)
    amount          = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    received_in     = models.CharField(max_length=255)
    token_id        = models.CharField(max_length=12, default=generate_unique_id, blank=True)
    user            = models.CharField(max_length=255, blank=True, null=True)
    status          = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "transfer_account"



class chart_of_account(models.Model):
    account_id          = models.CharField(max_length=255)
    series_name         = models.CharField(max_length = 255)
    account_type        = models.CharField(max_length=255)
    account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
    status              = models.CharField(max_length=255, default="Inactive")
    code                = models.CharField(max_length=255, null=True, blank=True)
    credit_limit        = models.CharField(max_length=255, null=True, blank=True)
    token_id            = models.CharField(max_length=255, default=generate_unique_id)
    actual_balance      = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    cleared_bal         = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    pending_deposit     = models.CharField(max_length=255, null=True, blank=True)
    pending_withdrawal  = models.CharField(max_length=255, null=True, blank=True)
    availablr_credit    = models.CharField(max_length=255, null=True, blank=True)
    Userlogin           = models.CharField(max_length=255, blank="True", null="True")
    created_at = models.DateTimeField(auto_now_add=True)		
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "chart_of_account"




# class OLDaccounts(models.Model):
#     account_series      = models.CharField(max_length = 255)
#     series_name         = models.CharField(max_length = 255, null=True, blank=True)
#     description         = models.CharField(max_length = 255, null=True, blank=True)
#     account_type        = models.CharField(max_length=255)
#     status              = models.CharField(max_length=255, default="Inactive")
#     Token_ID            = models.CharField(max_length=255, default=generate_unique_id())
#     Userlogin           = models.CharField(max_length=255, null=True, blank=True)

#     class Meta:
#         db_table = "accounts"

class accounts(models.Model):
    account_series      = models.CharField(max_length = 255)
    series_name         = models.CharField(max_length = 255, null=True, blank=True)
    description         = models.CharField(max_length = 255, null=True, blank=True)
    account_type        = models.CharField(max_length=255)
    status              = models.CharField(max_length=255, default="Inactive")
    Userlogin           = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "accounts"













#====== ALL ACCOUNT LOG ======

class account_log(models.Model):
    transactionId       = models.CharField(max_length = 255, default=generate_unique_id)
    transaction_source  = models.CharField(max_length = 255, default="INTER ACCOUNT TRANSFER")
    amount              = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    date                = models.DateField(auto_now_add=True)
    timestamp           = models.TimeField(auto_now_add=True)
    token_id            = models.CharField(max_length=255, default=generate_token_id)
    account             = models.CharField(max_length=255)
    account_type        = models.CharField(max_length=255, default="Cash")
    dateTimeSt          = models.DateTimeField(auto_now_add=True)
    cancellation_status = models.CharField(max_length=255, default=0)
    Userlogin           = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "account_log"
        
        

# class OLDACCOUNTSETUP(models.Model):
#     account_id          = models.CharField(max_length=255)
#     series_name         = models.CharField(max_length = 255)
#     account_type        = models.CharField(max_length=255)
#     account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
#     status              = models.CharField(max_length=255, default="Inactive")
#     code                = models.CharField(max_length=255, null=True, blank=True)
#     credit_limit        = models.CharField(max_length=255, null=True, blank=True)
#     token_id            = models.CharField(max_length=255, default=generate_unique_id())
#     actual_balance      = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
#     cleared_bal         = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
#     pending_deposit     = models.CharField(max_length=255, null=True, blank=True)
#     pending_withdrawal  = models.CharField(max_length=255, null=True, blank=True)
#     availablr_credit    = models.CharField(max_length=255, null=True, blank=True)
#     Userlogin           = models.CharField(max_length=255, blank="True", null="True")


class Assets_account(models.Model):
    account_id          = models.CharField(max_length=255)
    amount              = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    series_name         = models.CharField(max_length = 255)
    account_type        = models.CharField(max_length=255)
    account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
    status              = models.CharField(max_length=255, default="Inactive")
    canclelation_status = models.CharField(max_length=255, default="Inactive")
    date                = models.DateField(default=timezone.now)
    update_date         = models.DateField(default=timezone.now)
    Userlogin           = models.CharField(max_length=255, blank="True", null="True")
    created_at          = models.DateTimeField(auto_now_add=True)		
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "assets_account"
        
class Expenses_account(models.Model):
    account_id          = models.CharField(max_length=255)
    amount              = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    series_name         = models.CharField(max_length = 255)
    account_type        = models.CharField(max_length=255)
    account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
    status              = models.CharField(max_length=255, default="Inactive")
    canclelation_status = models.CharField(max_length=255, default="Inactive")
    date                = models.DateField(default=timezone.now)
    update_date         = models.DateField(default=timezone.now)
    Userlogin           = models.CharField(max_length=255, blank="True", null="True")
    created_at          = models.DateTimeField(auto_now_add=True)		
    updated_at          = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "expenses_account"
        
        
class Liability_account(models.Model):
    account_id          = models.CharField(max_length=255)
    amount              = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    series_name         = models.CharField(max_length = 255)
    account_type        = models.CharField(max_length=255)
    account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
    status              = models.CharField(max_length=255, default="Inactive")
    canclelation_status = models.CharField(max_length=255, default="Inactive")
    date                = models.DateField(default=timezone.now)
    update_date         = models.DateField(default=timezone.now)
    Userlogin           = models.CharField(max_length=255, blank="True", null="True")
    created_at          = models.DateTimeField(auto_now_add=True)		
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "liability_account"
        
class Equity_account(models.Model):
    account_id          = models.CharField(max_length=255)
    amount              = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    series_name         = models.CharField(max_length = 255)
    account_type        = models.CharField(max_length=255)
    account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
    status              = models.CharField(max_length=255, default="Inactive")
    canclelation_status = models.CharField(max_length=255, default="Inactive")
    date                = models.DateField(default=timezone.now)
    update_date         = models.DateField(default=timezone.now)
    Userlogin           = models.CharField(max_length=255, blank="True", null="True")
    created_at          = models.DateTimeField(auto_now_add=True)		
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "equity_account"
        
class Income_account(models.Model):
    account_id          = models.CharField(max_length=255)
    amount              = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    series_name         = models.CharField(max_length = 255)
    account_type        = models.CharField(max_length=255)
    account_bankname    = models.CharField(max_length = 255, null=True, blank=True)
    status              = models.CharField(max_length=255, default="Inactive")
    canclelation_status = models.CharField(max_length=255, default="Inactive")
    date                = models.DateField(default=timezone.now)
    update_date         = models.DateField(default=timezone.now)
    Userlogin           = models.CharField(max_length=255, blank="True", null="True")
    created_at          = models.DateTimeField(auto_now_add=True)		
    updated_at          = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "income_account"



