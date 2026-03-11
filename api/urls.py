from django.urls import path
from .views import *
# from afrikbook_server.views import *
from django.conf.urls.static import static
from django.conf import settings

app_name ="api"

urlpatterns = [
    path('api/item_api/', item, name='item_api'),
    path('api/customers/create/', create_customer_api, name='create_customer_api'),
    path('api/check-item-qty/', check_item_qty, name='check_item_qty'),
    path('initial-data/', sales_invoice_initial_data, name='initial_data'),
    path('api/create/', create_sales_invoice_api, name='create_invoice'),
    path('check-invoice/<str:invoiceID>/', check_invoice_exists, name='check_invoice'),

    path('api/invoices/<str:invoice_id>/', get_invoice_detail_api, name='api_invoice_detail'),
    path('api/orders/<str:order_id>/invoices/', get_invoice_by_order_api, name='api_order_invoices'),
    path('api/customers/<int:customer_id>/invoices/', get_customer_invoices_api, name='api_customer_invoices'),
    path('api/customers/<int:customer_id>/invoices/summary/', get_customer_invoice_summary_api, name='api_customer_invoice_summary'),
    path('api/search_invoices/searches/', search_invoice_api, name='api_invoice_search'),
    path('api/invoices/<str:invoice_id>/download/', download_invoice_pdf_api, name='api_invoice_download'),
    
    # path('invoice/<str:invoice_id>/', invoice_detail_view, name='invoice_detail'),
    # path('orders/<str:order_id>/invoices/', my_invoices_view, name='order_invoices'),
    # path('customers/<int:customer_id>/invoices/', customer_invoices_view, name='customer_invoices'),
]
    #path("api/", dashboard, name="client-dashboard"),
    # path("orderfew/", getorderFewEncrypt, name="getorderFewEncrypt"),
    # path("invoicefew/", getinvoiceFewEncrypt, name="getinvoiceFewEncrypt"),
    # path("test/", Decrypt, name="Encrypt"),

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)