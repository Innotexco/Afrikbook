
from django import forms

from .models import *
from Stock.models import *

# Table1, Table2, Table3






class AccountForm(forms.ModelForm):

    class Meta:
        model = accounts
        fields = ("account_series", "series_name", "account_type")


    



class ChartOfAccount(forms.ModelForm):

    class Meta:
        model = chart_of_account
        fields = ("account_id", "account_bankname", "account_type")
        
class AssetsAccount(forms.ModelForm):

    class Meta:
        model = Assets_account
        fields = ("account_id", "account_bankname", "account_type")
        
class ExpensesAccount(forms.ModelForm):

    class Meta:
        model = Expenses_account
        fields = ("account_id", "account_bankname", "account_type")
        
        
class LiabilityAccount(forms.ModelForm):

    class Meta:
        model = Liability_account
        fields = ("account_id", "account_bankname", "account_type")
        
        
class EquityAccount(forms.ModelForm):

    class Meta:
        model = Equity_account
        fields = ("account_id", "account_bankname", "account_type")
        
        
class IncomeAccount(forms.ModelForm):

    class Meta:
        model = Income_account
        fields = ("account_id", "account_bankname", "account_type")
        




class AccountTransfer(forms.ModelForm):
    class Meta:
        model = transfer_account
        fields = ['date_tx', 'description', 'paid_from', 'received_in', 'amount']




class Account_Log_Form(forms.ModelForm):
                    
    class Meta:
        model = account_log
        fields = '__all__'
        


class StockIn_Form(forms.ModelForm):
                    
    class Meta:
        model = CreateStockIn
        fields = '__all__'
        

class StockIn_Log_Form(forms.ModelForm):
                    
    class Meta:
        model = CreateStockIn
        fields = '__all__'
        

class Outlet_StockIn_Form(forms.ModelForm):
                    
    class Meta:
        model = CreateOutletStockIn
        fields = '__all__'
        


class Outlet_StockIn_Log_Form(forms.ModelForm):
                    
    class Meta:
        model = CreateOutletStockInLog
        fields = '__all__'
        











class InsertDataForm(forms.Form):
    token_id = forms.CharField(max_length=50)
    amount = forms.IntegerField()



# class Table1Form(forms.ModelForm):
#     class Meta:
#         model = Table1
#         fields = ['field1', 'field2']

# class Table2Form(forms.ModelForm):
#     class Meta:
#         model = Table2
#         fields = ['field3', 'field4']

# class Table3Form(forms.ModelForm):
#     class Meta:
#         model = Table3
#         fields = ['field5', 'field6']
