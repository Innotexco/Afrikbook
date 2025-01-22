

from django.urls import path, include
# from rest_framework import routers
# from .views import CustomerViewSet
from . import views
from . functions.newsales import invoiceExist

# route = routers.DefaultRouter()
# route.register(r'customer', CustomerViewSet)

app_name = 'customer'

urlpatterns = [
    #customer urls
    path('Customers', views.Customers, name='Customers'),
    path('Newcustomer', views.AddCustomer, name='NewCustomer'),
    path('Update/<int:id>/', views.UpdateCustomer, name='updateCustomer'),
    path('Delete/<int:id>/', views.delete_customer, name='delete-customer'),
    path('CustomerOpeningBalance', views.CusOpenBalance, name='CustomerOpeningBalance'),
    path('RefundCustomer', views.RefundCustomer, name='RefundCustomer'),
    path('view-returns-inwards', views.ViewReturnsInWards, name='ViewReturnsInWards'),
    path('ReturnInward', views.ReturnInward, name='ReturnInward'),
    path('ViewReturnItem/<int:code>/<str:invoice>/', views.ViewCustomerReturnedItem, name='ViewReturnItem'),
    path('ReturnInwwardChangeDate/', views.ReturnedInwardChangeDate, name='ReturnInwwardChangeDate'),
    path('ChangeReturnInwardDate/', views.ChangeReturnInwardDate, name='ChangeReturnInwardDate'),

    #sales invoice urls
    path('NewSales', views.SalesInvoice, name='NewSales'),

    #sales quote urls
    path('NewSalesQuote', views.AddSalesQuote, name='NewSalesQuote'),
    path('SalesQuote', views.SalesQuote, name='SalesQuote'),
    # path('Update/<int:id>/', views.UpdateCustomer, name='updateCustomer'),
    # path('Delete/<int:id>/', views.delete_customer, name='delete-customer'),
    
    #sales order urls
    path('NewSalesOrder', views.AddSalesOrder, name='NewSalesOrder'),
    path('SalesOrder', views.SalesOrder, name='SalesOrder'),

    #sales invoice urls
    path('VerifiedPayment', views.VerifiedPayment, name='VerifiedPayment'),
    path('VerifyPayment', views.VerifyPayment, name='VerifyPayment'),
    path('Verify', views.Verify, name='Verify'),#ajax


    path('get_customer/<int:id>/', views.GetCustomerDetails, name='customer-details'), #ajax
    path('get_vendor/<str:id>/', views.GetVendorDetails, name='vendor-details'), #ajax
    path('customer/<int:id>/', views.ViewCustomerDetails, name='customer-details'), #ajax
    path('get_items/<int:item_id>/', views.GetItemDetails, name='item-details'), #ajax
    path('get_return_items/<str:invoice>/<int:item_id>/', views.GetReturnItemDetails, name='item-get_return_items'), #ajax
    path('invoice/<int:invoice_id>/', views.GetInvoiceDetails, name='invoice'), #ajax  

    path('get_items_qty', views.CheckItemQty, name='item-qty'), #ajax
    path('Stockget_items_qty', views.StockCheckItemQty, name='Stockitem-qty'), #ajax
    path('get_customer_balance/<int:id>/', views.GetCustomerBalance, name='customer-balance'), #ajax
    path('get_customer_or_vendor_balance', views.GetCustomer_or_VendorBalance, name='get_customer_or_vendor_balance'), #ajax
    path('invoiceExist/<int:invoiceID>/', invoiceExist, name='invoiceExist'), #ajax
    path('CancelSales', views.CancelSales, name='CancelSales'), #ajax
    path('Edit_incoice', views.Edit_incoice, name='Edit_incoice'), #ajax
    path('supply_pending_invoice', views.supply_pending_invoice, name='supply_pending_invoice'), #ajax
    
    
    path('get_shipping_cost/<int:itemcode>/<int:city>/', views.get_shipping_cost, name='get_shipping_cost'), #ajax

]


