# from typing import Any, Dict
from django import forms 

from .models import Vendor_invoice, vendor_table, Vendor_Quote, Vendor_Order, Vendor_Return


class VendorInovoiceForm(forms.ModelForm):

    class Meta:
        model = Vendor_invoice
        fields = ('__all__')
        # exclude = ['item_descriptions',]


class VendorQuoteForm(forms.ModelForm):

    class Meta:
        model = Vendor_Quote
        fields = ('__all__')

class PurchaseQuoteForm(forms.Form):
    quote_date = forms.DateField()
    referenceID = forms.CharField(required=False)
    Gdescription = forms.CharField(required=False)
    genby = forms.CharField()
    item = forms.CharField()
    desc = forms.CharField()
    qty = forms.IntegerField()
    unit = forms.DecimalField()
    discount = forms.DecimalField()
    amount = forms.DecimalField()


class VendorOrderForm(forms.ModelForm):

    class Meta:
        model = Vendor_Order
        fields = ('__all__')


class VendorReturnForm(forms.ModelForm):

    class Meta:
        model = Vendor_Return
        fields = ('__all__')
        # fields = ("refund_date", "invoiceID", "itemcode", "Gdescription", "genby")



class VendorRegistrationForm(forms.ModelForm):

    class Meta:
        model = vendor_table
        fields = ("name", "phone", "email", "address",)

    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    
    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return ''
        model = self.Meta.model
        if model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A vendor with that email already exists!")
        return email

    def clean_phone(self):
        return (self.cleaned_data.get('phone') or '').strip()



class VendorUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['email'].required = False

         
    class Meta:
        model = vendor_table
        fields = ("name", "phone", "email", "address", "company_name",)

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return ''
        model = self.Meta.model
        if model.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A vendor with that email already exists!")
        return email

    def clean_phone(self):
        return (self.cleaned_data.get('phone') or '').strip()






