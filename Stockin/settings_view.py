from django.shortcuts import render, redirect
from settings. models import *
from settings. forms import *
from django.contrib import messages
from django.http import HttpResponse, JsonResponse

from main.models import User
from Stock.models import Item, CreateStockInLog, CreateStockIn
from datetime import datetime, timezone, date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Expiration Control
def SetItemNotify(request):
    db = request.user.company_id.db_name
    items = SetItemNotification.objects.using(db).all()

    if request.method == "POST":
        days = request.POST.get('days')
        item = request.POST.get('item')
        
        try:
            item = SetItemNotification.objects.using(db).filter(id=item).update(notification_days=days)
            messages.success(request, "Changes saved")
        except SetItemNotification.DoesNotExist: 
            messages.error(request, "Changes not  saved")
        

    return render(request, "stockin/settings/ViewNotification.html", {'items':items})



def NotificationStatus(request):
    db = request.user.company_id.db_name
    invoice = CreateStockInLog.objects.using(db).values('invoice_no').distinct()
    items = CreateStockInLog.objects.using(db).all()
    
    logs = []
    for i in invoice:
        new_data = CreateStockInLog.objects.using(db).filter(invoice_no=i['invoice_no']).values()
    
        if new_data.exists():
            logs.append(new_data.first())

    return render(request, "stockin/settings/NotificationStatus.html", {'items':items, 'logs':logs})

from django.template.loader import render_to_string

def notification_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Convert strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Perform filtering based on the date range
    invoice = CreateStockInLog.objects.using(db).filter(datetx__range=(start_date, end_date)).values('invoice_no').distinct()
    items = CreateStockInLog.objects.using(db).filter(datetx__range=(start_date, end_date))
    
    logs = []
    for i in invoice:
        new_data = CreateStockInLog.objects.using(db).filter(datetx__range=(start_date, end_date), invoice_no=i['invoice_no']).values()
    
        if new_data.exists():
            logs.append(new_data.first())

    rendered_html = render_to_string('stockin/settings/NotifyFilter.html', {'items': items, 'logs': logs})


    data1 = list(logs)
    data2 = list(items)

    data = {
        'logs':data1,
        'items': data1,
        'html': rendered_html
    }

    return JsonResponse(data, safe=False)

def notification_filter(request, value):
    db = request.user.company_id.db_name

   
    invoice = CreateStockInLog.objects.using(db).filter(invoice_no__iexact=value).values('invoice_no').distinct()
    items = CreateStockInLog.objects.using(db).filter(invoice_no__iexact=value).values()
    
    logs = []
    for i in invoice:
        new_data = CreateStockInLog.objects.using(db).filter(invoice_no=value).values()
    
        if new_data.exists():
            logs.append(new_data.first())

    rendered_html = render_to_string('stockin/settings/NotifyFilter.html', {'items': items, 'logs': logs})


    data1 = list(logs)
    data2 = list(items)

    data = {
        'logs':data1,
        'items': data2,
        'html': rendered_html
    }

    return JsonResponse(data, safe=False)

def ChangeStatus(request):
    db = request.user.company_id.db_name
    invoice_no = request.GET.get('invoice_no')
    item_code = request.GET.get('item_code')
    status = request.GET.get('status')
  
    try:
       status = CreateStockInLog.objects.using(db).filter(invoice_no=invoice_no, item_code=item_code).update(notification_status=status)
       
       return JsonResponse(status, safe=False)
    except CreateStockInLog.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)


def ItemExpiryDate(request):
    db = request.user.company_id.db_name

    message_display = False
    invoice_nos = ExpiryDate.objects.using(db).values_list('invoice_no', flat=True).distinct()
    itemcode = ExpiryDate.objects.using(db).values_list('item_code', flat=True).distinct()

    logs = CreateStockInLog.objects.using(db).values('invoice_no').distinct().exclude(invoice_no__in=invoice_nos, item_code__in=itemcode)
   
    if request.method == "POST":
        invoice_no       = request.POST.get('invoice_no')
        item             = request.POST.getlist('item[]')
        item_code        = request.POST.getlist('item_code[]')
        manufacture_date = request.POST.getlist('m_date[]')
        expiry_date      = request.POST.getlist('e_date[]')

        if invoice_no != "":
            if str(item_code) != "":
                for i in range(len(item_code)):
                    if str(manufacture_date[i]) != "" and str(expiry_date[i]) != "":
                        m_date = datetime.strptime(manufacture_date[i], '%Y-%m-%d').date()
                        e_date = datetime.strptime(expiry_date[i], '%Y-%m-%d').date()
                        dates = e_date - m_date
                        number_of_days = dates.days
                        
                        ExpiryDate.objects.using(db).create(invoice_no=invoice_no,
                                                item=item[i],
                                                item_code=item_code[i],
                                                manufacture_date=manufacture_date[i],
                                                expiry_date=expiry_date[i],
                                                days=number_of_days,
                                                Userlogin=request.user.username)
                        if not message_display:
                            messages.success(request, invoice_no+" expiry date set successfully")
                            message_display = True
                    else:
                        messages.error(request, item[i]+" expiry date was not set")

        else:
            messages.error(request, "Please select an invoice")
    

    return render(request, "stockin/settings/ItemExpiryDate.html", {'logs':logs})


def ItemExpiryDate_filter(request, value):
    db = request.user.company_id.db_name

   
    itemcode = ExpiryDate.objects.using(db).values_list('item_code', flat=True).distinct()

    items = CreateStockInLog.objects.using(db).filter(invoice_no__iexact=value).exclude(item_code__in=itemcode).values()
    
    
    data2 = list(items)

    data = {
        'items': data2,
    }

    return JsonResponse(data, safe=False)


def UpdateItemExpiryDate(request):
    db = request.user.company_id.db_name
    message_display = False 

    logs = ExpiryDate.objects.using(db).values('invoice_no').distinct()

    if request.method == "POST":
        invoice_no       = request.POST.get('invoice_no')
        item             = request.POST.getlist('item[]')
        item_code        = request.POST.getlist('item_code[]')
        manufacture_date = request.POST.getlist('m_date[]')
        expiry_date      = request.POST.getlist('e_date[]')

        if invoice_no != "":
            if str(item_code) != "":
                for i in range(len(item_code)):
                    if str(manufacture_date[i]) != "" and str(expiry_date[i]) != "":
                        m_date = datetime.strptime(manufacture_date[i], '%Y-%m-%d').date()
                        e_date = datetime.strptime(expiry_date[i], '%Y-%m-%d').date()
                        dates = e_date - m_date
                        number_of_days = dates.days
                        
                        ExpiryDate.objects.using(db).filter(invoice_no=invoice_no, item_code=item_code[i]).update(
                                                manufacture_date=manufacture_date[i],
                                                expiry_date=expiry_date[i],
                                                days=number_of_days)

                        if not message_display:
                            messages.success(request, invoice_no+" expiry date set successfully")
                            message_display = True
        else:
            messages.error(request, "Please select an invoice")
    

    return render(request, "stockin/settings/UpdateItemExpiryDate.html", {'logs':logs})

def UpdateItemExpiryDate_filter(request, value):
    db = request.user.company_id.db_name

    items = ExpiryDate.objects.using(db).filter(invoice_no__iexact=value).values()
    
    
    data2 = list(items)

    data = {
        'items': data2,
    }

    return JsonResponse(data, safe=False)

def InspirationControl(request):
    db = request.user.company_id.db_name

    products = Item.objects.using(db).count()
    stock = CreateStockIn.objects.using(db).filter(quantity__gt=0).count()
    sold = CreateStockInLog.objects.using(db).filter(status="sold").count()
    expired = CreateStockInLog.objects.using(db).filter(status="expired").count()
    items = ExpiryDate.objects.using(db).all()
   
    getData(items, db)
  

    # for pagination
    page = request.GET.get('page', 1)

    paginator = Paginator(items, 10)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

         
    context ={
        'products': products,
        'stock': stock,
        'sold': sold,
        'expired': expired,
        'items' : items,
    }
    return render(request, "stockin/settings/InspirationControl.html", context)

def InspirationControlFilter(request, value):
    db = request.user.company_id.db_name
  
    items = ExpiryDate.objects.using(db).values()
    today = date.today()
    
    for i in items:
        i['rdays'] = (i['expiry_date'] - today).days
        
        try:
            item1 = SetItemNotification.objects.using(db).get(item__generated_code=['item_code'])
            i['notify_me'] = item1.notification_days

            log = CreateStockInLog.objects.using(db).filter(item_code=i['item_code'])
            i['n_status'] = log.notification_status
            i['status'] = log.notification_status
        
            
        except SetItemNotification.DoesNotExist:
             i['notify_me'] = "not set"
        try:
            log = CreateStockInLog.objects.using(db).filter(item_code=i['item_code']).first()
            i['n_status'] = log.notification_status
            i['status'] = log.status
        
            
        except CreateStockInLog.DoesNotExist:
            i['n_status'] = "1"
            i['status'] = "2"



    serialize_data = list(items)   
    data ={
        'status': value,
        'items' : serialize_data,
    }

    
    return JsonResponse(data, safe=False)


def ExpiryDateReminder(request):
    db = request.user.company_id.db_name
  
    items = ExpiryDate.objects.using(db).values()
    today = date.today()
    expired_items = ExpiryDate.objects.using(db).filter(expiry_date__lte=today).count()
    expire = ExpiryDate.objects.using(db).filter(expiry_date__gte=today).count()
    
    for i in items:
        try:
            item1 = SetItemNotification.objects.using(db).get(item__generated_code=['item_code'])
            i['notify_me'] = item1.notification_days

            log = CreateStockInLog.objects.using(db).filter(item_code=i['item_code'])
            i['n_status'] = log.notification_status
            i['status'] = log.notification_status
        
            
        except SetItemNotification.DoesNotExist:
             i['notify_me'] = "not set"
        i['rdays'] = (i['expiry_date'] - today).days
        log = CreateStockInLog.objects.using(db).filter(item_code=i['item_code']).first()
        i['n_status'] = log.notification_status

    
    
    
    serialize_data = list(items)   
    data ={
        'items' : serialize_data,
        'expired' : expired_items,
        'expire' : expire
    }

    return JsonResponse(data, safe=False)




def ViewExpiredItems(request):
    db = request.user.company_id.db_name

    items = ExpiryDate.objects.using(db).all()
   
    getData(items, db) 
      
    context ={
        'items' : items,
    }
    return render(request, "stockin/settings/ExpiredItems.html", context)

def DeleteExpiredItem(request, invoice_no, item_code):
    db = request.user.company_id.db_name
    item = ExpiryDate.objects.using(db).get(invoice_no=invoice_no, item_code=item_code)
    log = CreateStockInLog.objects.using(db).get(invoice_no=invoice_no, item_code=item_code)
 
    messages.success(request, "Delete successfully")
    return redirect("settings:ViewExpiredItems")

def DeleteExpiredItems(request):
    db = request.user.company_id.db_name
    today = date.today()
    items = ExpiryDate.objects.using(db).filter(expiry_date__lte=today).count()
    log = CreateStockInLog.objects.using(db).filter(status="Expired").count()
 
    messages.success(request, "Delete successfully")
    return redirect("settings:ViewExpiredItems")

def ViewAboutToExpireItems(request):
    db = request.user.company_id.db_name

    items = ExpiryDate.objects.using(db).all()

    getData(items, db)

    context ={
        'items' : items,
    }
    return render(request, "stockin/settings/ViewAboutToExpireItem.html", context)



def getData(items, db):
    today = date.today()
    
    for i in items:
        i.rdays = (i.expiry_date - today).days
       
        try:
            item1 = SetItemNotification.objects.using(db).get(item__generated_code=i.item_code)
            i.notify_me = item1.notification_days

            
            
        except SetItemNotification.DoesNotExist:
             i.notify_me = "not set"
        try:
            log = CreateStockInLog.objects.using(db).get(invoice_no=i.invoice_no, item_code=i.item_code)

            if i.rdays > 1 and log.status != "Unverified":
                log.status = "Unverified"
                log.save()
            
            if i.rdays < 1 and log.status != "Expired":
                log.status = "Expired"
                log.save()

            i.n_status = log.notification_status
            i.status = log.status
        
            
        except CreateStockInLog.DoesNotExist:
            i.n_status = "1"
            i.status = "2"
