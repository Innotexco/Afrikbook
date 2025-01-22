from django.urls import path

# from .views import *
from vendor.views import *

app_name="vendor"


urlpatterns = [
    # path('get_supplier_info/<int:id>/', GetSupplierDetails, name='supplier-details'), #ajax

    path('get_items_vendor/<int:item_id>/', GetItemDetails, name='item-details'), #ajax

    path('get_vendors/<str:id>/',GetVendorDetails, name='VendorDetails'), #ajax
    path('GetInvoiceDetails/<str:invoice_id>/',GetInvoiceDetails, name='GetInvoiceDetails'), #ajax
    path('GetReturnOutwardItemDetails/<str:invoice>/<int:item_id>/',GetReturnOutwardItemDetails, name='GetReturnOutwardItemDetails'), #ajax
    path('new-purchase/', NewPurchase, name='NewPurchase'),
    path('purchase-adjustment/', PurchaseAdjustment, name='PurchaseAdjustment'),
    path('cancle-purchase/', CanclePurchaseInvoice, name='CanclePurchaseInvoice'),
    path('view-cancle-purchase/', viewCanclePurchase, name='viewCanclePurchase'),
    path('new-purchase-quote', NewPurchaseQuote, name='NewPurchaseQuote'),
    path('view-purchase-quote/', ViewPurchaseQuote, name='ViewPurchaseQuote'),
    path('update-purchase-quote/<str:pk>/', UpdatePurchaseQuote, name='UpdatePurchaseQuote'),
    path('new-purchase-order',NewPurchaseOrder, name='NewPurchaseOrder'),
    path('view-purchase-order',ViewPurchaseOrder, name='ViewPurchaseOrder'),
    path('return-items', ReturnItems, name='ReturnItems'),
    path('return-outwards', ViewReturnOutwards, name='ViewReturnOutwards'),

    path('add-vendor/', register_vendor, name='register_vendor'),
    path('vendor/edit/<int:id>', update_vendor, name='update_vendor'),
    path('view-vendor/', view_vendor, name='view_vendor'),
    path('vendor/delete/<int:id>', delete_vendor, name='delete_vendor'),
    path('view_user_information/<str:username>/', view_user_information, name='view_user_information'),
    
]  
