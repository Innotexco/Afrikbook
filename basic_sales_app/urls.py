from django.urls import path, include
from . import views
from basic_sales_app.functions.Function_Hub import *;

app_name = 'basic_sales_app'

urlpatterns = [
    path('basicSalePoint', views.basicSalePoint, name='basicSalePoint'),
    path('SalesMenu', views.SaleMenu, name='SalesMenu'),
    path('fetch_all_items', views.fetch_all_items, name='fetch_all_items'),
    path('SalesHistory', views.SalesHistory, name='SalesHistory'),
    path('edit_sales_history/<int:pk>', views.edit_sales_history, name='edit_sales_history'),
    path('CancelSales', views.CancelSales, name='CancelSales'),
    path('AddItemForSales', views.AddItemForSales, name='AddItemForSales'),
    path('stockIn', views.stockIn, name='stockIn'),
    path('stockin_history', views.stockin_history, name='stockin_history'),
    path('update_item/<int:pk>', views.update_item, name='update_item'),
    path('add_profile', views.add_profile, name='add_profile'),
    path('add_customer', views.add_customer, name='add_customer'),
    path('customer_history', views.customer_history, name='customer_history'),
    path('account_recievable', views.account_recievable, name='account_recievable'),
    path('get_account_receiables', get_account_receiables, name='get_account_receiables'),
    path('UpdateCancelSales', UpdateCancelSales, name='UpdateCancelSales'),
    path('Search_for_sales', Search_for_sales, name='Search_for_sales'),
    path('ItemCategory', views.ItemCategory, name='ItemCategory'),
    path('editCategory/<int:pk>', views.edit_category, name='editCategory'),
    path('view_item/<int:pk>', views.view_item, name='View_item'),
    path('fetch_default', fetch_items_by_default, name='fetch_default'),
    path('edit_customer/<int:pk>', views.edit_customer, name='edit_customer'),
    path('deleteAccount', deleteAccount, name='deleteAccount'),
    path('Delete_Stockin_History', Delete_Stockin_History, name='Delete_Stockin_History'),
    path('Scanned_code', Scanned_code, name='Scanned_code'),
    path('Sales_history_details/<slug:slug>', views.Sales_history_details, name='Sales_history_details'),
    path('Cus_Sales_history_details/<slug:slug>', views.Cus_Sales_history_details, name='Cus_Sales_history_details'),
    path('Delete_sales_history', Delete_sales_history, name='Delete_sales_history'),
    path('Sales_Data', Sales_Data, name='Sales_Data'),
    path('edit_user', edit_user, name='edit_user'),
    path('Delete_user', Delete_user, name='Delete_user'),
    path('add_user', views.add_user, name='add_user'),
    path('autovat', views.autovat, name='autovat'),
    path('checkout_summary', views.checkout_summary, name='checkout_summary'),
    path('itemSearch', itemSearch, name='itemSearch'),
    path('Delete_Item', Delete_Item, name='Delete_Item'),
    path('authAmount', views.authAmount, name='authAmount'),
    path('OutletStockLevel', views.OutletStockLevel, name='OutletStockLevel'),
]