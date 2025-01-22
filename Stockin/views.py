# import sys
# sys.path.append('/Stock/functions')
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse,Http404;
from django.views.decorators.csrf import csrf_exempt;
import json
from datetime import datetime, date
from itertools import zip_longest
from decimal import Decimal


from .models import company_table
from Stock.forms import *
from Stock.models import *
from  customer.models import *
from Stock.Forms.forms import *
from settings.models import sales_outlet, Warehouse

from .utils import random_string_generator;



from account.models import *
from vendor.models import *
from vendor.forms import *
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Stockin.functions.company.company import *
from vendor.functions.vendorfunc import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main.forms import *
from settings.forms import WarehouseForm
from .functions.stockin.stockin import *
from .functions.stockout.stockout import *

from django.contrib.auth import authenticate, login, logout



def register_user(request):
    form = UserRegistrationForm()
    company_id =  request.session.get('company_id')
    if company_id == None:
       return redirect('Stockin:Stocklogin') 
    else:
        company = company_table.objects.get(pk=company_id)
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        
        if company_id == "":
            messages.error(request, "You need company ID to register")
        else:
            if form.is_valid():
                user = form.save(commit=False)
                user.company_id = company
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                messages.success(request, "Registration Successful")
                return redirect('Stockin:Stocklogin')

    context = {
        "form": form,
    }
    return render(request, 'stockin/register.html', context)






def Login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
      
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data.get('username'),
                password = form.cleaned_data.get('password')
            )
            if user:
                login(request, user)
                return redirect('Stockin:Stockin')
                del request.session['company_id']
            else:
                messages.warning(request, "Invalid Credentials !")

        else:
            pass

    context = {
        "form": form
    }
    return render(request, 'stockin/login.html', context)



def logout_user(request):
    logout(request)
    return redirect('Stockin:Stocklogin')


    
@login_required(login_url="/Stocklogin")
def Company(request):
    db = request.user.company_id.db_name
    companys = company_table.objects.filter(db_name=db)
    context = {
        'companys':companys,
    }
   
    return render(request, 'stockin/Company.html', context)


def MigrationPage(request):
    
    return render(request, "stockin/Migration.html")

def AddCompany(request):
    
    company = company_table.objects.all()
    if request.method == 'POST':
        db_name = 'afrikbook_'+generate_company_id()
    

        db = company_table.objects.filter(db_name=db_name)
        if db.exists():
            messages.success(request, "Database already exists")
        else:
            add_company(request, db_name)
            return redirect('Stockin:Migration')

    context = {
        'companys': company,
    }
    return render(request, "stockin/NewCompany.html", context)

def UpdateCompany(request, id):
    company = company_table.objects.get(id=id)
    companys = company_table.objects.all()
    
    if request.method == 'POST':    
        update_company(request, id)
        return redirect("Stockin:NewCompany")
        
    context = {
        "company": company,
        "companys": companys
    }   
    return render(request, "stockin/EditCompany.html", context)

def delete_Company(request, id):
    company = Company_table.objects.get(id=id)
    company.delete()
    messages.error(request, "Company was deleted successfully")
    return redirect("/Stockin/NewCompany")



# Stock
@login_required(login_url="/Stocklogin")
def Stock(request):
    db = request.user.company_id.db_name
    
   
    today = date.today()

    items = Item.objects.using(db).count()
    all_sales = CreateStockout.objects.using(db).count()
    # all_stock = CreateStockIn.objects.count()
    all_stock = CreateStockIn.objects.using(db).filter(quantity__gt=0).count()
    expired_p = CreateStockInLog.objects.using(db).filter(expiry_date__lte=today).count()
   
    total_qty = CreateStockout.objects.using(db).values("invoice_no").aggregate(qty_total=Sum("quantity"))['qty_total']
   
    
    
    
    if total_qty is None:
       total_qty = total_qty = "0.00" 
    

    today_qty = CreateStockout.objects.using(db).filter(date=today).aggregate(qty_total=Sum("quantity"))['qty_total']
    

    
    if today_qty is None:
       today_qty = today_qty = "0.00" 
        
    
    
    

    sales = CreateStockout.objects.filter(date=today).values("invoice_no").distinct()
    distinct_sales = []

    for sale in sales:
        new_data =  CreateStockout.objects.filter(invoice_no=sale["invoice_no"]).values()
        total_qty = CreateStockout.objects.filter(date=today).aggregate(qty_total=Sum("quantity"))['qty_total']
   
    
        
        
        
        

        if new_data.exists():
            new_data = new_data.first()
            new_data['total_qty'] = total_qty
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
        'items':items,
        'all_sales':all_sales,
        'all_stock':all_stock,
        'stockouts':distinct_sales,
        'today_sales':today_qty,
        'expired_p':expired_p,
        'total_amount':total_qty
    }
    return render(request, 'Stockhome.html', context)

@login_required(login_url="/Stocklogin")
def NewStockin(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    item = Item.objects.using(db).all()

    invoiceID = generate_unique_id()
    orderID = generate_order_id()

    if request.method == "POST":
       add_stockin(request, db)
     
    
    context = {
        'invoiceID': "Invoice_"+invoiceID,
        'orderID': orderID,
        'warehouse': warehouse,
        'items': item,
    }
    return render(request, 'stockin/NewStockin.html', context)


@login_required(login_url="/Stocklogin")
def Stockin(request):
    db = request.user.company_id.db_name
    invoice_no = CreateStockIn.objects.using(db).values("invoice_no").distinct()
    warehouse = Warehouse.objects.using(db).all()
    context = {
        "invoice":invoice_no,
        "warehouse":warehouse
        }
    return render(request, 'stockin/Stockin.html', context)



@login_required(login_url="/Stocklogin")
def NewStockout(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    item = Item.objects.using(db).all()

    invoiceID = generate_unique_id()
    orderID = generate_order_id()

    if request.method == "POST":
       add_stockout(request, db)
     
    
    context = {
        'invoiceID': "Invoice_"+invoiceID,
        'orderID': orderID,
        'supplier': supplier,
        'warehouse': warehouse,
        'items': item,
    }
    return render(request, 'stockin/NewStockout.html', context)


@login_required(login_url="/Stocklogin")
def Stockout(request):
    db = request.user.company_id.db_name
    invoice_no = CreateStockout.objects.using(db).values("invoice_no").distinct()
    return render(request, 'stockin/Stockout.html', {"invoice":invoice_no})


@login_required(login_url="/Stocklogin")
def ReleaseOrder(request):
    db = request.user.company_id.db_name
    warehouse = Warehouse.objects.using(db).all()
    item = Item.objects.using(db).all()
    order_no = CreateStockoutOrder.objects.using(db).values("invoice_no").distinct().exclude(stockout_status="Supplied")
    
    invoiceID = generate_unique_id()
    orderID = generate_order_id()

    if request.method == "POST":
       release_order(request, db)
    
    context = {
        'invoiceID': "Invoice_"+invoiceID,
        'orderID': orderID,
        'warehouse': warehouse,
        'items': item,
        'order':order_no
    }
    return render(request, 'stockin/ReleaseOrder.html', context)

@login_required(login_url="/Stocklogin")
def InstantStockour(request):
    db = request.user.company_id.db_name

    if request.method == "POST":
       release_order(request, db)
       return redirect('Stockin:NewStockout')
     


@login_required(login_url="/Stocklogin")
def Stockout(request):
    db = request.user.company_id.db_name
    invoice_no = CreateStockout.objects.using(db).values("invoice_no").distinct()
    warehouse = Warehouse.objects.using(db).all()
    context = {
        "invoice":invoice_no,
        "warehouse":warehouse
        }
    return render(request, 'stockin/Stockout.html', context)


@login_required(login_url="/Stocklogin")
def StockNewItem(request):
    db = request.user.company_id.db_name
    form = ItemForm(request.POST, request.FILES)

    item = Item.objects.using(db).all()

    item_category = Category.objects.using(db).all()
    sub_category = Sub_Category.objects.using(db).all()

    if request.method == 'POST':
        if form.is_valid():
            item_instance = form.save(commit=False) 
            item_instance.Userlogin = request.user.username
            item_instance.save(using=db) 

            item_id = item_instance.id 
            items = Item.objects.using(db).get(id=item_id) 
            notify = SetItemNotification(item=items, Userlogin=request.user.username)

            notify.save(using=db)
            messages.success(request,"Item was Created successfully")
        else:
            pass
    context = {
        'form': form,
        'item': item,
        'item_category': item_category,
        'sub_category': sub_category,
    }
   
    return render(request, 'stockin/NewItem.html', context)


@login_required(login_url="/Stocklogin")
def StockUpdate_Item(request, item_id):
    db = request.user.company_id.db_name

    item_category = Category.objects.using(db).all()

    item_code =     Item.objects.using(db).all()

    edit_item = Item.objects.using(db).get(pk=item_id)

    form = EditItemForm(request.POST, instance=edit_item)

    files = request.FILES.getlist("image")
   
    if request.method == 'POST':
       
        if form.is_valid():
            
            f = form.save(commit=False)
            f.user = request.user
            f.save(using=db)
            for i in files:
                ItemImage.objects.create(item=f, image=i)
            

           
                
            messages.success(request, "Vendor data has been updated successfully")
            return redirect('Stockin:StockNewItem') 
        else:
            pass
         
            
            form = EditItemForm(instance=edit_item)


    return render(request, 'stockin/EditItem.html', {'edit_item': edit_item, 'item_category': item_category, 'item_code': item_code})



@login_required(login_url="/Stocklogin")        
def StockDeleteItem(request, id):
    db = request.user.company_id.db_name
    delete_item = Item.objects.using(db).get(id=id)
    delete_item.delete()
    messages.success(request, "Itemn deleted successfully")
    return redirect('Stockin:StockNewItem')


@login_required(login_url="/Stocklogin")
def StockItemCategory(request):
    db = request.user.company_id.db_name
    item_category = Category.objects.using(db).all()

    if request.method == "POST":

        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form_i = form.save(commit=False)
           
            form_i.save(using=db)
            messages.success(request, "Category Added Successful")
            return redirect('Stockin:StockItemCategory')
            
        else:
            pass
           
    else:
        form = CategoryForm()
   
    return render(request, 'stockin/ItemCategory.html', {'item_category': item_category})
    

@login_required(login_url="/Stocklogin")
def StockEditItemCategory(request, id):
    db = request.user.company_id.db_name
    edit_cat = Category.objects.using(db).get(id=id)

    form = CategoryForm(request.POST, instance=edit_cat)
    
    if request.method == "POST":
        if form.is_valid():
            form_i = form.save(commit=False)
           
            form_i.save(using=db)
            messages.success(request, "Category data has been updated successfully")
            return redirect('Stockin:StockItemCategory')
    return render(request, 'stockin/EditCategory.html', {'edit_cat': edit_cat})


@login_required(login_url="/Stocklogin")
def NewUser(request):
    company_id = request.user.company_id.id
    user = User.objects.filter(company_id=company_id)

    form = NewUserForm()

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.company_id = company_id
            user.save()
            messages.success(request, "Registration Successful")
            return redirect('Stockin:StockNewUser')

    context = {
        "form": form,
        "user": user
    }
   
   
    return render(request, 'stockin/NewUser.html', context)

    
@csrf_exempt
@login_required(login_url="/Stocklogin")
def EditUser(request):
    company_id = request.user.company_id.id
    show_user = User.objects.filter(company_id=company_id)
    view_page = Pages.objects.all()
    outlet = sales_outlet.objects.all()
    
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        user_id = data.get('id')
        username = data.get('username')
        privileges = data.get('privileges', [])

        # Assuming you have a User instance
        user_instance = User.objects.get(id=user_id)

        # Save privileges in the Privilege model
        # for privilege_name in privileges:
        #     privilege = Privilege(user=user_instance, name=privilege_name, description='', is_active=True)
        #     privilege.save()

        # return JsonResponse({'success': True, 'message': 'Privileges updated successfully'})

        for privilege_name in privileges:
            if not Privilege.objects.filter(user=user_instance, name=privilege_name).exists():
                # If the privilege doesn't exist, save it
                privilege = Privilege(user=user_instance, name=privilege_name, description='', is_active=True)
                privilege.save()

        return JsonResponse({'success': True, 'message': 'Privileges updated successfully'})
    
    return render(request, 'stockin/EditUser.html', {'show_user': show_user, 'view_page': view_page, 'outlet': outlet})


@login_required(login_url="/Stocklogin")
def StockAddWarehouse(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form_i = form.save(commit=False)
           
            form_i.save(using=db)
            messages.success(request, "Warehouse added Successfully")  
        else: 
            pass
    else:
        form = WarehouseForm()
   
    return render(request, 'stockin/AddWarehouse.html')



def stockin_filter_by_date(request):
    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    

    # Convert strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    filtered_data = CreateStockIn.objects.using(db).values('invoice_no').distinct()
    
    unique_stockin = []

    for i in filtered_data:
        new_data = CreateStockIn.objects.using(db).filter(datetx__range=(start_date, end_date), invoice_no=i['invoice_no']).values()
        total_qty = CreateStockIn.objects.using(db).filter(datetx__range=(start_date, end_date), invoice_no=i['invoice_no']).aggregate(total=Sum("quantity"))['total']
       

        if new_data.exists():
            new_data = new_data.first()
            new_data['total_qty'] = total_qty
            unique_stockin.append(new_data)


    qty_total = CreateStockIn.objects.using(db).filter(datetx__range=(start_date, end_date)).aggregate(total_qty=Sum("quantity"))['total_qty']
    
    serializer_data = list(unique_stockin)
    data = {
        'serializer_data': serializer_data,
        'qty_total':qty_total,
    }

    return JsonResponse(data)

def stockin_filter(request, value):
    db = request.user.company_id.db_name
    if value:
        lookup = Q(invoice_no=value) | Q(warehouse=value)

        filtered_data = CreateStockIn.objects.using(db).filter(lookup).values("invoice_no").distinct()
        unique_stockin = []

        for i in filtered_data:
            new_data = CreateStockIn.objects.using(db).filter(lookup).values()
            total_qty = CreateStockIn.objects.using(db).filter(lookup).aggregate(total=Sum("quantity"))['total']
            # stockin = CreateStockIn.objects.filter(invoice_no=value).first()
            # item_code = stockin.item_code
            # warehouse = stockin.warehouse
            
            # total_qty1 = CreateStockIn.objects.filter(invoice_no=value, warehouse=warehouse).aggregate(total=Sum("quantity"))['total']
            # total_qty2 = CreateStockInLog.objects.filter(invoice_no=value, warehouse=warehouse).aggregate(total=Sum("quantity"))['total']
            # total = total_qty2 - total_qty1
            # total_qty = total - total_qty1
            

            if new_data.exists():
                new_data = new_data.first()
                new_data['total_qty'] = total_qty
                unique_stockin.append(new_data)

        qty_total = CreateStockIn.objects.using(db).filter(lookup).values("invoice_no").distinct().aggregate(total_qty=Sum("quantity"))['total_qty']
        
        serializer_data = list(unique_stockin)
        
        data = {
            'serializer_data': serializer_data,
            'qty_total':qty_total,
        }

    return JsonResponse(data)


def ViewStockin(request, invoice):
    db = request.user.company_id.db_name
    try:
       
       stockin = CreateStockIn.objects.using(db).filter(invoice_no=invoice).first()
       
       date = stockin.datetx
       invoice_no = stockin.invoice_no
       warehouse = stockin.warehouse
        
       invoice = CreateStockIn.objects.using(db).filter(invoice_no=invoice).values()
       serialized_data = list(invoice)

    #    total_qty = CreateStockIn.objects.filter(invoice_no=invoice).aggregate(total=Sum("quantity")) #['total']
    #    if  total_qty :
    #    total_qty = '0.00'

       data={
           'serialized_data':serialized_data,
        #    'total_qty':total_qty,
           "stockin":{
            'date': date,
            'invoice_no': invoice_no,
            'warehouse': warehouse
           }
       }
       return JsonResponse(data, safe=False)
    except CreateStockIn.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)


def stockout_filter_by_date(request):
    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

  

    # Convert strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    filtered_data = CreateStockout.objects.using(db).values('invoice_no').distinct()
    
    unique_stockin = []

    for i in filtered_data:
        new_data = CreateStockout.objects.using(db).filter(date__range=(start_date, end_date), invoice_no=i['invoice_no']).values()
        total_qty = CreateStockout.objects.using(db).filter(date__range=(start_date, end_date), invoice_no=i['invoice_no']).aggregate(total=Sum("quantity"))['total']
       

        if new_data.exists():
            new_data = new_data.first()
            new_data['total_qty'] = total_qty
            unique_stockin.append(new_data)


    qty_total = CreateStockout.objects.using(db).filter(date__range=(start_date, end_date)).aggregate(total_qty=Sum("quantity"))['total_qty']
    
    serializer_data = list(unique_stockin)
    data = {
        'serializer_data': serializer_data,
        'qty_total':qty_total,
    }

    return JsonResponse(data)

def stockout_filter(request, value):
    db = request.user.company_id.db_name
    if value:
        lookup = Q(invoice_no=value) | Q(warehouse=value)
        filtered_data = CreateStockout.objects.using(db).filter(lookup).values("invoice_no").distinct()
        unique_stockin = []

        for i in filtered_data:
            new_data = CreateStockout.objects.using(db).filter(lookup).values()
            total_qty = CreateStockout.objects.using(db).filter(lookup).aggregate(total=Sum("quantity"))['total']
            

            if new_data.exists():
                new_data = new_data.first()
                new_data['total_qty'] = total_qty
                unique_stockin.append(new_data)

        qty_total = CreateStockout.objects.using(db).filter(lookup).aggregate(total_qty=Sum("quantity"))['total_qty']
        
        serializer_data = list(unique_stockin)
        
        data = {
            'serializer_data': serializer_data,
            'qty_total':qty_total,
        }

    return JsonResponse(data)


def ViewStockout(request, invoice):
    db = request.user.company_id.db_name
    try:
       
       stockin = CreateStockout.objects.using(db).filter(invoice_no=invoice).first()
       
       date = stockin.date
       invoice_no = stockin.invoice_no
       warehouse = stockin.warehouse
        
       invoice = CreateStockout.objects.using(db).filter(invoice_no=invoice).values()
       serialized_data = list(invoice)

    #    total_qty = CreateStockout.objects.filter(invoice_no=invoice).aggregate(total=Sum("quantity"))['total']
    #    if  total_qty :
    #    total_qty = '0.00' 
       data={
           'serialized_data':serialized_data,
        #    'total_qty':total_qty,
           "stockin":{
            'date': date,
            'invoice_no': invoice_no,
            'warehouse': warehouse
           }
       }
       return JsonResponse(data, safe=False)
    except CreateStockIn.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)


def GetOrderDetails(request, order):
    db = request.user.company_id.db_name
    invoiceID = request.GET.get('invoiceId')
    try:
        # Fetch all fields related to the given invoice_id
        data = CreateStockoutOrder.objects.using(db).filter(invoice_no=order).values()
        
       

        serialized_data = {
            'order':list(data),
        }

        return JsonResponse(serialized_data,  safe=False)
    except CreateStockoutOrder.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)

