from django.shortcuts import render, redirect
from . models import *
from . forms import *
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
# from .functions.company_d import *
from .functions.pricemanagement import *
from .functions.salesoutlet import *
from .functions.profile import *
from .functions.getData import *
from .functions.sgipping_address import *

from main.models import User
from Stock.views import autosaveFunction
from Stock.models import Item, CreateStockInLog, CreateStockIn, cat_payment_method
from customer.models import customer_table
from Stockin.models import company_table
from client.models import shipping_addr
from customer.models import  billing_addr, customer_invoice
from datetime import datetime, timezone, date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import os, requests
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name
from main.functions.verification import check_sub
 
# Create your views here.
# Price management
@login_required(login_url='/')
@urls_name(name="Price Management")
def PriceChangeHistory(request):
    db = request.user.company_id.db_name
    history = pricechange_history.objects.using(db).all()

    context = {
        'history': history
    }
    return render(request, "price-history.html", context)

@login_required(login_url='/')
@urls_name(name="Price Management")
def AddPriceChangeHistory(request):
    db = request.user.company_id.db_name
    history = pricechange_history.objects.using(db).all()
    if request.method == "POST":
        add_price_management(request, db)

    context = {
        'history': history
    }
    return render(request, "settings/PriceManagement.html", context)

@login_required(login_url='/')
@urls_name(name="Price Management")
def UpdatePriceChangeHistory(request, id):
    db = request.user.company_id.db_name
    price_history = pricechange_history.objects.using(db).get(id=id)
    histories = pricechange_history.objects.using(db).all()
    if request.method == "POST":
        update_price_management(request, id, db)
        # return redirect("settings:PriceManagement")
    context = {
        "history": price_history,
        "histories":histories
        
    }
    return render(request, "settings/UPdatePriceManagement.html", context)

# User
def AddCompanyDetails(request):
    db = request.user.company_id.db_name
    company_d = company_details.objects.all()
    if request.method == "POST":
        company = company_table.objects.get(id=request.user.company_id.id)
        form = CompanyDetailsForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = company
            instance.Userlogin = request.user.username
            instance.save()

            messages.success(request, "Company "+form.cleaned_data.get('type')+" details was added successfully")
        else:
            pass
          
    else:
        form = CompanyDetailsForm()
    context = {
        'company_d': company_d,
        'form': form
    }
    return render(request, "settings/NewUser.html", context)

def UpdateCompanyDetails(request, id):
    db = request.user.company_id.db_name
    company_d = company_details.objects.get(id=id)
    if request.method == "POST":
        form = CompanyDetailsForm(request.POST, instance=company_d)
        if form.is_valid():
            form.save()
            messages.success(request, "Company "+form.cleaned_data.get('type')+" details was updated successfully")
        return redirect("settings:NewCompany_details")
    else:
        form = CompanyDetailsForm()
    context = {
        'company_d': company_d,
        'form': form
    }
    return render(request, "settings/EditCompanyDetails.html", context)

def DeleteCompanyDetails(request, id):
    db = request.user.company_id.db_name
    company_d = company_details.objects.get(id=id)
    company_d.delete()
    messages.error(request, "User was deleted successfully")
    return redirect("settings:NewCompany_details")

# Sales OUtlet
@login_required(login_url='/')
@urls_name(name="Sales Unit")
def SalesOutlet(request):
    db = request.user.company_id.db_name
    outlets = sales_outlet.objects.using(db).all()
    context = {
        'outlets': outlets
    }
    return render(request, "settings/ViewSalesUnit.html", context)



def get_all_currencies():
    currency_code_list = ['NGN', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NZD', 'KRW', 'SGD', 'NOK', 'MXN', 'INR', 'RUB', 'ZAR', 'BRL', 'TRY', 'HKD', 'THB', 'IDR', 'TWD', 'DKK', 'PLN', 'PHP', 'HUF', 'CZK', 'ILS', 'CLP', 'AED', 'COP', 'SAR', 'MYR', 'RON', 'VND', 'ARS',  'EGP', 'PKR', 'UAH', 'KES', 'BDT', 'IQD', 'MAD', 'KWD', 'HNL', 'QAR', 'NPR', 'NAD', 'CRC', 'UYU', 'PYG', 'OMR', 'BHD', 'BOB', 'DOP', 'LBP', 'JMD', 'GYD', 'AFN', 'SZL', 'TND', 'YER', 'GHS', 'MZN', 'UZS', 'KHR', 'LRD', 'XAF', 'XCD', 'HTG', 'BZD', 'MVR', 'BND', 'MWK', 'SBD', 'GNF', 'XOF', 'LAK', 'XPF', 'WST', 'DJF', 'MNT', 'MOP', 'KGS', 'FJD', 'TOP', 'GMD', 'SLL', 'TJS', 'BWP', 'SCR', 'STD', 'LSL', 'AZN', 'SVC', 'KHR', 'RWF', 'MKD', 'VUV', 'DZD', 'SRD', 'ANG', 'MMK', 'BAM', 'GIP', 'TMT', 'FKP', 'GGP', 'IMP', 'JEP', 'SHP', 'TVD', 'ZMW', 'BYN', 'XAG', 'XAU', 'XPT', 'XPD', 'BIF']
    return currency_code_list



# GET CURRENCIES(PLUS THE ONE ALREADY EXISTING)
def get_currency_by_name(get_one_only, all_currencies):
    if get_one_only is not None:
        encountered_any = []
        encountered_any.append(get_one_only.currency)
        for i in all_currencies:
            if i not in encountered_any:
                encountered_any.append(i)
        return encountered_any
    else:
        return all_currencies
    

from main.models import currency

def get_user_currency(request):
    db = request.user.company_id.db_name
    cur = get_currency(request)
    
    try:
        profile = CreateProfile.objects.using(db).get(CompanyName=request.user.company_id.company_name)
       
        cn = profile.ownerName
        img = str(profile.logo.url) 
        if img:
            pp = img
        else:
            pp = "image"
       
        return JsonResponse({'cur':cur, 'cn':cn,'pp':pp}, safe=False)
    except CreateProfile.DoesNotExist:
       pass
       return JsonResponse({'cur':cur, 'cn':cn,'pp':"image"}, safe=False)
    except Exception as e:
    
      return JsonResponse({'cur':cur, 'cn':cn,'pp':"image"}, safe=False)
    

    

@login_required(login_url='/')
@urls_name(name="Sales Unit")
def AddSalesOutlet(request):
   
    db = request.user.company_id.db_name
    country = currency.objects.all()
    form = SalesOutletForm ()
    if request.method == "POST":
        add_sales_outlet(request, db)
    
    currencies = get_all_currencies()
    return render(request, "settings/SalesUnitSetup.html", {'form' :form, 'country':country})

@login_required(login_url='/')
@urls_name(name="Sales Unit")
def UpdateSalesOutlet(request, id):
    
    db = request.user.company_id.db_name
    sales = sales_outlet.objects.using(db).get(id=id)
    if request.method == "POST":
        update_sales_outlet(request, id, db)
        return redirect("settings:SalesOutlet")
    all_currencies = get_all_currencies()
    get_currency = get_currency_by_name(sales, all_currencies)
    context = {
        "sales_outlet": sales,
        "currencies": get_currency,
        
    }
    return render(request, "settings/UpdateSalesUnitSetup.html", context)

@login_required(login_url='/')
@urls_name(name="Sales Unit")
def DeleteSalesOutlet(request, id):
    db = request.user.company_id.db_name
    sales = sales_outlet.objects.using(db).get(id=id)
    sales.delete()
    messages.error(request, "Sales Outlet was deleted successfully")
    return redirect("settings:SalesOutlet")

# Address
def Shipping_Address(request):
    db = request.user.company_id.db_name

    # db = AfrikBookDB(request)
    customer = User.objects.using("afrikbook_client").all()
    #Endpoint api 
    try:
        response = requests.get('http://127.0.0.1:8000/address', timeout=10)
        if response.status_code == 200:
            data = response.json()
            shipping_address = data['ship']
        else:
            shipping_address = []
            
    except requests.RequestException:
       shipping_address = []
    if request.method == "POST":
        addr_id = request.POST.get('addr_id')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        address = request.POST.get('address')
        csrftoken = request.POST.get('csrfmiddlewaretoken')
        form = ShippingAddressForm(request.POST)
        if not addr_id:
            messages.error(request, "Select Customer")
        else:
            if form.is_valid():
                f = form.save(commit=False)
                f.addr_id_id = addr_id
                # f.save(using="afrikbook_client")
                create_shipping_address(request, csrftoken, False, addr_id, city, state, country, address)
            else:
                pass
               
    else:
        form = ShippingAddressForm()
 
    context = {
        'customer': customer,
        'address': shipping_address,
        'form': form
    }
    return render(request, "settings/ShippingAddress.html", context)

def UpdateShippingAddress(request, id):
    db = AfrikBookDB(request)
    address = shipping_addr.objects.using("afrikbook_client").get(id=id)
    # company_id = request.user.company_id.id
    customer = User.objects.using("afrikbook_client").all()
    if request.method == "POST":
        form = ShippingAddressForm(request.POST, instance=address)
      
        addr_id = request.POST.get('addr_id')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        address = request.POST.get('address')
        csrftoken = request.POST.get('csrfmiddlewaretoken')
        if form.is_valid():
            f= form.save(commit=False)
            f.addr_id_id = addr_id
            create_shipping_address(request, csrftoken, id, addr_id, city, state, country, address)
            # f.save(using="afrikbook_client")
            # messages.success(request, "Shipping Address updated successfully")
            return redirect("settings:ShippingAddress")
    context = {
        "address": address,
        "customer": customer
        
    }
    return render(request, "settings/UpdateShippingAddress.html", context)
def AfrikBookDB(request):
    db = request.user.company_id.db_name
    return db

def DeleteShippingAddress(request, id):
    db = AfrikBookDB(request)
    address = shipping_addr.objects.using("afrikbook_client").get(id=id)
    address.delete()
    messages.error(request, "Address was deleted successfully")
    return redirect("settings:ShippingAddress")

def Billing_Address(request):
    db = AfrikBookDB(request)

    customer = customer_table.objects.using(db).all()
    address = billing_addr.objects.using(db).all()
    if request.method == "POST":
        addr_id = request.POST.get('addr_id')
        form = BillingAddressForm(request.POST)
        if not addr_id:
            messages.error(request, "Select Customer")
        else:
            if form.is_valid():
                f = form.save(commit=False)
                f.addr_id_id = addr_id
                f.save(using=db)
                messages.success(request, "Billing Address created successfully")
            else:
                pass
                
    else:
        form = BillingAddressForm()
    
   
    context = {
        'customer': customer,
        'address': address,
        'form': form
    }
    return render(request, "settings/BillingAddress.html", context)

def UpdateBillingAddress(request, id):
    db = AfrikBookDB(request)
    address = billing_addr.objects.using(db).get(id=id)
    # company_id = request.user.company_id.id
    customer = User.objects.using(db).all()
    if request.method == "POST":
        form = BillingAddressForm(request.POST, instance=address)
        addr_id = request.POST.get('addr_id')
        if form.is_valid():
            f= form.save(commit=False)
            f.addr_id_id = addr_id
            f.save(using=db)
            messages.success(request, "Billing Address updated successfully")
            return redirect("settings:BillingAddress")
    context = {
        "address": address,
        "customer": customer
        
    }
    return render(request, "settings/UpdateBillingAddress.html", context)

def DeleteBillingAddress(request, id):
    db = AfrikBookDB(request)
    address = billing_addr.objects.using(db).get(id=id)
    address.delete()
    messages.error(request, "Address was deleted successfully")
    return redirect("settings:BillingAddress")



from django.shortcuts import render
from .Forms.profile import ProfileSetupForm
import logging
from Stock.utils import random_string_generator
# Create your views here.

logger = logging.getLogger(__name__)



@login_required(login_url='Profile Setup')
@urls_name(name="Profile Setup")
def Create_UpdateNewProfile(request):
    db = request.user.company_id.db_name
    profileID = request.POST.get('id')
    
    forms = ProfileSetupForm(request.POST, request.FILES or None)
    profiledata = CreateProfile.objects.using(db).all()
    randomtoken = random_string_generator()
    country = currency.objects.all() 
    context = {
        'form': forms,
        'submit': False,
        'token': 'Token_'+randomtoken,
        'profile':profiledata.first(),
        'country': country
    }
    if request.method == 'POST':
        
        

        if forms.is_valid():
            getdata = forms.cleaned_data
            name=getdata.get('ownerName')
            business_type=request.POST.get('salesinterface')
            token=getdata.get('Token_ID')
            logo=getdata.get('logo')
            Userlogin=getdata.get('Userlogin')
            
            if profiledata.count() > 0:
                profileIMG = CreateProfile.objects.using(db).get(id=profileID)
                formsUpdate = ProfileSetupForm(request.POST, request.FILES or None, instance=profileIMG)
                # profileIMG = CreateProfile.objects.using(db).all().first()
                
                if logo is not None:
                    try:
                        path = profileIMG.logo.url
                        file_system_path = os.path.join(settings.MEDIA_ROOT, path[len(settings.MEDIA_URL):])
                        if os.path.exists(file_system_path):
                            os.remove(file_system_path)
                            # profileIMG.logo = logo

                    except:
                        pass

                # updateProfile           = CreateProfile.objects.using(db).update(**getdata)
                updateProfile           = formsUpdate.save(commit=False)
                updateProfile.save(using=db)
                updatesaleinterface     = SalesInterface.objects.using(db).update(name=name, business_type=business_type, token=token, Userlogin=Userlogin)
                if updateProfile or updatesaleinterface:
                    context["success_message"] =  'Profile Successfully Updated' 
            else:
                profile_instance = forms.save(commit=False)
                profile_instance.save(using=db)
                SalesInterface.objects.using(db).create(name=name, business_type=business_type, token=token, Userlogin=Userlogin)
                if profile_instance:
                    context["success_message"] =  'Profile Successfully Created' 
                    return redirect('settings:ProfileSetup')
                else:
                    logger.error("Failed to create profile")
        else:
            logger.warning("Form is not valid")
            logger.warning(forms.errors.as_data())

    if profiledata.count() > 0:
        context['submit'] = 'Update Profile'
    else:
        context['submit']  = 'Create Profile'
    
    return render(request, 'settings/ProfileSetup.html', context)

def complete_profileSetup(request):
    db = request.user.company_id.db_name
    profileID = request.POST.get('id')
    profile = CreateProfile.objects.using(db).get(id=profileID)
    form = ProfileSetupForm(request.POST, request.FILES or None, instance=profile)

    if form.is_valid():
        form_save = form.save(commit=False)
        form_save.save(using=db)
    else:
        pass


    return redirect("/")

@login_required(login_url='Profile Setup')
@urls_name(name="Profile")
def ViewProfile(request):
    db = request.user.company_id.db_name
    profiledata = CreateProfile.objects.using(db).all()
    context = {
        'profiledata': profiledata.first()
    }
   
    return render(request, 'settings/ViewProfile.html', context)


@login_required(login_url='/')
@urls_name(name="Add Warehouse")
def AddWarehouse(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form_i = form.save(commit=False)
            form_i.save(using=db)
            messages.success(request, "Warehouse was Added Successful")
            return redirect('settings:AddWarehouse')
            
    else:
        form = WarehouseForm()
   
    return render(request, 'settings/AddWarehouse.html')


    
def instantStockout(request):
   context={}
   ifgood = autosaveFunction(request, 'IN_STOCKOUT', context)
   if ifgood:
      return ifgood
   return render(request, "components/modal/modal.html", context)


def autosaveSalesInterface(request, sessionName, context):
   aprove = request.POST.get('interface',)
   redirectTo = request.POST.get('redirectTo')
   interface = request.session[sessionName] = interface
   #  request.session.get(aprove, 'yes')
   if interface:
      context["success_message"] =  'Saved'
      return redirect(redirectTo)


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
        

    return render(request, "settings/ViewNotification.html", {'items':items})



def NotificationStatus(request):
    db = request.user.company_id.db_name
    invoice = CreateStockInLog.objects.using(db).values('invoice_no').distinct()
    items = CreateStockInLog.objects.using(db).all()
    
    logs = []
    for i in invoice:
        new_data = CreateStockInLog.objects.using(db).filter(invoice_no=i['invoice_no']).values()
    
        if new_data.exists():
            logs.append(new_data.first())

    return render(request, "settings/NotificationStatus.html", {'items':items, 'logs':logs})

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

    rendered_html = render_to_string('settings/NotifyFilter.html', {'items': items, 'logs': logs})


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

    invoice = CreateStockInLog.objects.using(db).filter(invoice_no=value).values('invoice_no').distinct()
    items = CreateStockInLog.objects.using(db).filter(invoice_no=value).values()
    
    logs = []
    for i in invoice:
        new_data = CreateStockInLog.objects.using(db).filter(invoice_no=value).values()
    
        if new_data.exists():
            logs.append(new_data.first())

    rendered_html = render_to_string('settings/NotifyFilter.html', {'items': items, 'logs': logs})


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
    

    return render(request, "settings/ItemExpiryDate.html", {'logs':logs})


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
    

    return render(request, "settings/UpdateItemExpiryDate.html", {'logs':logs})

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
    sold = customer_invoice.objects.using(db).filter(invoice_state="Supplied").values('invoiceID').distinct().count()
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
    return render(request, "InspirationControl.html", context)


def InspirationControlFilter(request, value):
    db = request.user.company_id.db_name
  
    items = ExpiryDate.objects.using(db).values()
    today = date.today()
    
    for i in items:
        i['rdays'] = (i['expiry_date'] - today).days
        
        try:
            item1 = SetItemNotification.objects.using(db).get(item__generated_code=['item_code'])
            i['notify_me'] = item1.notification_days        
            
        except SetItemNotification.DoesNotExist:
             i['notify_me'] = "not set"

        try:
            log = CreateStockInLog.objects.using(db).get(invoice_no=i['invoice_no'], item_code=i['item_code'])
            i['n_status'] = log.notification_status
            i['status'] = log.status
        
            
        except CreateStockInLog.DoesNotExist:
            i['n_status'] = "0"
            i['status'] = "Unverified"
            


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

    sold_items = CreateStockInLog.objects.using(db).filter(status="Sold").values_list('item_code', flat=True)

    expired_items = ExpiryDate.objects.using(db).filter(expiry_date__lte=today).exclude(item_code__in=sold_items).count()
    expire = ExpiryDate.objects.using(db).filter(expiry_date__gt=today).exclude(item_code__in=sold_items).count()
    
    for i in items:
        i['rdays'] = (i['expiry_date'] - today).days
        try:
            item1 = SetItemNotification.objects.using(db).get( item__generated_code=i['item_code'])
            i['notify_me'] = item1.notification_days
            
        except SetItemNotification.DoesNotExist:
             i['notify_me'] = "not set"


        try:
            log = CreateStockInLog.objects.using(db).get(invoice_no=i['invoice_no'], item_code=i['item_code'])
            i['n_status'] = log.notification_status
            i['status'] = log.status
           

        except CreateStockInLog.DoesNotExist:
            i['n_status'] = "0"
            i['status'] = "Unverified"
    
    sub_remaining_days, plan = check_sub(request, request.user.company_id.id)
  
    serialize_data = list(items)   
    data ={
        'items' : serialize_data,
        'expired' : expired_items,
        'expire' : expire,
        'remain': sub_remaining_days,
        # 'plan': plan
    }

    return JsonResponse(data, safe=False)




def ViewExpiredItems(request):
    db = request.user.company_id.db_name

    items = ExpiryDate.objects.using(db).all()
    
    getData(items, db)
         
    context ={
        'items' : items,
    }
    return render(request, "settings/ExpiredItems.html", context)


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
    return render(request, "settings/ViewAboutToExpireItem.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def ShippingMethod(request):
    db = request.user.company_id.db_name

    methods = shipping_method.objects.using(db).all()
    if request.method == "POST":
        id = request.POST['id']
        method = request.POST['method']
        delete = request.POST['delete']
        
        if id:
            query = shipping_method.objects.using(db).get(id=id)
            if delete:
                query.delete()
                messages.success(request, 'Method deleted successfully')
            else:
                query.method = method
                query.save()
                messages.success(request, 'Method Updated successfully')
        else:
            if shipping_method.objects.using(db).filter(method=method).exists():
                messages.error(request, 'Method already exists')
            else:
                shipping_method.objects.using(db).create(method=method)
                messages.success(request, 'Method created successfully')

         
    context ={
        'methods' : methods,
    }
    return render(request, "shipping/ShippingMethod.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def PickupStation(request):
    db = request.user.company_id.db_name

    stations = pickupstation.objects.using(db).all()

    if request.method == "POST":
        id = request.POST['id']
        addr = request.POST['station']
        delete = request.POST['delete']
        
        if id:
            query = pickupstation.objects.using(db).get(id=id)
            if delete:
                query.delete()
                messages.success(request, 'Pickup Station deleted successfully')
            else:
                query.addr = addr
                query.save()
                messages.success(request, 'Pickup Station Updated successfully')
        else:
            if pickupstation.objects.using(db).filter(addr=addr).exists():
                messages.error(request, 'Pickup Station already exists')
            else:
                pickupstation.objects.using(db).create(addr=addr)
                messages.success(request, 'Pickup Station created successfully')

         
    context ={
        'stations' : stations,
    }
    return render(request, "shipping/PickupStation.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def AddCity(request):
    db = request.user.company_id.db_name

    cities = city.objects.using(db).all()
    country = currency.objects.all() 

    if request.method == "POST":
        id = request.POST['id']
        City = request.POST['city']
        country = request.POST['country']
        delete = request.POST['delete']
        
        if id:
            query = city.objects.using(db).get(id=id)
            if delete:
                query.delete()
                messages.success(request, 'City deleted successfully')
            else:
                query.city = City
                query.country = country
                query.save()
                messages.success(request, 'City Updated successfully')
        else:
            if city.objects.using(db).filter(city=City).exists():
                messages.error(request, 'City already exists')
            else:
                city.objects.using(db).create(country=country, city=City)
                messages.success(request, 'City created successfully')

         
    context ={
        'cities' : cities,
        'country': country
    }
    return render(request, "shipping/Cities.html", context)


@login_required(login_url='/')
@urls_name(name="Customer")
def PickupShippingPrice(request):
    db = request.user.company_id.db_name

    shipping = pickUpShippingPrice.objects.using(db).all()
    items = Item.objects.using(db).all()
    locations = pickupstation.objects.using(db).all()

    if request.method == "POST":
        item = request.POST.get('item')
        same_price = request.POST['same_price']
        location = request.POST.getlist('location[]')
        price = request.POST.getlist('price[]')
     
        if item:
            item = Item.objects.using(db).get(generated_code=item)
            for i in range(len(location)):
                if price[i] == '':
                    price[i] = 0

                location_obj =  pickupstation.objects.using(db).get(addr=location[i])

                cost = pickUpShippingPrice.objects.using(db).filter(location=location_obj, item_name=item.item_name, generated_code=item.generated_code)
                
                if cost.exists():
                    cost.update(cost=price[i])
                else:
                    pickUpShippingPrice.objects.using(db).create(location=location_obj, item_name=item.item_name, generated_code=item.generated_code, cost=price[i])
            
            messages.success(request, 'Pickup Price created successfully')
            
        else:
            messages.error(request, 'Please select item')
   

         
    context ={
        'shipping': shipping,
        'items' : items,
        'locations': locations
    }
    return render(request, "shipping/PickupShippingPrice.html", context)


@login_required(login_url='/')
@urls_name(name="Customer")
def AddressShippingPrice(request):
    db = request.user.company_id.db_name

    shipping = addressShippingPrice.objects.using(db).all()
    items = Item.objects.using(db).all()
    country = currency.objects.all() 

    if request.method == "POST":

        item = request.POST.get('item')
        country = request.POST['country']
        city = request.POST.getlist('city[]')
        price = request.POST.getlist('price[]')
     
        if item:
            item = Item.objects.using(db).get(generated_code=item)
            for i in range(len(city)):
                if price[i] == '':
                    price[i] = 0

                cost = addressShippingPrice.objects.using(db).filter(country=country, city=city[i], item_name=item.item_name, generated_code=item.generated_code)
                
                if cost.exists():
                    cost.update(country=country, cost=price[i])
                else:
                    addressShippingPrice.objects.using(db).create(country=country, city=city[i], item_name=item.item_name, generated_code=item.generated_code, cost=price[i])
            
            messages.success(request, 'Address Price created successfully')
            
        else:
            messages.error(request, 'Please select item')
   

         
    context ={
        'shipping': shipping,
        'items' : items,
        'country': country
    }
    return render(request, "shipping/AddressShippingPrice.html", context)

# def AddressShippingPrice(request):
#     db = request.user.company_id.db_name

#     shipping = addressShippingPrice.objects.using(db).all()
#     items = Item.objects.using(db).all()

#     if request.method == "POST":

#         id = request.POST['id']
#         item = request.POST.get('item')
#         city = request.POST.get('city')
#         price = request.POST.get('price')
#         delete = request.POST['delete']
#         if item:
#             item = Item.objects.using(db).get(generated_code=item)
#             if id:
#                 query = addressShippingPrice.objects.using(db).get(id=id)
#                 if delete:
#                     query.delete()
#                     messages.success(request, 'Shipping price deleted successfully')
#                 else:
#                     query.city = city
#                     query.item_name = item.item_name
#                     query.generated_code = item.generated_code
#                     query.cost = price
#                     query.save()
#                     messages.success(request, 'Shipping price Updated successfully')
#             else:
#                 if addressShippingPrice.objects.using(db).filter(city = city, item_name = item.item_name, generated_code = item.generated_code).exists():
#                     messages.error(request, 'Shipping price already exists')
#                 else:
#                     addressShippingPrice.objects.using(db).create(city = city, item_name = item.item_name, generated_code = item.generated_code, cost=price)
#                     messages.success(request, 'Shipping price created successfully')

#         else:
#                 messages.error(request, 'Please select item')

         
#     context ={
#         'shipping': shipping,
#         'items' : items,
#     }
#     return render(request, "shipping/AddressShippingPrice.html", context)

def fetch_locations(request):
    db = request.user.company_id.db_name
    item = request.GET.get('item')
    try:  
        item = Item.objects.using(db).get(generated_code=item)
        locations = pickupstation.objects.using(db).values()

        for i in locations:
            i['item_name'] = item.item_name
            try:
               price = pickUpShippingPrice.objects.using(db).get(location=i['id'], item_name=item.item_name, generated_code=item.generated_code)
               i['cost'] = price.cost
            except pickUpShippingPrice.DoesNotExist:
                i['cost'] = "0"

        serialized_data = list(locations)
        return JsonResponse(serialized_data, safe=False)
        status = 200
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'No location not found'}, status = 404)
    
def fetch_cities(request):
    db = request.user.company_id.db_name
    item = request.GET.get('item')
    country = request.GET.get('country')
    try:  
        item = Item.objects.using(db).get(generated_code=item)
        cities = city.objects.using(db).filter(country=country).values()

        for i in cities:
            i['item_name'] = item.item_name
            try:
               price = addressShippingPrice.objects.using(db).get(country=country, city=i['city'], item_name=item.item_name, generated_code=item.generated_code)
               i['cost'] = price.cost
            except addressShippingPrice.DoesNotExist:
                i['cost'] = "0"

        serialized_data = list(cities)
        return JsonResponse(serialized_data, safe=False)
        status = 200
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status = 404)

def update_address_shipping_price(request):
    db = request.user.company_id.db_name
    item_id = request.GET.get('item_id')
    item_price = request.GET.get('item_price')
   
    try:
        price = addressShippingPrice.objects.using(db).get(id=item_id)
        price.cost = item_price
        price.save()
        return JsonResponse({'message': 'Changes saved successfully'})
    except addressShippingPrice.DoesNotExist:
        
        return JsonResponse({'message': 'Failed to update price. Please try again'}, status = 404)

@login_required(login_url='/')
@urls_name(name="Customer")
def CartPaymentMethod(request):
    db = request.user.company_id.db_name

    methods = cat_payment_method.objects.using(db).all()

    if request.method == "POST":
        id = request.POST['id']
        addr = request.POST.get('station')
        delete = request.POST['delete']
        
        if id:
            query = cat_payment_method.objects.using(db).get(id=id)
            if delete:
                query.delete()
                messages.success(request, 'Payment method deleted successfully')
            else:
                query.addr = addr
                query.save()
                messages.success(request, 'Payment method Updated successfully')
        else:
            if cat_payment_method.objects.using(db).filter(addr=addr).exists():
                messages.error(request, 'Payment method already exists')
            else:
                cat_payment_method.objects.using(db).create(addr=addr)
                messages.success(request, 'Payment method created successfully')

         
    context ={
        'methods' : methods,
    }
    return render(request, "shipping/CartPaymentMethod.html", context)

def ChangeCartMethosState(request):
    db = request.user.company_id.db_name
    method_id = request.GET.get('method_id')
    state = request.GET.get('state')
    try:
        price = cat_payment_method.objects.using(db).get(id=method_id)
        price.state = state
        price.save()
        return JsonResponse({'message': 'Changes saved successfully'})
    except cat_payment_method.DoesNotExist:
        
        return JsonResponse({'message': 'Failed to update price. Please try again'}, status = 404)

