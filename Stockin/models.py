import os
from django.db import models
# import uuid
# from django.utils.text import slugify
# from .utils import generate_unique_id
# from customer.models import customer_table
# from account.utils import generate_unique_id, generate_order_id, generate_token_id





# class CreateStockout(models.Model):
#     date                 = models.DateField(max_length=250, auto_now_add=True)
#     invoice_no           = models.CharField(max_length=250)
#     order_no             = models.CharField(max_length=250)
#     customer             = models.CharField(max_length=250)
#     warehouse            = models.CharField(max_length=250)
#     description          = models.CharField(max_length=250)
#     item_description     = models.CharField(max_length=250)
#     item                 = models.CharField(max_length=250)
#     quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
#     stockout_status      = models.CharField(max_length=250)
   

#     class Meta:
#         db_table = 'stockout'  # Specify the table name


# class CreateStockoutOrder(models.Model):
#     date                 = models.DateField(max_length=250, auto_now_add=True)
#     invoice_no           = models.CharField(max_length=250)
#     order_no             = models.CharField(max_length=250)
#     customer             = models.CharField(max_length=250)
#     warehouse            = models.CharField(max_length=250)
#     description          = models.CharField(max_length=250)
#     item_code            = models.CharField(max_length=250)
#     item_description     = models.CharField(max_length=250)
#     item                 = models.CharField(max_length=250)
#     quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
#     stockout_status      = models.CharField(max_length=250)
   

#     class Meta:
#         db_table = 'stockout_order'  # Specify the table name






# class CreateStockInLog(models.Model):
#     datetx               = models.DateField(max_length=250, auto_now_add=True)
#     invoice_no           = models.CharField(max_length=250)
#     order_no             = models.CharField(max_length=250)
#     supplier             = models.CharField(max_length=250)
#     warehouse            = models.CharField(max_length=250, null=True, blank=True)
#     description          = models.CharField(max_length=250)
#     item_decription      = models.CharField(max_length=250)
#     item                 = models.CharField(max_length=250)
#     quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=None)
#     outlet               = models.CharField(max_length=250, null=True, blank=True)
#     source               = models.CharField(max_length=250)
#     manufacture_date     = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
#     expiry_date          = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
#     Notification_date    = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
#     notification_status  = models.CharField(max_length=250)
#     token_id             = models.CharField(max_length=250)
#     item_code            = models.CharField(max_length=250)
#     ref_no               = models.CharField(max_length=250)
#     Userlogin            = models.CharField(max_length=250)
#     status               = models.CharField(max_length=250, default='Unverified')
#     transfer             = models.CharField(max_length=200, null=True, blank=True)
#     selling_price        = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
   

#     class Meta:
#         db_table = 'stockin_log'  # Specify the table name





# class CreateStockIn(models.Model):
#     datetx               = models.DateField(max_length=222, auto_now_add=True)
#     invoice_no           = models.CharField(max_length=250)
#     order_no             = models.CharField(max_length=250)
#     supplier             = models.CharField(max_length=250)
#     warehouse            = models.CharField(max_length=250)
#     outlet               = models.CharField(max_length=250, null=True, blank=True)
#     description          = models.CharField(max_length=250)
#     item                 = models.CharField(max_length=250)
#     item_decription      = models.CharField(max_length=250)
#     quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
#     manufacture_date     = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
#     expiry_date          = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
#     Notification_date    = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
#     notification_status  = models.CharField(max_length=250)
#     low_stock_level      = models.IntegerField(blank=True, null=True)
#     size                 = models.CharField(max_length=60, default=None, blank=True, null=True)
#     token_id             = models.CharField(max_length=250)
#     item_code            = models.CharField(max_length=250)
#     Userlogin            = models.CharField(max_length=250)  
#     main                 = models.BooleanField(default=True)  
   

#     class Meta:
#         db_table = 'stockin'  # Specify the table name









# class StockOutLog(models.Model):
#     datetx               = models.DateField(max_length=222, auto_now_add=True)
#     invoice_no           = models.CharField(max_length=250)
#     order_no             = models.CharField(max_length=250)
#     customer             = models.CharField(max_length=250)
#     warehouse            = models.CharField(max_length=250)
#     description          = models.CharField(max_length=250)
#     item                 = models.CharField(max_length=250)
#     item_description     = models.CharField(max_length=250)
#     quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
#     token                = models.CharField(max_length=250)
#     Userlogin            = models.CharField(max_length=250)
#     stockout_status      = models.CharField(max_length=250)

   

#     class Meta:
#         db_table = 'stockout_log'  # Specify the table name










# class Category(models.Model):
#     category_name       = models.CharField(max_length = 255)
#     description         = models.CharField(max_length = 255)
#     state               = models.IntegerField(default=0)
#     cat_img             = models.ImageField(null=True, blank=True, upload_to="category_img/", max_length=255)
#     token_id            = models.CharField(max_length=25, blank=True, default=generate_unique_id())
#     Userlogin           = models.CharField(max_length = 255, blank=True)

        
#     def generate_unique_filename(self):
#         # Generate a unique key (4 characters) along with the category name
#         unique_key = uuid.uuid4().hex[:4]
#         filename = f"{slugify(self.category_name)}_{unique_key}"
#         if self.cat_img:
#             _, extension = os.path.splitext(self.cat_img.name)
#             filename += extension.lower()  # Add the original extension
#         else:
#             filename += ".jpg"  # Set a default extension if no image is provided
#         return filename
    
#     def save(self, *args, **kwargs):
#         # Check if a category with the same name already exists
#         existing_category = Category.objects.filter(category_name=self.category_name).first()

#         if existing_category:
#             # If it exists, don't save the new record
#             return

#         # If it doesn't exist, proceed with saving
#         if self.cat_img and self.category_name:
#             filename = self.generate_unique_filename()
#             self.cat_img.name = os.path.join("", filename)

#         super().save(*args, **kwargs)

#     # def save(self, *args, **kwargs):
#     #     # Set the image name to a combination of unique key + category name
#     #     if self.cat_img and self.category_name:
#     #         filename = self.generate_unique_filename()
#     #         self.cat_img.name = os.path.join("", filename)

#     #     super().save(*args, **kwargs)

#     class Meta:
#         db_table = "category"


# class Sub_Category(models.Model):
#     main_category = models.ForeignKey(
#         Category, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.main_category.category_name + "---" + self.name
    
#     class Meta:
#         db_table = "sub_category"


           



# class ItemTags(models.Model):
#     item_code           = models.CharField(max_length=255, null=True, blank=True)
#     item_status    = models.CharField(max_length=255, null=True, blank=True)
#     slug = models.SlugField(null=True, blank=True)
#     created_date    = models.DateField(auto_now_add=True)
    
#     def __str__(self) -> str:
#         return self.item_status    

#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.item_status)
#         return super().save(*args, **kwargs) 
    
#     class Meta: 
#         db_table = "ItemTags"


# class Item(models.Model):
#     category = models.ForeignKey(
#             Category, on_delete=models.CASCADE, related_name='main_category')

#     sub_category = models.ForeignKey(
#         Sub_Category, on_delete=models.CASCADE, related_name='category', null=True, 
#         blank=True)
#     item_name       = models.CharField(max_length = 255)
#     generated_code  = models.CharField(max_length = 255)
#     purchase_price  = models.CharField(max_length = 255)
#     selling_price   = models.CharField(max_length = 255)
#     description     = models.TextField()
#     wholesale_price = models.CharField(max_length = 255)
#     size            = models.IntegerField(default=1)
#     attribute       = models.CharField(max_length = 255)
#     image           = models.ImageField(null=True, blank=True, upload_to="item_img/")
#     availability    = models.IntegerField(default=1)
#     likes           = models.ManyToManyField(customer_table, related_name='customer_likes', blank=True)
#     tags            = models.ManyToManyField(ItemTags, related_name='tag_items', blank=True)
#     state           = models.CharField(max_length=255, null=True, blank=True)
#     discount_price  = models.DecimalField(max_digits=65, decimal_places=2, default=0.00)
#     discount_percentage  = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, blank=True)
#     token_id        = models.CharField(max_length = 255, default=generate_unique_id())
#     Userlogin       = models.CharField(max_length = 255, blank=True, null=True)
#     slug            = models.SlugField(unique=True, max_length=100, null=True, blank=True)

    

#     def generate_unique_filename(self):
#         unique_key = uuid.uuid4().hex[:4]
#         filename = f"{slugify(self.description)}_{unique_key}"
#         if self.image:
#             _, extension = os.path.splitext(self.image.name)
#             filename += extension.lower()  
#         else:
#             filename += ".jpg" 
#         return filename

#     def save(self, *args, **kwargs):
        
#         if self.image and self.description:
#             filename = self.generate_unique_filename()
#             self.image.name = os.path.join("", filename)

#         super().save(*args, **kwargs)

#     def calculate_discount_percentage(self):
#         if self.selling_price and self.discount_price:
#             selling_price = float(self.selling_price)
#             discount_price = float(self.discount_price)
#             if selling_price != 0:
#                 discount_price = ((selling_price - discount_price) / selling_price) * 100 
#                 if discount_price > 100:
#                     return discount_price - 100
#                 return  100 - discount_price
#         return 0.00  # Default value if prices are not provided

#     def save(self, *args, **kwargs):
#         self.discount_percentage = self.calculate_discount_percentage()
#         super().save(*args, **kwargs)

#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.item_name)
#         return super(Item, self).save(*args, **kwargs) 
        
#     class Meta:
#         db_table = "Item"


# class ItemImage(models.Model):
#     item    = models.ForeignKey(Item, on_delete=models.CASCADE)
#     image   = models.ImageField(upload_to='item_img/')  

#     class Meta:
#         db_table = "item_image"      


# class ItemSpecification(models.Model):
#     item_code   = models.CharField(max_length=255, null=True, blank=True)
#     quality = models.CharField(max_length=255, null=True, blank=True) 
#     slug = models.SlugField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True, blank=True)

#     def __str__(self) -> str:
#         return self.quality
    
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.quality)
#         return super(ItemSpecification, self).save(*args, **kwargs) 

#     class Meta: 
#         db_table = "ItemSpecification"



# class ItemDetailDescription(models.Model):
#     item_code   = models.CharField(max_length=255, blank=True)
#     text = models.TextField()
#     slug = models.SlugField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.item_code

#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.text)
#         return super(ItemDetailDescription, self).save(*args, **kwargs)
    
#     class Meta: 
#         db_table = "ItemDetailDescription"



# class ItemSpecificationFeatures(models.Model):
#     item_code = models.CharField(max_length=255, null=True, blank=True)
#     key_features = models.CharField(max_length=255, null=True, blank=True)
#     slug = models.SlugField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.key_features
    
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.key_features)
#         return super(ItemSpecificationFeatures).save(*args, **kwargs) 
    
#     class Meta: 
#         db_table = "ItemSpecificationFeatures"




# class ItemSize(models.Model):
#     item_code   = models.CharField(max_length=255, null=True, blank=True)
#     size   = models.CharField(max_length=255, null=True, blank=True)
#     slug = models.SlugField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.size

#     def save(self, *args, **kwargs):
#         # self.slug = slugify(self.size)
#         if self.slug is None and self.created_date and self.id:
#             self.slug = self.created_date.strftime('75%Y%n%d23') + str(self.id)
#         return super().save(*args, **kwargs)
    
#     class Meta:
#         db_table = "ItemSize"




# class ItemBrand(models.Model):
#     item_code   = models.CharField(max_length=255, blank=True)
#     brand_name   = models.CharField(max_length=255, blank=True)
#     slug = models.SlugField( blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.brand_name

#     def save(self, *args, **kwargs):
#         # self.slug = slugify(self.item_code)
#         if self.slug is None and self.created_date and self.id:
#             self.slug = self.created_date.strftime('75%Y%n%d23') + str(self.id)
#         return super().save(*args, **kwargs)

#     class Meta: 
#         db_table = "ItemBrand"




# class ItemColor(models.Model):
#     item_code   = models.CharField(max_length=255, null=True, blank=True)
#     color_name   = models.CharField(max_length=255, null=True, blank=True)
#     color_code   = models.CharField(max_length=255, null=True, blank=True)
#     slug = models.SlugField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.color_name
    
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.color_name)
#         return super(ItemCustomerReview).save(*args, **kwargs)
    
#     class Meta: 
#         db_table = "ItemColor"
 



# class ItemCustomerReview(models.Model):
#     item    = models.ForeignKey(Item, on_delete=models.CASCADE)
#     customer    = models.ForeignKey(customer_table, on_delete=models.CASCADE)
#     star = models.CharField(max_length=255, null=True, blank=True)
#     text = models.TextField()
#     slug = models.SlugField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.text
    
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.text)
#         return super(ItemCustomerReview).save(*args, **kwargs) 
#     class Meta: 
#         db_table = "ItemCustomerReview"




# class Coupon(models.Model):
#     title        = models.CharField(max_length=100)
#     desc        = models.CharField(max_length=100)
#     code        = models.IntegerField(default=0)
#     amount      = models.DecimalField(max_digits=65, decimal_places=2, default=0.00)
#     slug = models.SlugField(null=True, blank=True)

#     def __str__(self) -> str:
#         return self.title
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.title)
#         return super(ItemCustomerReview).save(*args, **kwargs)
    
#     class Meta: 
#         db_table = "coupon"


class company_table(models.Model):
    company_name   = models.CharField(max_length=100)
    owner          = models.CharField(max_length=50, blank=True)
    db_name        = models.CharField(max_length=100)
    phone          = models.CharField(max_length=100)
    email          = models.EmailField(max_length=100, blank=True)
    city           = models.CharField(max_length=100)
    state          = models.CharField(max_length=100)
    zipCode        = models.CharField(max_length=100, blank=True)
    country        = models.CharField(max_length=100)
    address        = models.CharField(max_length=500)
    token_id       = models.IntegerField( blank=True, null=True)
    Userlogin      = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        db_table = "company"




