from django import forms;
from Stock.models import CreateStockInLog, CreateOutletStockInLog
from Stock.utils import random_string_generator;
class W_W_Form(forms.ModelForm):
    class Meta:
        model = CreateStockInLog
        fields = ['supplier', 'warehouse', 'description', 'item_decription', 'item', 'quantity', 'outlet', 'source', 'token_id', 'item_code', 'ref_no', 'Userlogin', 'selling_price']
        widgets = {
         
          'Userlogin': forms.HiddenInput(attrs={'value': 'admin'}),
          'supplier': forms.HiddenInput(attrs={'value': 'vendor'}),
          'source': forms.HiddenInput(attrs={'value': 'vendor'}),
          'description': forms.Textarea(attrs={'class': 'w-full border rounded py-2 px-3', 
               'placeholder':"Enter Description",}),
          'item_decription[]': forms.TextInput(attrs={ 'required': 'False'} ),
          'item_code[]': forms.TextInput(attrs={ 'required': 'False'} ),
          'item[]': forms.TextInput(attrs={ 'required': 'False'} ),
        }
     #    item_decription = forms.CharField(required=False)








class W_O_Form(forms.ModelForm):
  class Meta:
      model = CreateOutletStockInLog
      fields = ['supplier', 'warehouse', 'description', 'item_decription', 'item', 'quantity', 'outlet',  'token_id', 'item_code', 'ref_no', 'Userlogin', 'selling_price', 'wholesale_price']
      randomtoken = random_string_generator()
      widgets = {
        'token_id': forms.HiddenInput(attrs={'value': 'Token_'+randomtoken}),
        'Userlogin': forms.HiddenInput(attrs={'value': 'admin'}),
        'supplier': forms.HiddenInput(attrs={'value': 'vendor'}),
        'description': forms.Textarea(attrs={'class': 'w-full border rounded py-2 px-3', 
              'placeholder':"Enter Description",}),
        'item_decription[]': forms.TextInput(attrs={ 'required': 'False'} ),
        'item_code[]': forms.TextInput(attrs={ 'required': 'False'} ),
        'item[]': forms.TextInput(attrs={ 'required': 'False'} ),
      }
     #    item_decription = forms.CharField(required=False)