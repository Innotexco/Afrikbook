from django.shortcuts import render
from django.http import JsonResponse
from . models import *
import requests, json
from main.models import *
from customer.models import *
from Stock.models import *
from settings.models import  ExpiryDate

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Sum, Q
from customer.functions.generalFunction import ReduceOutletStockinItemQuantity
from filter.function.date import convertDate
# Create your views here.


@login_required(login_url="/")
def home(request):
    db = request.user.company_id.db_name
  
 
    today = date.today()

    customers = customer_table.objects.using(db).count()
    all_sales = customer_invoice.objects.using(db).values("invoiceID").distinct().count()
    orders = sales_order.objects.using(db).values("order_ID").distinct().count()
    pending_invoice = customer_invoice.objects.using(db).filter(invoice_state="Pending").values("invoiceID").distinct().count()
    on_transit_invoice = customer_invoice.objects.using(db).filter(invoice_state="On Transit").values("invoiceID").distinct().count()
    supplied_invoice = customer_invoice.objects.using(db).filter(invoice_state="Supplied").values("invoiceID").distinct().count()
    

    sales = customer_invoice.objects.using(db).filter(invoice_date__date=today).values("invoiceID").distinct()
   
    distinct_sales = []

    for sale in sales:
        new_data =  customer_invoice.objects.using(db).filter(invoiceID=sale["invoiceID"]).values()
        amount_expected =  customer_invoice.objects.using(db).filter(invoiceID=sale["invoiceID"]).first().amount_expected
        amount_paid =  customer_invoice.objects.using(db).filter(invoiceID=sale["invoiceID"]).first().amount_paid
        if amount_expected:
           total = amount_expected 
        else:
            total = amount_paid

    

        def get_customer_or_vendor():
            invoice = customer_invoice.objects.using(db).filter(invoiceID=sale['invoiceID']).first()
          
            if customer_table.objects.using(db).filter(customer_code=invoice.cusID):
                # return "Customer"
                return  customer_table.objects.using(db).get(customer_code=invoice.cusID).email or "No email"
            # elif vendor_table.objects.using(db).filter(custID=invoice.cusID):
            #     return vendor_table.objects.using(db).get(custID=invoice.cusID).email or "No email"
            else:
                return "No email"

        accountType = get_customer_or_vendor()
        
        

        if new_data.exists():
            new_data = new_data.first()
            new_data['customer_email'] = accountType
            new_data['total'] = total
            distinct_sales.append(new_data)

    # for pagination
    page = request.GET.get('page', 1)

    paginator = Paginator(distinct_sales, 4)
    try:
        distinct_sales = paginator.page(page)
    except PageNotAnInteger:
        distinct_sales = paginator.page(1)
    except EmptyPage:
        distinct_sales = paginator.page(paginator.num_pages)

    context = {
        'total_customers':customers,
        'all_sales':all_sales,
        'orders': orders,
        'sales':distinct_sales,
        'pending': pending_invoice,
        'transit': on_transit_invoice,
        'supplied': supplied_invoice
        
    }
    
    return render(request, 'client/home.html', context)

def PendingInvoice(request):
    db = request.user.company_id.db_name
    

    if request.method == "POST":
        invoiceID = request.POST.get('invoiceID')
        invoice_state = request.POST.get('state')
        if invoice_state == '1':
            queryset = customer_invoice.objects.using(db).filter(invoiceID=invoiceID)
            
            for item in queryset:
                ReduceOutletStockinItemQuantity(db, item.outlet, item.itemcode, item.qty)
            customer_invoice.objects.using(db).filter(invoiceID=invoiceID).update(invoice_state="On Transit")

        
        invoice = customer_invoice.objects.using(db).filter(invoice_state="Pending").values()
        
        return JsonResponse(list(invoice), safe=False)
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        customer = request.GET.get('customer')
        
        
        filter_conditions = Q()
    
        if start_date_str and end_date_str:
            pass
            filter_conditions &= Q(invoice_date__date__range=(convertDate(start_date_str, end_date_str)))
    
        if customer:
            
            filter_conditions &= Q(cusID=customer)
        
     
        if filter_conditions: 
            invoice = customer_invoice.objects.using(db).filter(filter_conditions, invoice_state="Pending").values()

            data = []
            for item in invoice:
                if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                    data.append(item)

            return JsonResponse(list(data), safe=False)
        else:
            invoice = customer_invoice.objects.using(db).filter(invoice_state="Pending")

    data = []
    for item in invoice:
        if item.invoiceID not in [d.invoiceID for d in data]:
            data.append(item)
    
    context = {
        'invoice': data,
        'customers': customer_table.objects.using(db)
    }

    return render(request, 'client/PendingInvoice.html', context)


def TransitInvoice(request):
    db = request.user.company_id.db_name
    

    if request.method == "POST":
        invoiceID = request.POST.get('invoiceID')
        invoice_state = request.POST.get('state')
        if invoice_state == '1':
            queryset = customer_invoice.objects.using(db).filter(invoiceID=invoiceID)
            
            for item in queryset:
                ReduceOutletStockinItemQuantity(db, item.outlet, item.itemcode, item.qty)
            customer_invoice.objects.using(db).filter(invoiceID=invoiceID).update(invoice_state="On Transit")

        
        invoice = customer_invoice.objects.using(db).filter(invoice_state="Pending")
        
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        customer = request.GET.get('customer')
        
        
        filter_conditions = Q()
    
        if start_date_str and end_date_str:
            # pass
            filter_conditions &= Q(invoice_date__date__range=(convertDate(start_date_str, end_date_str)))
    
        if customer:
            
            filter_conditions &= Q(cusID=customer)
        
     
        if filter_conditions: 
            invoice = customer_invoice.objects.using(db).filter(filter_conditions, invoice_state="On Transit").values()

            data = []
            for item in invoice:
                if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                    data.append(item)

            return JsonResponse(list(data), safe=False)
        else:
            invoice = customer_invoice.objects.using(db).filter(invoice_state="On Transit")

    data = []
    for item in invoice:
        if item.invoiceID not in [d.invoiceID for d in data]:
            data.append(item)

    context = {
        'invoice': data,
        'customers': customer_table.objects.using(db)
    }

    return render(request, 'client/OnTransitInvoice.html', context)


def SuppliedInvoice(request):
    db = request.user.company_id.db_name
    

    if request.method == "POST":
        invoiceID = request.POST.get('invoiceID')
        invoice_state = request.POST.get('state')
        if invoice_state == '1':
            queryset = customer_invoice.objects.using(db).filter(invoiceID=invoiceID)
            
            for item in queryset:
                ReduceOutletStockinItemQuantity(db, item.outlet, item.itemcode, item.qty)
            customer_invoice.objects.using(db).filter(invoiceID=invoiceID).update(invoice_state="On Transit")

        
        invoice = customer_invoice.objects.using(db).filter(invoice_state="Pending")
        
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        customer = request.GET.get('customer')
        
        
        filter_conditions = Q()
    
        if start_date_str and end_date_str:
            pass
            filter_conditions &= Q(invoice_date__date__range=(convertDate(start_date_str, end_date_str)))
    
        if customer:
            
            filter_conditions &= Q(cusID=customer)
        
     
        if filter_conditions: 
            invoice = customer_invoice.objects.using(db).filter(filter_conditions, invoice_state="Supplied").values()

            data = []
            for item in invoice:
                if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                    data.append(item)

            return JsonResponse(list(data), safe=False)
        else:
            invoice = customer_invoice.objects.using(db).filter(invoice_state="Supplied")

    data = []
    for item in invoice:
        if item.invoiceID not in [d.invoiceID for d in data]:
            data.append(item)
    
    context = {
        'invoice': data,
        'customers': customer_table.objects.using(db)
    }

    return render(request, 'client/SuppliedInvoice.html', context)

def SalesInvoice(request):
    db = request.user.company_id.db_name
    

    if request.method == "POST":
        invoiceID = request.POST.get('invoiceID')
        invoice_state = request.POST.get('state')
        if invoice_state == '1':
            queryset = customer_invoice.objects.using(db).filter(invoiceID=invoiceID)
            
            for item in queryset:
                ReduceOutletStockinItemQuantity(db, item.outlet, item.itemcode, item.qty)
            customer_invoice.objects.using(db).filter(invoiceID=invoiceID).update(invoice_state="On Transit")

        
        invoice = customer_invoice.objects.using(db).filter(invoice_state="Pending")
        
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        customer = request.GET.get('customer')
        
        
        filter_conditions = Q()
    
        if start_date_str and end_date_str:
            pass
            filter_conditions &= Q(invoice_date__date__range=(convertDate(start_date_str, end_date_str)))
    
        if customer:
            
            filter_conditions &= Q(cusID=customer)
        
     
        if filter_conditions: 
            invoice = customer_invoice.objects.using(db).filter(filter_conditions).values()

            data = []
            for item in invoice:
                if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                    data.append(item)

            return JsonResponse(list(data), safe=False)
        else:
            invoice = customer_invoice.objects.using(db).all()

    data = []
    for item in invoice:
        if item.invoiceID not in [d.invoiceID for d in data]:
            data.append(item)

    context = {
        'invoice': data,
        'customers': customer_table.objects.using(db)
    }

    return render(request, 'client/SalesInvoice.html', context)

