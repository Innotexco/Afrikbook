from django import forms;
from Stock.models import Category, Item
from customer.models import customer_table, customer_invoice
from settings.models import CreateProfile 
from main.models import User



class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description', 'token_id', 'cat_img', 'Userlogin']
       
        
class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ["sub_category", "item_name", "generated_code", "purchase_price", "selling_price", "description", "wholesale_price", "size", "attribute", "image"]
        

class ItemUpdateForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ["sub_category", "item_name", "generated_code", "purchase_price", "selling_price", "description", "wholesale_price", "size", "attribute", "image", "state", "discount_price", "discount_percentage"]
    


class CustomerForm(forms.ModelForm):
    class Meta:
        model = customer_table
        fields = ['name', 'phone', 'customer_code',  'email', 'category', 'company_name']



class SalesUpdateForm(forms.ModelForm):
    pass
    class Meta:
        model = customer_invoice
        fields = ['cusID',  'itemcode',  'qty', 'payment_method']


class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = CreateProfile
        fields = ['ownerName', 'phone', 'phone2', 'email', 'Rc', 'CompanyName', 'services', 'address', 'country', 'currency', 'logo', 'show_customer_info', 'Token_ID', 'vat', 'Userlogin', 'pdf_template_preference']
        


class RegisterForm(forms.ModelForm):
    class Meta:

        model = User
        fields = ['username', 'password', 'email', 'Token_ID']
        

    # def clean_username(self):
    #       username  = self.cleaned_data.get('username')
    #       qs        = User.objects.filter(username=username)
    #       if qs.exists():
    #            raise forms.ValidationError('Username already exists')
    #       return username
     
    # def clean_email(self):
    #       email  = self.cleaned_data.get('email')
    #       qs        = User.objects.filter(email=email)
    #       if qs.exists():
    #            raise forms.ValidationError('email already exists')
    #       return email
     
    #  def clean(self):
    #       data = self.cleaned_data
    #       password =  data.get('password')
    #       confirm_password =  data.get('confirm_password')
    #       if password != confirm_password:
    #            raise forms.ValidationError('Passwords must match')
