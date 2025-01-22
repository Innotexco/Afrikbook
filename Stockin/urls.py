from django.urls import path

# from .views import *
from Stockin import views, settings_view

app_name="Stockin"

urlpatterns = [
    path('Stockregister', views.register_user, name='Stockregister'),

    path('Stocklogin', views.Login, name='Stocklogin'),

    path('StockLogout/', views.logout_user, name='Stocklogout'),

    path('Migration', views.MigrationPage, name='Migration'),

    # Company
    path('Company', views.Company, name='Company'),
    path('NewCompany', views.AddCompany, name='NewCompany'),
    path('StockinUpdate/<int:id>/', views.UpdateCompany, name='updateCompany'),
    path('StockinDelete/<int:id>/', views.delete_Company, name='delete-company'),


    path('Stockin', views.Stock, name='Stockin'),
    path('NewStockin', views.NewStockin, name='NewStockin'),
    path('ViewStockin', views.Stockin, name='ViewStockin'),
    path('NewStockout', views.NewStockout, name='NewStockout'),
    path('ViewStockout', views.Stockout, name='ViewStockout'),
    path('ReleaseOrder', views.ReleaseOrder, name='ReleaseOrder'),
    path('InstantStockour', views.InstantStockour, name='InstantStockour'),
    path('order/<str:order>/', views.GetOrderDetails, name='order'),

    path('StockNew-Item', views.StockNewItem, name='StockNewItem'),
    path('Stockitem/edit/<int:item_id>/', views.StockUpdate_Item, name='Stockupdate_item'),
    path('Stockitem/delete/<int:item_id>/', views.StockDeleteItem, name='Stockdelete_item'),

    path('StockItem-Category', views.StockItemCategory, name='StockItemCategory'),
    path('StockEdit-Item-Category/<int:id>/', views.StockEditItemCategory, name='StockUpdateItemCategory'),


    path('StockNew-User', views.NewUser, name='StockNewUser'),
    path('StockEdit-User', views.EditUser, name='StockEditUser'),

    path('StockAddWarehouse', views.StockAddWarehouse, name='StockAddWarehouse'),

    path('stockin-date/', views.stockin_filter_by_date, name='stockin-date'), #ajax
    path('stockin/<str:value>/', views.stockin_filter, name='stockin'), #ajax
    path('view-stockin/<str:invoice>/', views.ViewStockin, name='view-stockin'), #ajax

    path('stockout-date/', views.stockout_filter_by_date, name='stockout-date'), #ajax
    path('stockout/<str:value>/', views.stockout_filter, name='stockout'), #ajax
    path('view-stockout/<str:invoice>/', views.ViewStockout, name='view-stockout'), #ajax


    # Expiration Control
    path('SSetItemNotification', settings_view.SetItemNotify, name='SSetItemNotification'),
    path('SNotificationStatus', settings_view.NotificationStatus, name='SNotificationStatus'),
    path('Snotification_filter_by_date', settings_view.notification_filter_by_date, name='Snotification_filter_by_date'),
    path('Snotification_filter/<str:value>/', settings_view.notification_filter, name='Snotification_filter'),
    path('SItemExpiryDate', settings_view.ItemExpiryDate, name='SItemExpiryDate'),
    path('SUpdateItemExpiryDate', settings_view.UpdateItemExpiryDate, name='SUpdateItemExpiryDate'),
    path('SItemExpiryDate_filter/<str:value>', settings_view.ItemExpiryDate_filter, name='SItemExpiryDate_filter'),
    path('SUpdateItemExpiryDate_filter/<str:value>', settings_view.UpdateItemExpiryDate_filter, name='SUpdateItemExpiryDate_filter'),
    path('SInspirationControl', settings_view.InspirationControl, name='SInspirationControl'),
    path('SInspirationControlFilter/<str:value>/', settings_view.InspirationControlFilter, name='SInspirationControlFilter'),
    path('SChangeStatus', settings_view.ChangeStatus, name='SChangeStatus'),
    path('SExpiryDateReminder', settings_view.ExpiryDateReminder, name='SExpiryDateReminder'),
    path('SViewExpiredItems', settings_view.ViewExpiredItems, name='SViewExpiredItems'),
    path('SDeleteExpiredItems', settings_view.DeleteExpiredItems, name='SDeleteExpiredItems'),
    path('SDeleteExpiredItem/<str:invoice_no>/<int:item_code>', settings_view.DeleteExpiredItem, name='SDeleteExpiredItem'),
    path('SViewAboutToExpireItems', settings_view.ViewAboutToExpireItems, name='SViewAboutToExpireItems'),





]  



