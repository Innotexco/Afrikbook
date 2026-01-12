from django import forms;
from settings.models import CreateProfile

class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = CreateProfile
        fields = ['ownerName', 'phone', 'phone2', 'email', 'Rc', 'CompanyName', 'services', 'address', 'country', 'currency', 'logo', 'show_customer_info', 'Token_ID', 'vat', 'Userlogin', 'pdf_template_preference']
        
        

