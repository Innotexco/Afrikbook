from django import forms
from . models import *

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

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = employee
        fields = ('__all__')
        
    gender = forms.ChoiceField(choices=GENDER, widget=forms.Select())
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS, widget=forms.Select())
    category = forms.ChoiceField(choices=CATEGORY, widget=forms.Select())
    

class EmployeeAccountForm(forms.ModelForm):
    class Meta:
        model = employee_account_details
        fields = ('__all__')
        exclude = ('employee_id',)

class EmployeeGurantorForm(forms.ModelForm):
    class Meta:
        model = employee_guarantor
        fields = ('__all__')
        exclude = ('employee_id',)

    relationship = forms.ChoiceField(choices=RELATIONSHIP, widget=forms.Select())

class PayRollForm(forms.ModelForm):
    class Meta:
        model = payroll
        fields = ('__all__')
        exclude = ('status', 'confirm_payment',)

class PayRollLogForm(forms.ModelForm):
    class Meta:
        model = payroll_log
        fields = ('__all__')

class StaffAccountForm(forms.ModelForm):
    class Meta:
        model = staff_account
        fields = ('__all__')