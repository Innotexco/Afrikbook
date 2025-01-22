from django import forms
from . models import *
from main. models import User
from client.models import shipping_addr
from customer.models import billing_addr

class PriceChangeForm(forms.ModelForm):
    class Meta:
        model = pricechange_history
        fields = ('__all__')

   


# class UserForm(forms.ModelForm):
#     class Meta:
#         model = user
#         fields = ('__all__')

#     username = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
#     password = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
#     confirm_password = forms.CharField(label="Confirm Password", required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
#     priviledge = forms.CharField(label="Priviledge", required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
    


    # def clean(self):
    #     cleaned_data = super(UserForm, self).clean()
    #     password = cleaned_data.get("password")
    #     confirm_password = cleaned_data.get("confirm_password")

    #     if confirm_password != password:
    #         raise forms.ValidationError("Password and confirm Password does not match")


# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = user
#         fields = ['username', 'priviledge', 'password']

#     username = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
#     password = forms.CharField(required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
#     priviledge = forms.CharField(label="Priviledge", required=False, widget=forms.TextInput(
#         attrs={"class": "form-control"}
#     ))
    

CURRENCY = (
    ('Naira', 'Naira'),
    ('Dollar', 'Dollar'),
    ('Pesos', 'Pesos'),
    
)

COUNTRY = (
    ('Nigeria', 'Nigeria'),
    ('USA', 'USA'),
    ('England', 'England'),
    ('Ghana', 'Ghana'),
    ('Benine', 'Benine'),
    ('South Africa', 'South Africa'),
    ('Russia', 'Russia')
)
class SalesOutletForm(forms.ModelForm):
    class Meta:
        model = sales_outlet
        fields = ('__all__')

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = profile
#         fields = ('__all__')


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse
        fields = ("warehouse_name", "description")

class CompanyDetailsForm(forms.ModelForm):

    class Meta:
        model = company_details
        fields = ("type", "detail")

class ShippingAddressForm(forms.ModelForm):

    class Meta:
        model = shipping_addr
        fields = "__all__"
        exclude = ('addr_id',)
    
    

class BillingAddressForm(forms.ModelForm):

    class Meta:
        model = billing_addr
        fields = "__all__"
        exclude = ('addr_id',)


        

