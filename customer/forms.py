from django import forms

from .models import *
from Stock.models import Item

CATEGORY_CHOICES = (
    ('Whole Sale', 'Whole Sale'),
    ('Retail', 'Retail')
)
CATEGORY = (
    ('Customer', 'Customer'),
    ('Vendor', 'Vendor')
)
TRANSACTION_TYPE = (
    ('Credit', 'Credit'),
    ('Debit', 'Debit')
)
OPERATING_ACCOUNT = (
    ('Uba', 'Uba'),
    ('Fidelity', 'Fidelity')
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = customer_table
        fields = ['name', 'phone', 'email', 'customer_code', 'category', 'company_name']

    email = forms.CharField(required=True)
        # REQUIREDFIELD =  ['name', 'phone', 'category', 'email', 'company_name', 'address']


    

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("__all__")  

class SalesQuoteForm(forms.ModelForm):
    class Meta:
        model = sales_quote
        fields = ("__all__") 

class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = sales_order
        fields = ("__all__")  

class CustomerSalesForm(forms.ModelForm):
    class Meta:
        model = customer_invoice
        fields = "__all__" 
    

class ReceivableForm(forms.ModelForm):
    class Meta:
        model = receivable
        fields = "__all__" 
    # description = forms.CharField(required=False)

class PayableForm(forms.ModelForm):
    class Meta:
        model = payable
        fields = "__all__" 

class ReturnInwardForm(forms.ModelForm):
    class Meta:
        model = sales_return
        fields = "__all__" 
    

class CustomerIncentiveForm(forms.ModelForm):
    class Meta:
        model = customer_incentive
        fields = ['customer_id', 'customer_name', 'description', 'amount', 'initial_amount', 'date']



