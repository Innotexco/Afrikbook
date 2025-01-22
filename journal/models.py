from django.db import models

# Create your models here.

class new_journal_entry(models.Model):
    date               = models.DateField()
    invoice_no         = models.CharField(max_length=200)	
    order_no           = models.CharField(max_length=200, blank=True)	
    account            = models.CharField(max_length=200)	
    vendor_name        = models.CharField(max_length=200)	
    category           = models.CharField(max_length=200)	
    narration          = models.CharField(max_length=200)	
    item               = models.CharField(max_length=200)	
    description        = models.CharField(max_length=255)	
    debit              = models.CharField(max_length=200, blank=True)	
    credit             = models.CharField(max_length=200, blank=True)	
    total              = models.CharField(max_length=200)	
    transaction_type   = models.CharField(max_length=200)	
    token_ID           = models.CharField(max_length=200, blank=True)	
    Userlogin          = models.CharField(max_length=60, blank=True)


    class Meta:
        db_table = "new_journal_entry"

class journal_entry_bin(models.Model):
    date               = models.DateField()
    invoice_no         = models.CharField(max_length=200)	
    order_no           = models.CharField(max_length=200, blank=True)	
    account            = models.CharField(max_length=200)	
    vendor_name        = models.CharField(max_length=200)	
    category           = models.CharField(max_length=200)	
    narration          = models.CharField(max_length=200)	
    item               = models.CharField(max_length=200)	
    description        = models.CharField(max_length=255)	
    debit              = models.CharField(max_length=200, blank=True)	
    credit             = models.CharField(max_length=200, blank=True)	
    total              = models.CharField(max_length=200)	
    transaction_type   = models.CharField(max_length=200)	
    created_at         = models.DateTimeField(auto_now_add=True)
    status             = models.CharField(max_length=50)	
    Userlogin          = models.CharField(max_length=60, blank=True)


    class Meta:
        db_table = "journal_entry_bin"

class new_journal_entry_log(models.Model):
    date          = models.DateField()
    invoice_no    = models.CharField(max_length=200)	
    order_no      = models.CharField(max_length=200)	
    account       = models.CharField(max_length=200)	
    vendor_name   = models.CharField(max_length=200)	
    category      = models.CharField(max_length=200)	
    narration     = models.CharField(max_length=200)	
    item          = models.CharField(max_length=200)	
    description   = models.CharField(max_length=255)	
    debit         = models.CharField(max_length=200)	
    credit        = models.CharField(max_length=200)	
    total_debit   = models.CharField(max_length=200)	
    total_credit  = models.CharField(max_length=200)	
    token_ID      = models.CharField(max_length=200)	
    Userlogin     = models.CharField(max_length=60)

    
    class Meta:
        db_table = "new_journal_entry_log"

class new_journal_entry_profit(models.Model):
    date           = models.DateField()
    invoice_no     = models.CharField(max_length=200)	
    order_no       = models.CharField(max_length=200)	
    account        = models.CharField(max_length=200)	
    vendor_name    = models.CharField(max_length=200)	
    category       = models.CharField(max_length=200)	
    narration      = models.CharField(max_length=200)	
    item           = models.CharField(max_length=200)	
    description    = models.CharField(max_length=255)	
    amount         = models.CharField(max_length=200)	
    total          = models.CharField(max_length=200)	
    # debit = models.CharField(max_length=200)	
    # credit = models.CharField(max_length=200)	
    # total_debit = models.CharField(max_length=200)	
    # total_credit = models.CharField(max_length=200)	
    token_ID = models.CharField(max_length=200)	
    class Meta:
        db_table = "new_journal_entry_profit"

class new_journal_entry_profit_log(models.Model):
    date = models.DateField()
    invoice_no = models.CharField(max_length=200)	
    order_no = models.CharField(max_length=200)	
    account = models.CharField(max_length=200)	
    vendor_name = models.CharField(max_length=200)	
    category = models.CharField(max_length=200)	
    narration = models.CharField(max_length=200)	
    item = models.CharField(max_length=200)	
    description = models.CharField(max_length=255)	
    amount = models.CharField(max_length=200)	
    total = models.CharField(max_length=200)	
    debit = models.CharField(max_length=200)	
    credit = models.CharField(max_length=200)	
    total_debit = models.CharField(max_length=200)	
    total_credit = models.CharField(max_length=200)	
    token_ID = models.CharField(max_length=200)	
    class Meta:
        db_table = "new_journal_entry_profit_log"


class loan_account(models.Model):
    date = models.DateField()
    debtor_name	= models.CharField(max_length=200)
    debtor_id	= models.CharField(max_length=60)
    description	= models.CharField(max_length=223)
    amount_borrowed	= models.CharField(max_length=200)
    amount_paid	= models.CharField(max_length=200)
    balance_left	= models.CharField(max_length=200)
    account_debited	= models.CharField(max_length=200)
    status	= models.CharField(max_length=200, blank=True, default="unpaid")
    token_ID	= models.CharField(max_length=200, blank=True)
    transaction_id = models.CharField(editable=False, max_length=200)
    Userlogin	= models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = "loan_account"


class loan_account_log(models.Model):
    date = models.DateField()
    debtor_name	= models.CharField(max_length=200)
    debtor_id	= models.CharField(max_length=60)
    description	= models.CharField(max_length=223)
    amount_borrowed	= models.CharField(max_length=200)
    amount_paid	= models.CharField(max_length=200)
    balance_left	= models.CharField(max_length=200)
    account_debited	= models.CharField(max_length=200)
    status	= models.CharField(max_length=200, blank=True, default="unpaid")
    token_ID	= models.CharField(max_length=200, blank=True)
    transaction_id = models.CharField(editable=False, max_length=200)
    Userlogin	= models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = "loan_account_log"

    
