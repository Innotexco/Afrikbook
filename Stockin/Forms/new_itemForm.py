from django import forms;
from Stock.models import Item
from Stock.utils import random_string_generator;
class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'sub_category', 'item_name', 'generated_code', 'purchase_price', 'selling_price',  'wholesale_price', 'size', 'token_id', 'attribute', 'Userlogin', 'description']
        randomtoken = random_string_generator()
        widgets = {
            'token_id': forms.HiddenInput(attrs={'value': 'Token_'+randomtoken}),
            'Userlogin': forms.HiddenInput(attrs={'value': 'admin'}),
            'item_name': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Item Name",
                 }),
            'generated_code': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Code",
                 }),
            'purchase_price': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Purchase Price",
                 }),
            'selling_price': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Selling Price",
                 }),
            
            'wholesale_price': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Wholesale",
                 }),
            'size': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Size",
                 }),
            'attribute': forms.TextInput(attrs={'class': 'w-full border rounded py-2 px-3', 
                                                    'placeholder':"Enter Attribute",
                 }),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded py-2 px-3', 
                                            'placeholder':"Enter Description",
            }),
        }
        