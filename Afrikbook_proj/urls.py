"""
URL configuration for Afrikbook_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("main.urls")),
    path('', include('customer.urls', namespace='customer')),
    path('', include('settings.urls', namespace='settings')),
    path('', include('employee.urls', namespace='employee')),
    path('', include('journal.urls', namespace='journal')),
    path('', include('report.urls', namespace='report')),
    path('', include('filter.urls', namespace='filter')),
    path('', include('vendor.urls', namespace='vendor')),
    path('', include('account.urls', namespace='account')),
    # path('', include('widget.urls', namespace='widget')),
    path('', include('Stock.urls', namespace='Stock')),
    path('', include('Stockin.urls', namespace='Stockin')),
    path('', include('basic_sales_app.urls', namespace='basic_sales_point')),
    path('', include('client.urls', namespace='afrikbook_client')),
    # path('', include('api.urls', namespace='api')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
