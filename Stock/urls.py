from django.urls import path

# from .views import *
from Stock import views

app_name="Stock"

urlpatterns = [
    # path('', views.home, name='home'),
    # Stock
    path('Item-Issue', views.ItemIssue, name='ItemIssue'),
    path('Transfer-to-a-warehouse', views.WarehouseToWarehouse, name='WarehouseToWarehouse'),
    path('Transfer-to-an-outlet', views.WarehouseToOutlet, name='WarehouseToOutlet'),
    path('Transfer-from-outlet-warehouse', views.OutletToWarehouse, name='OutletToWarehouse'),
    path('Transfer-from-outlet-to-outlet', views.OutletToOutlet, name='OutletToOutlet'),
    path('New-Item', views.NewItem, name='NewItem'),
    path('Item-Category', views.ItemCategory, name='ItemCategory'),
    path('Verify-Transfer', views.VerifyTransfer, name='VerifyTransfer'),
    path('Transfer-History', views.TransferHistory, name='TransferHistory'),
    path('outlet-stock-level', views.OutletStockLevel, name='OutletStockLevel'),
    path('warehouse-stock-level', views.WarehouseStockLevel, name='WarehouseStockLevel'),
    path('stock-level-comparison', views.StockLevelComparison, name='StockLevelComparison'),
    path('stock-adjustment', views.StockAdjustment, name='StockAdjustment'),
    path('stock-adjustment-outlet', views.StockAdjustmentOutlet, name='StockAdjustmentOutlet'),
    path('Delete-Item', views.DeleteItem, name='DeleteItem'),
    path('instant-Transfer', views.instantTransfer, name='instantTransfer'),
    path('Check-Stocklevelby', views.checkstocklevelby, name='checkstocklevelby'),
    path('Coupon', views.coupon, name='Coupon'),
    path('NewStockin', views.NewStockin, name='NewStockin'),



    path('item/edit/<int:item_id>/', views.Update_Item, name='update_item'),

    path('add_item_tag/', views.add_item_tag, name='add_item_tag'),
    path('add_item_size/', views.add_item_size, name='add_item_size'),
    path('add_item_description/', views.add_item_description, name='add_item_description'),
    path('add_item_specification/', views.add_item_specification, name='add_item_specification'),
    path('add_item_brand/', views.add_item_brand, name='add_item_brand'),
    path('add_coupon/', views.AddCoupon, name='add_coupon'),
    path('edit_coupon/', views.EditCoupon, name='edit_coupon'),
    path('delete_coupon/<int:id>', views.DeleteCoupon, name='delete_coupon'),
    path('add_item_color/', views.add_item_color, name='add_item_color'),
    
    path('item/detail/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/delete/<int:id>/', views.DeleteItem, name='delete_item'),
    


    path('Edit-Item-Category/<int:id>/', views.EditItemCategory, name='UpdateItemCategory'),

    path('update-item-category/', views.update_item_category, name='SubCategory'),
    path('fetch-subcategories/<int:category_id>/', views.fetch_subcategories, name='fetch_subcategories'),
    path('category-details/<int:category_id>/', views.category_details, name='category_details'),
    path('get_sub_category/<str:category_id>/', views.get_sub_category, name='get_sub_category'),

    # # Customer
    # path('StockCustomers', views.Customers, name='StockCustomers'),
    # path('StockNewcustomer', views.AddCustomer, name='StockNewCustomer'),
    # path('StockUpdate/<int:id>/', views.UpdateCustomer, name='StockupdateCustomer'),
    # path('StockDelete/<int:id>/', views.delete_customer, name='Stockdelete-customer'),

    # # Vendor
    # path('Stockadd-vendor/', views.register_vendor, name='Stockregister_vendor'),
    # path('Stockvendor/edit/<int:id>', views.update_vendor, name='Stockupdate_vendor'),
    # path('Stockview-vendor/', views.view_vendor, name='Stockview_vendor'),
    # path('Stockvendor/delete/<int:id>', views.delete_vendor, name='Stockdelete_vendor'),

    # path('Stock', views.Stock, name='Stock'),
    # path('NewStockin', views.NewStockin, name='NewStockin'),
    # path('ViewStockin', views.Stockin, name='ViewStockin'),
    # path('NewStockout', views.NewStockout, name='NewStockout'),
    # path('ViewStockout', views.Stockout, name='ViewStockout'),
    # path('ReleaseOrder', views.ReleaseOrder, name='ReleaseOrder'),
    # path('order/<str:order>/', views.GetOrderDetails, name='order'),

    # path('StockNew-Item', views.StockNewItem, name='StockNewItem'),
    # path('Stockitem/edit/<int:item_id>/', views.StockUpdate_Item, name='Stockupdate_item'),

    # path('StockItem-Category', views.StockItemCategory, name='StockItemCategory'),
    # path('StockEdit-Item-Category/<int:id>/', views.StockEditItemCategory, name='StockUpdateItemCategory'),


    # path('StockNew-User', views.NewUser, name='StockNewUser'),
    # path('StockEdit-User', views.EditUser, name='StockEditUser'),

    # path('StockAddWarehouse', views.StockAddWarehouse, name='StockAddWarehouse'),

    # path('stockin-date/', views.stockin_filter_by_date, name='stockin-date'), #ajax
    # path('stockin/<str:value>/', views.stockin_filter, name='stockin'), #ajax
    # path('view-stockin/<str:invoice>/', views.ViewStockin, name='view-stockin'), #ajax

    # path('stockout-date/', views.stockout_filter_by_date, name='stockout-date'), #ajax
    # path('stockout/<str:value>/', views.stockout_filter, name='stockout'), #ajax
    # path('view-stockout/<str:invoice>/', views.ViewStockout, name='view-stockout'), #ajax





]  



