from django.conf import settings

from django import forms
from Stock.models import CreateStockInLog, CreateStockIn

class generalForms(forms.ModelForm):
    class Meta:
        table = CreateStockIn
        if settings.MY_EXPERIMENT == True:
            table = CreateStockInLog
        model = table
   

        # # UPDATE FORM WARE... TO WARE.....
        # fields = ['invoice_no']



        # CREATE STOCKIN FORM
        fields =['supplier','warehouse', 'description', 'item_decription', 
                 'item', 'quantity', 'outlet', 'notification_status', 'token_id', 'item_code', 
                 'Userlogin']
        exclude = ['id']        
        
        widgets = {
                    'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Invoice Number'}),
                    'order_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Order Number'}),
                    'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Supplier'}),
                    # 'supplier': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Supplier'}),
                    # 'warehouse': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Warehouse'}),
                    'warehouse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'item_decription': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'item': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TextInput Warehouse'}),
                    'outlet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Select Warehouse'}),
                    # 'outlet': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Warehouse'}),
                    'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'notification_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'token_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'ref_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'Userlogin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
                    'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Warehouse'}),
        }



    # invoice_no        = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))



    # order_no          = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # supplier          = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # warehouse         = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # description       = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # item_description  = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # item              = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # quantity          = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # outlet            = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # source            = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # notification_status= forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # token_id          = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # item_code         = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # ref_no            = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # Userlogin         = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # status            = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))
    # selling_price     = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    # }))