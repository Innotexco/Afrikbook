import os
import uuid
from django.db import models
from django.utils.text import slugify
from .utils import generate_unique_id
from customer.models import customer_table
from account.utils import generate_unique_id, generate_order_id, generate_token_id
from django.db.models.signals import pre_save, post_save
from .utils import unique_slug_generator;
from main.models import User
# Create your models here.
# class CreateCategory(models.Model):
#     category_name       = models.CharField(max_length=250)
#     sub_category        = models.CharField(max_length=500)
#     token_id            = models.CharField(max_length=200, unique=True)
#     userlog             = models.CharField(max_length=500)

#     class Meta:
#         db_table = 'category'  



# class CreateItem(models.Model):
#     category             = models.CharField(max_length=250)
#     sub_category         = models.CharField(max_length=250)
#     item_name            = models.CharField(max_length=250)
#     generated_code       = models.CharField(max_length=250)
#     purchase_price       = models.CharField(max_length=250)
#     selling_price        = models.CharField(max_length=250)
#     description          = models.CharField(max_length=250)
#     wholesale_price      = models.CharField(max_length=250)
#     size                 = models.CharField(max_length=250)
#     token_id             = models.CharField(max_length=250)
#     attribute            = models.CharField(max_length=250, default=None)
#     Userlogin            = models.CharField(max_length=250)

    # class Meta:
    #     db_table = 'Item'  



class CreateStockout(models.Model):
    date                 = models.DateField(max_length=250, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    customer             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250)
    description          = models.CharField(max_length=250)
    item_description     = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    stockout_status      = models.CharField(max_length=250)
   

    class Meta:
        db_table = 'stockout'  


class CreateStockoutOrder(models.Model):
    date                 = models.DateField(max_length=250, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    customer             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250)
    description          = models.CharField(max_length=250)
    item_code            = models.CharField(max_length=250)
    item_description     = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    stockout_status      = models.CharField(max_length=250)
   

    class Meta:
        db_table = 'stockout_order'  






class CreateStockInLog(models.Model):
    datetx               = models.DateField(max_length=250, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    supplier             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250, null=True, blank=True)
    description          = models.CharField(max_length=250)
    item_decription      = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=None)
    outlet               = models.CharField(max_length=250, null=True, blank=True)
    source               = models.CharField(max_length=250)
    manufacture_date     = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
    expiry_date          = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
    Notification_date    = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
    notification_status  = models.CharField(max_length=250)
    token_id             = models.CharField(max_length=250)
    item_code            = models.CharField(max_length=250)
    ref_no               = models.CharField(max_length=250)
    Userlogin            = models.CharField(max_length=250)
    status               = models.CharField(max_length=250, default='Unverified')
    transfer             = models.CharField(max_length=200, null=True, blank=True)
    selling_price        = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
   

    class Meta:
        db_table = 'stockin_log'  





class CreateStockIn(models.Model):
    datetx               = models.DateField(max_length=222, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    supplier             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250)
    outlet               = models.CharField(max_length=250, null=True, blank=True)
    description          = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    item_decription      = models.CharField(max_length=250)
    amount              = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)	
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    manufacture_date     = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
    expiry_date          = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
    Notification_date    = models.DateField(max_length=250, null=True, blank=True, auto_now_add=True)
    notification_status  = models.CharField(max_length=250)
    low_stock_level      = models.IntegerField(blank=True, null=True)
    size                 = models.CharField(max_length=60, default=None, blank=True, null=True)
    token_id             = models.CharField(max_length=250)
    item_code            = models.CharField(max_length=250)
    Userlogin            = models.CharField(max_length=250)  
    main                 = models.BooleanField(default=True)  
   

    class Meta:
        db_table = 'stockin'  





class CreateOutletStockInLog(models.Model):
    datetx               = models.DateField(auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    supplier             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250, null=True, blank=True)
    outlet               = models.CharField(max_length=250, null=True, blank=True)
    description          = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    item_decription      = models.CharField(max_length=250)
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    token_id             = models.CharField(max_length=250)
    item_code            = models.CharField(max_length=250)
    Userlogin            = models.CharField(max_length=250)  
    selling_price        = models.CharField(max_length=250)  
    wholesale_price      = models.CharField(max_length=250)  
    status               = models.CharField(max_length=250, default='Unverified')  
    edit_status          = models.CharField(max_length=250, default='Unverified')  
    transfer             = models.CharField(max_length=200, null=True, blank=True)
    ref_no               = models.CharField(max_length=250)  
    main                 = models.BooleanField(default=True)  

    class Meta:
        db_table = 'outlet_stockin_log'  





class CreateOutletStockIn(models.Model):
    datetx               = models.DateField(max_length=222, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    supplier             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250, null=True, blank=True)
    outlet               = models.CharField(max_length=250, null=True, blank=True)
    description          = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    item_decription      = models.CharField(max_length=250)
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    token_id             = models.CharField(max_length=250)
    item_code            = models.CharField(max_length=250)
    Userlogin            = models.CharField(max_length=250)  
    selling_price        = models.CharField(max_length=250)  
    wholesale_price      = models.CharField(max_length=250)  
    notification_status  = models.CharField(max_length=250)
    low_stock_level      = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2)
    size                 = models.CharField(max_length=60, default=None, blank=True, null=True)
    main                 = models.BooleanField(default=True)  

   

    class Meta:
        db_table = ' outlet_stockin'  





class StockAdjustmentLog(models.Model):
    datetx               = models.DateField(max_length=222, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250, null=True, blank=True)
    initial_qty          = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    new_qty              = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    item_code            = models.CharField(max_length=250)
    type                 = models.CharField(max_length=250)  
    Userlogin            = models.CharField(max_length=250)  

   

    class Meta:
        db_table = 'stock_adjustment_log'  






class StockInUpdateLog(models.Model):
    itemname             = models.CharField(max_length=250)
    description          = models.CharField(max_length=250)
    reason               = models.CharField(max_length=250)
    oldQty               = models.CharField(max_length=250)
    newQty               = models.CharField(max_length=250)
    user                 = models.CharField(max_length=250)

    class Meta:
        db_table = 'stockin_update_log'  






class StockOutStatus(models.Model):
    status               = models.CharField(max_length=250)
    userlogin            = models.CharField(max_length=250)
    token_id             = models.CharField(max_length=250)
    

    class Meta:
        db_table = 'stockout_status'  



class StockOutLog(models.Model):
    datetx               = models.DateField(max_length=222, auto_now_add=True)
    invoice_no           = models.CharField(max_length=250)
    order_no             = models.CharField(max_length=250)
    customer             = models.CharField(max_length=250)
    warehouse            = models.CharField(max_length=250)
    description          = models.CharField(max_length=250)
    item                 = models.CharField(max_length=250)
    item_description     = models.CharField(max_length=250)
    quantity             = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, default=0.0)
    token                = models.CharField(max_length=250)
    Userlogin            = models.CharField(max_length=250)
    stockout_status      = models.CharField(max_length=250)

   

    class Meta:
        db_table = 'stockout_log'  










class Category(models.Model):
    category_name       = models.CharField(max_length = 255)
    description         = models.CharField(max_length = 255)
    state               = models.IntegerField(default=0)
    cat_img             = models.ImageField(null=True, blank=True, upload_to="category_img/", max_length=255)
    token_id            = models.CharField(max_length=25, blank=True, default=generate_unique_id)
    Userlogin           = models.CharField(max_length = 255, blank=True)

        
    def generate_unique_filename(self):
        # Generate a unique key (4 characters) along with the category name
        unique_key = uuid.uuid4().hex[:4]
        filename = f"{slugify(self.category_name)}_{unique_key}"
        if self.cat_img:
            _, extension = os.path.splitext(self.cat_img.name)
            filename += extension.lower()  # Add the original extension
        else:
            filename += ".jpg"  # Set a default extension if no image is provided
        return filename
    
    def save(self, *args, **kwargs):
        # Check if a category with the same name already exists
        # existing_category = Category.objects.filter(category_name=self.category_name).first()

        # if existing_category:
        #     # If it exists, don't save the new record
        #     return

        # If it doesn't exist, proceed with saving
        if self.cat_img and self.category_name:
            filename = self.generate_unique_filename()
            self.cat_img.name = os.path.join("", filename)

        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Set the image name to a combination of unique key + category name
    #     if self.cat_img and self.category_name:
    #         filename = self.generate_unique_filename()
    #         self.cat_img.name = os.path.join("", filename)

    #     super().save(*args, **kwargs)

    class Meta:
        db_table = "category"


class  fre_category(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.CharField(max_length=256)
    state = models.IntegerField(default=0)
    image = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'fre_category'

class Sub_Category(models.Model):
    main_category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.main_category.category_name + "---" + self.name
    
    class Meta:
        db_table = "sub_category"


           



class ItemTags(models.Model):
    item_code           = models.CharField(max_length=255, null=True, blank=True)
    item_status    = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    created_date    = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.item_status    

    def save(self, *args, **kwargs):
        self.slug = slugify(self.item_status)
        return super().save(*args, **kwargs) 
    
    class Meta: 
        db_table = "ItemTags"



class Attribute(models.Model):
    name = models.CharField(max_length=100)  
    value = models.CharField(max_length=100)  

    def __str__(self):
        return f"{self.name}: {self.value}"



class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE, null=True, blank=True)
    
    item_name = models.CharField(max_length=255)
    generated_code = models.CharField(max_length=255)
    
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    retailer_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True)
    wholesale_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True)
    
    description = models.TextField(blank=True)
    size = models.CharField(max_length=255, blank=True)
    attribute = models.ManyToManyField(Attribute, related_name="items", blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="item_img/")
    availability = models.IntegerField(default=1)
    likes = models.ManyToManyField(customer_table, related_name='customer_likes', blank=True)
    tags = models.ManyToManyField(ItemTags, related_name='tag_items', blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    discount_percentage = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, blank=True)
    token_id = models.CharField(max_length=255, default=generate_unique_id)
    Userlogin = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=100, null=True, blank=True)
    qty_state = models.CharField(max_length=255, default="Quantify")

    def generate_unique_filename(self):
        import uuid
        import os
        from django.utils.text import slugify
        
        unique_key = uuid.uuid4().hex[:4]
        filename = f"{slugify(self.description)}_{unique_key}"
        if self.image:
            _, extension = os.path.splitext(self.image.name)
            filename += extension.lower()
        else:
            filename += ".jpg"
        return filename

    def save(self, *args, **kwargs):
        # Set image filename
        if self.image and self.description:
            filename = self.generate_unique_filename()
            self.image.name = os.path.join("", filename)

        # Ensure all prices are valid Decimal values, default to 0
        if not self.purchase_price or self.purchase_price is None:
            self.purchase_price = 0.00
        if not self.selling_price or self.selling_price is None:
            self.selling_price = 0.00
        if not self.retailer_price or self.retailer_price is None:
            self.retailer_price = 0.00
        if not self.wholesale_price or self.wholesale_price is None:
            self.wholesale_price = 0.00

        # Calculate discount percentage
        self.discount_percentage = self.calculate_discount_percentage()
        
        super().save(*args, **kwargs)

    def calculate_discount_percentage(self):
        from decimal import Decimal
        
        if self.selling_price and self.discount_price:
            selling_price = Decimal(str(self.selling_price))
            discount_price = Decimal(str(self.discount_price))
            
            if selling_price != 0:
                discount_pct = ((selling_price - discount_price) / selling_price) * 100
                if discount_pct > 100:
                    return discount_pct - 100
                return 100 - discount_pct
        
        return Decimal('0.00')

    class Meta:
        db_table = "Item"
        

class  fre_item_table(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.CharField(max_length=256)
    state = models.IntegerField(default=0)
    image = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'fre_item_table'

# make sure item slug is unique
def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
       instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Item)




class ItemImage(models.Model):
    item    = models.ForeignKey(Item, on_delete=models.CASCADE)
    image   = models.ImageField(upload_to='item_img/')  

    class Meta:
        db_table = "item_image"      


class ItemSpecification(models.Model):
    item_code   = models.CharField(max_length=255, null=True, blank=True)
    quality = models.CharField(max_length=255, null=True, blank=True) 
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        return self.quality
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.quality)
        return super(ItemSpecification, self).save(*args, **kwargs) 

    class Meta: 
        db_table = "ItemSpecification"



class ItemDetailDescription(models.Model):
    item_code   = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.item_code

    def save(self, *args, **kwargs):
        self.slug = slugify(self.text)
        return super(ItemDetailDescription, self).save(*args, **kwargs)
    
    class Meta: 
        db_table = "ItemDetailDescription"



class ItemSpecificationFeatures(models.Model):
    item_code = models.CharField(max_length=255, null=True, blank=True)
    key_features = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.key_features
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.key_features)
        return super(ItemSpecificationFeatures).save(*args, **kwargs) 
    
    class Meta: 
        db_table = "ItemSpecificationFeatures"




class ItemSize(models.Model):
    item_code   = models.CharField(max_length=255, null=True, blank=True)
    size   = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.size

    def save(self, *args, **kwargs):
        # self.slug = slugify(self.size)
        if self.slug is None and self.created_date and self.id:
            self.slug = self.created_date.strftime('75%Y%n%d23') + str(self.id)
        return super().save(*args, **kwargs)
    
    class Meta:
        db_table = "ItemSize"




class ItemBrand(models.Model):
    item_code   = models.CharField(max_length=255, blank=True)
    brand_name   = models.CharField(max_length=255, blank=True)
    slug = models.SlugField( blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.brand_name

    def save(self, *args, **kwargs):
        # self.slug = slugify(self.item_code)
        if self.slug is None and self.created_date and self.id:
            self.slug = self.created_date.strftime('75%Y%n%d23') + str(self.id)
        return super().save(*args, **kwargs)

    class Meta: 
        db_table = "ItemBrand"




class ItemColor(models.Model):
    item_code   = models.CharField(max_length=255, null=True, blank=True)
    color_name   = models.CharField(max_length=255, null=True, blank=True)
    color_code   = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.color_name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.color_name)
        return super(ItemCustomerReview).save(*args, **kwargs)
    
    class Meta: 
        db_table = "ItemColor"
 



class ItemCustomerReview(models.Model):
    item    = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer    = models.ForeignKey(customer_table, on_delete=models.CASCADE)
    star = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField()
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.text
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.text)
        return super(ItemCustomerReview).save(*args, **kwargs) 
    class Meta: 
        db_table = "ItemCustomerReview"




class Coupon(models.Model):
    code         = models.IntegerField(default=0)
    amount       = models.DecimalField(max_digits=65, decimal_places=2, default=0.00)
    limit        = models.CharField(max_length=100)
    usage        = models.CharField(max_length=100)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    created_by   = models.CharField(max_length=100)

    
    
    class Meta: 
        db_table = "coupon"

class  couponUsers(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=256)
    invoice = models.CharField(max_length=256)
    amount =  models.DecimalField(max_digits=65, decimal_places=2, default=0.0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=256, default='None')

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'couponUsers'

class Check_StockLevel_By(models.Model):
    level        = models.CharField(max_length=100)

    class Meta: 
        db_table = "check_stock_level_by"


class  cat_payment_method(models.Model):
    name = models.CharField(max_length=256)
    state = models.CharField(max_length=256, default='0')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        # app_label = 'afrikbook_server'
        db_table = 'cat_payment_method'






