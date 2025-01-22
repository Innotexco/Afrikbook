from django.urls import path, include
from . import views


app_name = 'settings'

urlpatterns = [
    path('price-management-history', views.PriceChangeHistory, name='price-management-history'),
    path('PriceManagement', views.AddPriceChangeHistory, name='PriceManagement'),
    path('update/<int:id>/', views.UpdatePriceChangeHistory, name='update-price-history'),
    # path('delete/<int:id>/', views.delete_employee, name='delete-employee'),

    path('NewCompany_details', views.AddCompanyDetails, name='NewCompany_details'),
    path('update/company_detail/<int:id>/', views.UpdateCompanyDetails, name='update-company_detail'),
    path('delete/company_detail/<int:id>/', views.DeleteCompanyDetails, name='delete-company_detail'),

    path('SalesOutlet', views.SalesOutlet, name='SalesOutlet'),
    path('NewSalesOutlet', views.AddSalesOutlet, name='NewSalesOutlet'),
    path('update/sales/<int:id>/', views.UpdateSalesOutlet, name='update-salesoutlet'),
    path('delete/sales/<int:id>/', views.DeleteSalesOutlet, name='delete-salesoutlet'),

    path('View-Profile', views.ViewProfile, name='ViewProfile'),
    path('Profile-Setup', views.Create_UpdateNewProfile, name='ProfileSetup'),

    
    path('ShippingAddress', views.Shipping_Address, name='ShippingAddress'),
    path('update/ShippingAddress/<int:id>/', views.UpdateShippingAddress, name='UpdateShippingAddress'),
    path('delete/ShippingAddress/<int:id>/', views.DeleteShippingAddress, name='DeleteShippingAddress'),

    path('BillingAddress', views.Billing_Address, name='BillingAddress'),
    path('update/BillingAddress/<int:id>/', views.UpdateBillingAddress, name='UpdateBillingAddress'),
    path('delete/BillingAddress/<int:id>/', views.DeleteBillingAddress, name='DeleteBillingAddress'),

    path('Add-Warehouse', views.AddWarehouse, name='AddWarehouse'),

    path('instantStockout', views.instantStockout, name='instantStockout'),

    # Expiration Control
    path('SetItemNotification', views.SetItemNotify, name='SetItemNotification'),
    path('NotificationStatus', views.NotificationStatus, name='NotificationStatus'),
    path('notification_filter_by_date', views.notification_filter_by_date, name='notification_filter_by_date'),
    path('notification_filter/<str:value>/', views.notification_filter, name='notification_filter'),
    path('ItemExpiryDate', views.ItemExpiryDate, name='ItemExpiryDate'),
    path('UpdateItemExpiryDate', views.UpdateItemExpiryDate, name='UpdateItemExpiryDate'),
    path('ItemExpiryDate_filter/<str:value>', views.ItemExpiryDate_filter, name='ItemExpiryDate_filter'),
    path('UpdateItemExpiryDate_filter/<str:value>', views.UpdateItemExpiryDate_filter, name='UpdateItemExpiryDate_filter'),
    path('InspirationControl', views.InspirationControl, name='InspirationControl'),
    path('InspirationControlFilter/<str:value>/', views.InspirationControlFilter, name='InspirationControlFilter'),
    path('ChangeStatus', views.ChangeStatus, name='ChangeStatus'),
    path('ExpiryDateReminder', views.ExpiryDateReminder, name='ExpiryDateReminder'),
    path('ViewExpiredItems', views.ViewExpiredItems, name='ViewExpiredItems'),
    path('DeleteExpiredItems', views.DeleteExpiredItems, name='DeleteExpiredItems'),
    path('DeleteExpiredItem/<str:invoice_no>/<int:item_code>', views.DeleteExpiredItem, name='DeleteExpiredItem'),
    path('ViewAboutToExpireItems', views.ViewAboutToExpireItems, name='ViewAboutToExpireItems'),
    
    path('get_user_currency', views.get_user_currency, name='get_user_currency'),
    path('complete_profileSetup', views.complete_profileSetup, name='complete_profileSetup'),

    path('ShippingMethod', views.ShippingMethod, name='ShippingMethod'),
    path('CartPaymentMethod', views.CartPaymentMethod, name='CartPaymentMethod'),
    path('PickupStation', views.PickupStation, name='PickupStation'),
    path('AddCity', views.AddCity, name='AddCity'),
    path('PickupShippingPrice', views.PickupShippingPrice, name='PickupShippingPrice'),
    path('AddressShippingPrice', views.AddressShippingPrice, name='AddressShippingPrice'),

    path('fetch_locations', views.fetch_locations, name='fetch_locations'),
    path('fetch_cities', views.fetch_cities, name='fetch_cities'),
    path('update_address_shipping_price', views.update_address_shipping_price, name='update_address_shipping_price'),
    path('ChangeCartMethosState', views.ChangeCartMethosState, name='ChangeCartMethosState'),

]