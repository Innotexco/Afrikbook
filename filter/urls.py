from django.urls import path, include
# from rest_framework import routers
# from .views import CustomerViewSet
from . import views, vendor_views

# route = routers.DefaultRouter()
# route.register(r'customer', CustomerViewSet)

app_name = 'filter'

urlpatterns = [
    # Customer
    path('sales-date/', views.sales_filter_by_date, name='date'), #ajax
    path('sales/<str:value>/', views.sales_filter, name='sales'), #ajax

    path('return-inward-date/', views.return_inwards_filter_by_date, name='return-inward-date'), #ajax
    path('journal-entry-date/', views.journal_entry_filter_by_date, name='journal-entry-date'), #ajax


    path('receivable-date/', views.receivable_filter_by_date, name='receivable-date'), #ajax
    path('receivable/<str:value>/', views.recievable_filter, name='receivable'), #ajax
    path('aged-receivable-date/', views.aged_receivable_filter_by_date, name='aged-receivable-date'), #ajax
    path('aged-receivable/<str:value>/', views.aged_recievable_filter, name='aged-receivable'), #ajax
   
    path('sales-report-date/', views.sales_report_filter_by_date, name='sales-report-date'), #ajax
    path('sales-quote-date/', views.sales_quote_filter_by_date, name='sales-quote-date'), #ajax
    path('sales-order-date/', views.sales_order_filter_by_date, name='sales-order-date'), #ajax

    path('profit-loss/', views.profit_loss_filter_by_date, name='profit-loss'), #ajax

    path('customers-ledger/', views.customers_ledger_filter_by_date, name='customers-ledger'), #ajax
    path('customer-ledger/', views.customer_ledger_filter_by_date, name='customer-ledger'), #ajax
    path('sales-ladger-date/', views.sales_ladger_filter_by_date, name='sales-ladger-date'), #ajax
    

    # Vendor
    # path('purchase-date/', vendor_views.purchase_filter_by_date, name='purchse-date'), #ajax
    path('purchase/<str:value>/', vendor_views.purchase_filter, name='purchase'), #ajax

    path('return-inward-date/', views.return_inwards_filter_by_date, name='return-inward-date'), #ajax


    path('payables-date/', vendor_views.payables_filter_by_date, name='payables-date'), #ajax
    path('payables/<str:value>/', vendor_views.payables_filter, name='payables'), #ajax
    path('aged-payables-date/', vendor_views.aged_payables_filter_by_date, name='aged-payables-date'), #ajax
    path('aged-payables/<str:value>/', vendor_views.aged_payables_filter, name='aged-payables'), #ajax
   
    path('purchase-report-date/', vendor_views.purchase_report_filter_by_date, name='purchase-report-date'), 
    # path('purchase-report/<str:value>/', vendor_views.purchase_report_filter, name='purchase-report'), #ajax
    #ajpurchaseath('sales-order-date/', views.sales_order_filter_by_date, name='sales-order-date'), #ajax

    path('profit-loss/', views.profit_loss_filter_by_date, name='profit-loss'), #ajax

    path('vendors-ledger/', vendor_views.vendors_ledger_filter_by_date, name='vendors-ledger'), #ajax
    path('vendor-ledger/', vendor_views.vendor_ledger_filter_by_date, name='vendor-ledger'), #ajax
    path('purchase-ladger-date/', vendor_views.purchase_ladger_filter_by_date, name='purchase-ladger-date'), #ajax
]