from django import forms

# from .models import (
#     Item, ItemImage, ItemTags, ItemSpecification, ItemDetailDescription, 
#     ItemSpecificationFeatures, ItemBrand, ItemSize, ItemColor, 
#     Category, Sub_Category, Coupon, company_table
# )
from .models import company_table



# class CategoryForm(forms.ModelForm):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#     class Meta:
#         model = Category
#         fields = ("category_name", "description", "cat_img")   


# class EditCategoryForm(forms.ModelForm):

#     class Meta:
#         model = Category
#         fields = ("category_name", "description", "cat_img")   


# class SubCategoryForm(forms.ModelForm):
    
#     class Meta:
#         model = Sub_Category
#         fields = ("main_category", "name")  
    



# class ItemForm(forms.ModelForm):

#     class Meta:
#         model = Item
#         fields = ("category", "sub_category", "item_name", "generated_code", "purchase_price", "selling_price", "description", "wholesale_price", "size", "attribute", "image")
    
#     images = forms.ImageField(widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}), required=False)

    
#     def save(self, commit=True):
#         product = super(ItemForm, self).save(commit=commit)
#         images = self.cleaned_data.get('images')
#         if commit and images:
#             if isinstance(images, list):  # Check if images is a list of uploaded files
#                 for img in images:
#                     ItemImage.objects.create(product=product, image=img)
#             else:  # Handle the case when a single image is uploaded
#                 ItemImage.objects.create(product=product, image=images)
#         return product
    



# class EditItemForm(forms.ModelForm):

#     images = forms.ImageField(widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}), required=False)

#     class Meta:
#         model = Item
#         fields = ("category", "sub_category", "item_name", "generated_code", "purchase_price", "selling_price", "description", "wholesale_price", "size", "attribute", "image", "discount_price", "discount_percentage", "state")




# class ItemTagForm(forms.ModelForm):
#     class Meta:
#         model = ItemTags
#         fields = ("item_code", "item_status",)



# class ItemSizeForm(forms.ModelForm):
#     class Meta:
#         model = ItemSize
#         fields = ("item_code", "size",)




# class ItemSpecificationForm(forms.ModelForm):
#     class Meta:
#         model = ItemSpecification
#         fields = ("item_code", "quality")




# class ItemDescriptionForm(forms.ModelForm):
#     class Meta:
#         model = ItemDetailDescription
#         fields = '__all__'
        


# class ItemBrandForm(forms.ModelForm):
#     class Meta:
#         model = ItemBrand
#         fields = '__all__'
        


# class ItemColorForm(forms.ModelForm):
#     class Meta:
#         model = ItemColor
#         fields = ("item_code","color_name", "color_code")
        


# class ItemFeaturesForm(forms.ModelForm):
#     class Meta:
#         model = ItemSpecificationFeatures
#         fields = ("item_code","key_features")




# class CouponForm(forms.ModelForm):

#     class Meta:
#         model = Coupon
#         fields = ("title", "desc", "code", "amount")

class CompanyForm(forms.ModelForm):

    class Meta:
        model = company_table
        fields = '__all__'
        exclude = ('owner','db_name', )







