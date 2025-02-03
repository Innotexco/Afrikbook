
from django.urls import path, include
from . import views
from . import api

app_name = 'afrikbook_client'

urlpatterns = [
    path('address', api.shipping_address_api, name='address'), #ajax
    path('get_shipping_address/<int:customer_id>/', api.get_shipping_address, name='get_shipping_address'), #ajax
    path('create_new_customer', api.create_new_customer, name='create_new_customer'), #ajax
    path('create_new_shippping_address', api.create_new_shippping_address, name='create_new_shippping_address'), #ajax

    path('Customer/Dashboard', views.home, name='CustomerDashboard'),
    path('PendingInvoice', views.PendingInvoice, name='PendingInvoice'),
    path('TransitInvoice', views.TransitInvoice, name='TransitInvoice'),
    path('SuppliedInvoice', views.SuppliedInvoice, name='SuppliedInvoice'),
    path('SalesInvoice', views.SalesInvoice, name='SalesInvoice'),
    
]




# Afrik!24


#ses-smtp-user.20250128-111643

#AKIARSU7KXMCVSJNHFMR

#BK9PkGX/S7zyEOfBWmt6CZP4I7FYTNNmKc/BKTP2xlbt



#K9PkGX/S7zyEOfBWmt6CZP4I7FYTNNmKc/BKTP2xlbt