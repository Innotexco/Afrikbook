from django import forms
from .models import loan_account, loan_account_log, new_journal_entry, new_journal_entry_log
from customer.models import customer_table

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = new_journal_entry
        fields = '__all__'

class JournalEntryLogForm(forms.ModelForm):
    class Meta:
        model =new_journal_entry_log
        fields = '__all__'

class LoanAccountForm(forms.ModelForm):
    class Meta:
        model = loan_account
        fields = '__all__'
    
     
    # def clean_debtor_name(self):
    #     debtor_id = self.cleaned_data['account_debited']
    #     debtor = customer_table.objects.get(id=debtor_id)
    #     debtor_name = debtor.name
    #    
    #     return debtor_name 
    
    # def save(self, *args, **kwargs):
    #     # Calculate balance_left by subtracting amount_paid from amount_borrowed
    #     amount_borrowed = int(self.cleaned_data['amount_borrowed'])
    #     amount_paid = int(self.cleaned_data['amount_paid'])
    #     self.balance_left = amount_borrowed - amount_paid
    #     return super().save(*args, **kwargs)
    
   
    
    
class LoanAccountLogForm(forms.ModelForm):
    class Meta:
        model = loan_account_log
        fields = ('__all__')

    

    # def save(self, *args, **kwargs):
    #     # Calculate balance_left by subtracting amount_paid from amount_borrowed
    #     amount_borrowed = int(self.cleaned_data['amount_borrowed'])
    #     amount_paid = int(self.cleaned_data['amount_paid'])
    #     self.balance_left = amount_borrowed - amount_paid
    #     return super().save(*args, **kwargs)
    
    # def clean_debtor_name(self):
    #     debtor_id = self.cleaned_data['account_debited']
    #     debtor = customer_table.objects.get(id=debtor_id)
    #     debtor_name = debtor.name
    #    
    #     return debtor_name