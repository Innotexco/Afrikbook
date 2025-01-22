# from typing import Any, Dict
from django import forms 

from .models import Vendor_invoice, vendor_table, Vendor_Quote, Vendor_Order, Vendor_Return


class VendorInovoiceForm(forms.ModelForm):

    class Meta:
        model = Vendor_invoice
        fields = ('__all__')
        exclude = ['item_descriptions',]


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

    email = forms.CharField(required=False)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        model = self.Meta.model
        vendor = model.objects.filter(email__iexact = email)

        if vendor.exists():
            raise forms.ValidationError("A vendor with that email already exists!")
        return self.cleaned_data.get('email') 



class VendorUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         
    class Meta:
        model = vendor_table
        fields = ("name", "phone", "email", "address", "company_name",)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        model = self.Meta.model
        vendor = model.objects.filter(email = email).exclude(pk=self.instance.pk)

        if vendor.exists():
            raise forms.ValidationError("A vendor with that email already exists!")
        return self.cleaned_data.get('email') 






