from django import forms;
from Stock.models import Category
from Stock.utils import random_string_generator;
class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'sub_category', 'token_id', 'userlog']
        randomtoken = random_string_generator()
        widgets = {
            'token_id': forms.HiddenInput(attrs={'value': 'Token_'+randomtoken}),
            'userlog': forms.HiddenInput(attrs={'value': 'admin'}),
            'category_name': forms.TextInput(attrs={'class': 'w-full border rounded py-3 px-3', 
                                                    'placeholder':"Enter Category",
                 }),
            'sub_category': forms.TextInput(attrs={'class': 'w-full border rounded py-3 px-3', 
                                                     'placeholder':"Enter Sub Category" 
                }),
        }
        