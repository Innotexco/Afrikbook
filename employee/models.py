from django.db import models
from .utils import generate_staff_id

# Create your models here.
GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

MARITAL_STATUS = (
    ('Married', 'Married'),
    ('Single', 'Single'),
    ('Divorced', 'Divorced'),
    ('Widow/Widower', 'Widow/Widower'),
)
RELATIONSHIP = (
    ('Mother', 'Mother'),
    ('Father', 'Father'),
    ('Uncle', 'Uncle'),
    ('Aunty', 'Aunty'),
    ('Brother', 'Brother'),
    ('Sister', 'Sister'),
    ('Friend', 'Friend')
)
CATEGORY = (
    ('Full-time', 'Full-time'),
    ('Part-time', 'Part-time'),
    ('Contract', 'Contract'),
)


class employee(models.Model):
    fullname             = models.CharField(max_length=222)	
    email                = models.EmailField(max_length=225)	
    gender               = models.CharField(max_length=255, choices=GENDER)	
    date_of_birth        = models.DateField()	
    phone                = models.CharField(max_length=225)	
    marital_status	     = models.CharField(max_length=255, choices=MARITAL_STATUS)
    address              = models.CharField(max_length=222)
    staff_ID             = models.CharField(max_length=255, blank=True, unique=True)	
    basic_salary         = models.CharField(max_length=223)	
    job_title            = models.CharField(max_length=255)
    department           = models.CharField(max_length=255)
    category	         = models.CharField(max_length=255, choices=CATEGORY)
    supervisor           = models.CharField(max_length=222)	
    start_date           = models.DateField()	
    work_location        = models.CharField(max_length=222)	
    token_id             = models.CharField(max_length=222, blank=True, null=True)	
    Userlogin            = models.CharField(max_length=60, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.staff_ID:
            # Generate the ID only if it's not already set
            data = employee.objects.count()
            if data > 0:
               last_id = employee.objects.order_by('-staff_ID').values_list('staff_ID', flat=True).first()[4:]
            else:
                last_id = 0
            new_id = 1 if not last_id else int(last_id) + 1
            self.staff_ID = generate_staff_id()+'_'+f"{new_id:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff_ID}"
    
    class Meta:
        db_table = "employee"

class employee_account_details(models.Model):
    employee_id    = models.CharField(max_length=255)
    account_no     = models.CharField(max_length=222)	
    account_name   = models.CharField(max_length=222)	
    bank_name      = models.CharField(max_length=222)
    
    class Meta:
        db_table = "employee_account_details"



class employee_guarantor(models.Model):
    g_fullname           = models.CharField(max_length=222)	
    residential_address  = models.CharField(max_length=222)	
    work_address         = models.CharField(max_length=222)
    relationship	     = models.CharField(max_length=255, choices=RELATIONSHIP)
    g_phone              = models.CharField(max_length=225)	
    g_email              = models.EmailField(max_length=225)
    employee_id          = models.CharField(max_length=255)
    
    class Meta:
        db_table = "employee_guarantor"



class payroll(models.Model):
    month_year       = models.CharField(max_length=222)
    employee_name    = models.CharField(max_length=255)
    staffID          = models.CharField(max_length=200)
    bsaic_salary     = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    overtime         = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    allowance        = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    others           = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    gross_pay        = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    tax              = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    loan_repay       = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    union_pay        = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    sanction         = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    NHF              = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    NSIFT            = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    other_deduction  = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    total_due        = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    net_pay          = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    token_id         = models.CharField(max_length=200, blank=True, null=True)
    Userlogin        = models.CharField(max_length=60, blank=True, null=True)
    dateG            = models.DateField(auto_now_add=True)
    status           = models.CharField(max_length=60, default='unapprove')
    confirm_payment  = models.CharField(max_length=60, default='pending')

    class Meta:
        db_table = "payroll"

class payroll_log(models.Model):
    month_year       = models.CharField(max_length=225)
    Amount           = models.DecimalField(decimal_places=2, max_digits=60, default=0.00)
    status           = models.CharField(max_length=60, default='unapprove')
    account_debited  = models.CharField(max_length=225)
    token_id         = models.CharField(max_length=60, blank=True)
    Userlogin        = models.CharField(max_length=60, blank=True)	


    class Meta:
        db_table = "payroll_log"


class staff_account(models.Model):	
    date              = models.DateField()	
    description	      = models.CharField(max_length=255)
    type              = models.CharField(max_length=50)	
    amount            = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)		
    initial_amount    = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)		
    balance           = models.DecimalField(decimal_places=2, max_digits=64, blank=True, null=True)		
    staff_id	      = models.CharField(max_length=50, blank=True)
    staff_name        = models.CharField(max_length=60, blank=True)	
    payment_method    = models.CharField(max_length=50)	
    cur_datetime      = models.DateTimeField(auto_now_add=True)	
    account_posted    = models.CharField(max_length=50, blank=True)	
    transaction_id    = models.CharField(max_length=50, blank=True)	
    token_id          = models.CharField(max_length=50, blank=True)	
    Userlogin         = models.CharField(max_length=50, blank=True)	
    invoice_status    = models.CharField(max_length=200)

    class Meta:
        db_table = "staff_account"