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


from .models import *
from  customer.models import *;
from .Forms.forms import *
from settings.models import sales_outlet, Warehouse, SetItemNotification
from Stock.forms import NotificationForm
# from .Forms.new_categoryForm import*;
# from .Forms.new_itemForm import*;
from .Forms.stockTransferForm import*;
from .Forms.StockoutForm import*;
from django.db.models import Count, F
from .functions.functionHub.Stokinfunctions import *
from .functions.verifyFunctions.verify import *
from .utils import random_string_generator;
from .functions.globalFunctions.globalFunctions import *
from .functions.functionHub.functionHub import *
from .functions.stockin import *
from .functions.stockout import *
from .setCurrentUsers import *
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name


# Create your views here.
@login_required(login_url='/')
@urls_name(name="Item Issue")   
def ItemIssue(request):
   db = request.user.company_id.db_name
   word = '12345'
   getinvoice = customer_invoice.objects.using(db).filter(status=0);

   # get invioceID appear once**********************************
   encountered_invoice = Encountered(getinvoice, 'invoiceID')
   # get invioceID appear once end**********************************
   
   getOrderID = random_string_generator()
   context = {
         'myarray': word[0],
         'invoice': encountered_invoice,
         'getOrderID': "Order_"+getOrderID,
      }
   verifyStockout(request, context, db)

   # a get method***********************************
   getinvoiceID = request.GET.get('getinvoiceID')
   if getinvoiceID:
      done =  getStockOutInvoiceData(getinvoiceID, context, db)
      if done:
         context['loader'] = 'No'
         return done
   # a get method END ***********************************
      
   return render(request, 'ItemIssue.html', context)



@login_required(login_url='/')
@urls_name(name="Verify Transfer")
def VerifyTransfer(request):
   db = request.user.company_id.db_name
   # DEFAULT DISPLAY
   getUnverified = CreateStockInLog.objects.using(db).filter(status='Unverified', transfer='W_W')
   buttonName = request.POST.get('buttonName') 
   deleteID = request.POST.get('deleteID') 
   context = {
      'Unverified' : getUnverified,
      'whichtrans' : 'W_W',
   }
   # GET OTHER UNVERIFIED DATA "ONCHANGE"
   unverifiedD = getStockInLog(request, db)
   if unverifiedD:
      return JsonResponse({'data': unverifiedD})

   # POST TO VERIFY
   if request.method == 'POST':
      verifyFunction = VerifyStockTransfer(request,context)

      if buttonName != None:
         if verifyFunction:
            return JsonResponse({'data': verifyFunction, 'message': 'Transfer Verified'})
      elif deleteID != None:
         if verifyFunction:
            return JsonResponse(verifyFunction)
      else:
         # FOR DEFAULT POST, INCASE JS HAD NO ONCHANGE
         verifyFunction

   return render(request, 'VerifyTransfer.html', context)





def deleteDate(deletedata):
   deletedata.delete()
   response_data = {'message': 'Transfer successfully deleted'}
   return JsonResponse(response_data)

@login_required(login_url='/')
@urls_name(name="Item")
def DeleteItem(request):
   db = request.user.company_id.db_name
   # PENDING ......
   deleterow = request.POST.get('deleterow')
   if deleterow:
      try:
         deletedata = CreateStockInLog.objects.using(db).get(id=deleterow)
         deletedata.delete()
      
         response_data = {'message': 'Transfer successfully deleted'}
         return JsonResponse(response_data)

      except CreateStockInLog.DoesNotExist:
         response_data = {'error': 'Item not found'}
         return JsonResponse(response_data, status=404)
   # PENDING END ......
      
   deleteID = request.POST.get('deleteID')
   if deleteID:
      try:
         deletedata = CreateStockInLog.objects.using(db).get(id=deleteID)
         return deleteDate(deletedata)
      except CreateStockInLog.DoesNotExist:
         deletedata = CreateOutletStockInLog.objects.using(db).get(id=deleteID)
         if deletedata:
            return deleteDate(deletedata)


@login_required(login_url='/')
@urls_name(name="Transfer Stock")
def TransferHistory(request):
   db = request.user.company_id.db_name
   # DEFAULT PRINT
   getransfer2 = CreateStockInLog.objects.using(db).all()
   warehouse = Warehouse.objects.using(db).all()
   encountered_items = Encountered(getransfer2,'item')
   shop = sales_outlet.objects.using(db).all()
   context = {
      'warehouse':warehouse,
      'items':encountered_items,
      'shop':shop,
   }
   # DEFAULT PRINT

   # GET CALL WHEN ONCHANGE(JS)
   data = getTransferHistory(request, db)
   if data:
      return JsonResponse({'data': data})
   return render(request, 'TransferHistory.html', context)



@login_required(login_url='/')
@urls_name(name="Warehouse to Warehouse")
def WarehouseToWarehouse(request):
   db = request.user.company_id.db_name
   form = W_W_Form(request.POST or None)
   listitems = Item.objects.using(db).all()
   warehouse = Warehouse.objects.using(db).all()
   randomtoken = random_string_generator()   
   context = {
      'listitems' : listitems,
      'warehouse' : warehouse,
      'form' : form,
      'tokenID': 'Token_'+randomtoken,
      'refID': 'Ref_'+randomtoken
   }

   id = request.GET.get('id')
   fromw = request.GET.get('from')
   if id and fromw:
    
      # return ifemptyfunction(request, id, fromw)
      return ifemptyfunction(request, id, fromw, 'buttonoutlet', db)
   
   getid = request.GET.get('data')
   if getid is not None:
      # context['loader'] = 'Yes'
      return getStocktransferTableDate(getid, context, db)
   
   itemcode = request.GET.get('itemcode')
   sender = request.GET.get('sender')
   if itemcode is not None:
      # context['loader'] = 'Yes'
      return ifemptyfunction(request, itemcode, sender, 'store', db)

   
   
   
   if  request.method == 'POST':     
    Warehouse_warehouse(request, context, db)
   return render(request, 'WarehouseToWarehouse.html', context)


@login_required(login_url='/')
@urls_name(name="Warehouse to Outlet")
def WarehouseToOutlet(request):
   db = request.user.company_id.db_name
   getware_H = Warehouse.objects.using(db).all()
   listitems = Item.objects.using(db).all()
   form      = W_O_Form()
   shop = sales_outlet.objects.using(db).all()
   
   refno =  random_string_generator()
   context = {
       'wareH': getware_H,
       'refno': 'Ref_'+refno,
       'listitems': listitems,
       'form': form,
       'shop' : shop,
   }
   if request.method == 'POST':
      Warehouse_outlet(request, context, db)
   return render(request, 'WarehouseToOutlet.html', context)



@login_required(login_url='/')
@urls_name(name="Outlet to Oulet")
def OutletToWarehouse(request):
   db = request.user.company_id.db_name
   getware_H = Warehouse.objects.using(db).all()
   listitems = Item.objects.using(db).all()
   form      = W_O_Form()
   shop = sales_outlet.objects.using(db).all()
   

   refno =  random_string_generator()
   context = {
       'wareH': getware_H,
       'refno': 'Ref_'+refno,
       'listitems': listitems,
       'form': form,
       'shop' : shop,
   }
   if request.method == 'POST':
      outlet_Warehouse(request, context, db)
   return render(request, 'OutletToWarehouse.html', context)


def OutletToOutlet(request):
   db = request.user.company_id.db_name
   getware_H = Warehouse.objects.using(db).all()
   listitems = Item.objects.using(db).all()
   form      = W_O_Form()
   shop = sales_outlet.objects.using(db).all()
   refno =  random_string_generator()
   context = {
       'wareH': getware_H,
       'refno': 'Ref_'+refno,
       'listitems': listitems,
       'form': form,
       'shop': shop,
   }
   if request.method == 'POST':
      outlet_outlet(request, context, db)
   return render(request, 'OutletToOutlet.html', context)




# ********************************************************************************************************
# def NewItem(request):
#    form =  NewItemForm(request.POST or None)
  
#    getcate = Category.objects.all();
#    getitem = Item.objects.all();
#    encountered_categories = Encountered(getcate,'category_name')

#    # Getting sub cate using ajax
#    sub_categories = getNewItemSubcat(request)
#    if sub_categories:
#       return JsonResponse({'data': sub_categories})

#    context = {
#          'getcate': encountered_categories,
#          'form': form,
#          'getitem': getitem,
#       }
#    # POST NEW ITEM DATA
#    saveNewItemdata(request,form, context, NewItemForm())

#    return render(request, 'NewItem.html', context)

# ********************************************************************************************************



# ********************************************************************************************************
@login_required(login_url='/')
@urls_name(name = "Stock Adjustment")
def StockAdjustment(request):
   db = request.user.company_id.db_name
   # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
   stockinlog = CreateStockInLog.objects.using(db).filter(~Q(status='Cancelled'))
   warehouse = Warehouse.objects.using(db).all()
   getitem = Item.objects.using(db).all();

   context = {
      'allinvoice': stockinlog,
      'items': getitem,
      'store': warehouse,
   }
   # function to fetch data for update(when edit btn is clicked)
   data = getStockAdjustmentData(request, CreateStockInLog, db)
   if data:
      return JsonResponse({'data': data})
   
   # update function
   updateStockAdjustmentData(request, CreateStockInLog, CreateStockIn, 'warehouse', context, db)

   # get function
   stockadjustmentdata =getStockAdjustmentDate(request, CreateStockInLog, context, db)
   if stockadjustmentdata:
     return JsonResponse({'data':stockadjustmentdata})

   return render(request, 'StockAdjustment_warehouse.html', context)

# ********************************************************************************************************

# ********************************************************************************************************
@login_required(login_url='/')
@urls_name(name = "Stock Adjustment Outlet")
def StockAdjustmentOutlet(request):
   db = request.user.company_id.db_name
   # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
   stockinlog = CreateOutletStockInLog.objects.using(db).filter(~Q(status='Cancelled'))
   outlet = sales_outlet.objects.using(db).all()
   getitem = Item.objects.using(db).all();

   context = {
      'allinvoice': stockinlog,
      'items': getitem,
      'store': outlet,
   }
   # function to fetch data for update(when edit btn is clicked)
   data = getStockAdjustmentData(request, CreateOutletStockInLog, db)
   if data:
      return JsonResponse({'data': data})
   
   # update function
   updateStockAdjustmentData(request, CreateOutletStockInLog, CreateOutletStockIn, 'outlet', context, db)

   # get function
   stockadjustmentdata =getStockAdjustmentDate(request, CreateOutletStockInLog, context, db)
   if stockadjustmentdata:
     return JsonResponse({'data':stockadjustmentdata})

   return render(request, 'StockAdjustment_Outlet.html', context)

# ********************************************************************************************************





# ********************************************************************************************************

# def ItemCategory(request):
#    form =  NewCategoryForm(request.POST or None)
#    getcate = Category.objects.all();

#    context = {
#        'form' : form,
#        'getcategory': getcate,
#     }
   

#    ItemCategory(request, context, form)

#    return render(request, 'ItemCategory.html', context)

# ********************************************************************************************************

# ********************************************************************************************************

def stockLevel(request, outlet, filter1, filter2):
    db = request.user.company_id.db_name

    if filter1 is not None: 
        shop = request.GET.get('store')
        Itemcode = request.GET.get('Itemcode') 
        searchItem = request.GET.get('searchItem')
        if  Itemcode or searchItem: 
        # if  shop is not None: 
            itemList = Item.objects.using(db).filter(Q(generated_code=Itemcode) | Q(item_name=searchItem))
        else:
            itemList = Item.objects.using(db).all()
    else:
            itemList = Item.objects.using(db).all()
            
    try:
       stock_ = Check_StockLevel_By.objects.using(db).first() #.level or "NO"
      
       if stock_ is not None:
           stock_level = stock_.level
       else:
           stock_level = "NO"

    except Check_StockLevel_By.DoesNotExist:
        stock_level = "NO"


    data = []
    if stock_level == "YES":
        for x in itemList:
                qty = get_grand_total_from_outlet_stockin(x.generated_code, CreateOutletStockIn,  outlet, db, filter1)
                #    itemList.update("'qty':" + str(qty))
                x.qty = qty
                x.outlet = outlet
                entry(x, qty, outlet, data)
               
    else:  
        for x in itemList:
            qty = get_grand_total_from_stock_log(x.generated_code, CreateOutletStockInLog, CreateStockInLog,  outlet, db, filter1, filter2)
            #    itemList.update("'qty':" + str(qty))
            x.qty = qty
            x.outlet = outlet
            entry(x, qty, outlet, data)
  
    return itemList, data


def entry(x, qty, outlet, data):

    qty2 = {
        'category':x.category.category_name,
        'item_name':x.item_name,
        'qty':qty,
        'itemcode': x.generated_code,
        'store':outlet,
        'low_stock_level': "x.low_stock_level",
        'wholesale_price': x.selling_price,
        'wholesale_price': x.wholesale_price,
        'selling_price': x.selling_price,
        'selling_price': x.selling_price
        }
    data.append(qty2)


def OutletStockLevel(request):
    db = request.user.company_id.db_name
    shop = sales_outlet.objects.using(db).all()

    Itemcode = request.GET.get('Itemcode') 
    searchItem = request.GET.get('searchItem')  
    fromdate = request.GET.get('fromdate') 
    todate = request.GET.get('todate') 
    outlet = request.GET.get('store') 

    if Itemcode or searchItem or fromdate or outlet:
        
        filter_conditions = Q()
        filter_sales_conditions = Q()
        if fromdate and todate:
                from_date, to_date = getdate(fromdate, todate)
                filter_conditions &= Q(datetx__range=(from_date, to_date))
                filter_sales_conditions &= Q(invoice_date__range=(from_date, to_date))

        if outlet:
            filter_conditions &= Q(outlet=outlet)
            filter_sales_conditions &= Q(outlet=outlet)


        if searchItem:
            filter_conditions &= Q(item=searchItem)
            filter_sales_conditions &= Q(item_name=searchItem)

        if Itemcode:
            filter_conditions &= Q(item_code=Itemcode)
            filter_sales_conditions &= Q(itemcode=Itemcode)
        
        stock, data = stockLevel(request, outlet, filter_conditions, filter_sales_conditions)
      
        if data is not None:
            stockLeve = list(data)
            return JsonResponse({'data': stockLeve, 'totalqty': "ooooo"})
    else:
    
        filter_conditions = Q(outlet=request.user.outlet)
        filter_sales_conditions = Q()

        stock, data = stockLevel(request, request.user.outlet, filter_conditions, filter_sales_conditions)

    context = {
        'shop' : shop,
        'outlet': stock
    }
 
    return render(request, 'OutletStockLevel.html', context)

# def OutletStockLevel(request):
#    db = request.user.company_id.db_name
#    itemList = Item.objects.using(db).all()
   

   
# #    total = [ for item in getstock]
#    for x in itemList:
#        qty = get_grand_total_from_stock_log(x.generated_code, CreateOutletStockInLog, CreateStockInLog,  request.user.outlet, db)
#     #    itemList.update("'qty':" + str(qty))
#        x.qty = qty


       


#    level = request.session.get('level', 'NO')
#    if level == "YES":
#        stock = CreateOutletStockIn.objects.using(db).all()
#    else:
#         stock = CreateOutletStockInLog.objects.using(db).all()
#    getstock = CreateOutletStockInLog.objects.using(db).all()
#    total_quantity = sum(item.quantity for item in getstock)    
  
# #    listedloop = list(zip_longest(getstock, total))
#    shop = sales_outlet.objects.using(db).all()
#    context = {
#     #   'stock' : listedloop,
#       'totalqty' : total_quantity,
#       'level' : level,
#       'shop' : shop,
#       'outlet': itemList
#    }
#    stock_level_data= getOutletStockLevel(request, db)
#    if stock_level_data is not None:
#      
#       stockLevel, total_quant = stock_level_data
#       return JsonResponse({'data': stockLevel, 'totalqty': total_quant})

#    return render(request, 'OutletStockLevel.html', context)
# ********************************************************************************************************


# ********************************************************************************************************
def WarehouseStockLevel(request):
    db = request.user.company_id.db_name
    warehouse = Warehouse.objects.using(db).all()
   
    Itemcode = request.GET.get('Itemcode') 
    searchItem = request.GET.get('searchItem')  
    fromdate = request.GET.get('fromdate') 
    todate = request.GET.get('todate') 
    outlet = request.GET.get('store') 
   
    if Itemcode or searchItem or fromdate or outlet:
            
        stock = WarehouseStock(Itemcode, searchItem, fromdate, todate, outlet, db)
        
        stock, data = stock.run()
      
        if data is not None:
            stockLeve = list(data)
            return JsonResponse({'data': stockLeve, 'totalqty': "ooooo"})
    else:
        warehous = warehouse.first().warehouse_name 
        if warehous:
            outlet= warehous 
        
        stock = WarehouseStock(Itemcode, searchItem, fromdate, todate, outlet, db)
        stock, data = stock.run()
    
    context = {
        'warehouse' : warehouse,
        'stock': stock
    }
   
    return render(request, 'WarehouseStockLevel.html', context)


# def WarehouseStockLevel(request):
#    db = request.user.company_id.db_name
#    getstock = CreateStockIn.objects.using(db).all()
#    warehouse = Warehouse.objects.using(db).all()
#    total = [get_grand_total_from_stock_log(item, CreateStockInLog, CreateOutletStockInLog,  item.warehouse, db) for item in getstock]
#    listedloop = list(zip_longest(getstock, total))
#    level = request.session.get('level', 'NO')
#    context = {
#       'stock' : listedloop,
#       'warehouse' : warehouse,
#       'level' : level,
#    }
   
#    stock_level_data = getWarehouseStockLevel(request, db)
  
#    if stock_level_data is not None:
#       stockLevel, total_quanti = stock_level_data
#       return JsonResponse({'data': stockLevel, 'totalqty': total_quanti})
   
#    return render(request, 'WarehouseStockLevel.html', context)

# ********************************************************************************************************



# ********************************************************************************************************
@login_required(login_url='/')
@urls_name(name="Stock Level")
def StockLevelComparison(request):
    db = request.user.company_id.db_name
    shop = sales_outlet.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    context = {
      'shop' : shop,
      'warehouse' : warehouse,
    }
    stockcomparison = getStockLevelComparison(request, db)
    if stockcomparison:
        combined_data, total_quantity1, total_quantity2 = stockcomparison
        return JsonResponse({'data': combined_data, 'totalqty1': total_quantity1, 'totalqty2': total_quantity2})

    return render(request, 'StockLevelComparison.html', context)


# ********************************************************************************************************





def autosaveFunction(request, sessionName, context):
   db = request.user.company_id.db_name
   aprove = request.POST.get('aprove',)
   redirectTo = request.POST.get('redirectTo')
   INT = request.session[sessionName] = aprove
   level = Check_StockLevel_By.objects.using(db).all()
   if level.count() <= 0:
       level.create(level=aprove)
   else:
      
       level.update(level=aprove)
   #  request.session.get(aprove, 'yes')
   if INT:
      context["success_message"] =  'Saved'
      return redirect(redirectTo)


def instantTransfer(request):
   context={}
   ifgood = autosaveFunction(request, 'INT', context)
   if ifgood:
      return ifgood
   return render(request, "components/modal/modal2.html", context)

def checkstocklevelby(request):
   context={}
   ifgood = autosaveFunction(request, 'level', context)
   if ifgood:
      return ifgood
   return render(request, "components/modal/modal3.html", context)

















# ===================================  

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages

from django.template.defaultfilters import slugify

from django.http.response import JsonResponse, HttpResponse

from .models import (
    Item, ItemImage, Category, ItemSize, Sub_Category
)

from .forms import (
    ItemForm, EditItemForm, ItemTagForm, ItemSpecificationForm, 
    ItemDescriptionForm, CategoryForm, CouponForm,
    ItemBrandForm, ItemColorForm
)

from settings.models import Warehouse, user_account



from main.models import User




def GetItemCode(request, code_id):
    db = request.user.company_id.db_name
    try:
        item_code = Item.objects.using(db).get(token_id=code_id)
        data = {
                'generated_code': item_code.generated_code,
            }
        return JsonResponse(data)
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'item_code not found'}, status=404)


# def ItemIssue(request):
   
#     return render(request, 'stock/ItemIssue.html')


# def WarehouseToWarehouse(request):

#     warehouse = Warehouse.objects.all()
   
#     return render(request, 'stock/WarehouseToWarehouse.html', {'warehouse': warehouse})


# def WarehouseToOutlet(request):
   
#     warehouse = Warehouse.objects.all()
#     outlet    = user_account.objects.all()

#     context = {
#         'warehouse': warehouse,
#         'outlet': outlet
#     }
#     return render(request, 'stock/WarehouseToOutlet.html',context)


# def OutletToWarehouse(request):

#     warehouse = Warehouse.objects.all()
#     outlet    = user_account.objects.all()

#     context = {
#         'warehouse': warehouse,
#         'outlet': outlet
#     }
   
#     return render(request, 'stock/OutletToWarehouse.html', context)


# def VerifyTransfer(request):
   
#     return render(request, 'stock/VerifyTransfer.html')


# def TransferHistory(request):
   
#     return render(request, 'stock/TransferHistory.html')


# def OutletToOutlet(request):

#     outlet    = user_account.objects.all()

#     context = {
#         'outlet': outlet
#     }
   
#     return render(request, 'stock/OutletToOutlet.html', context)


# def StockAdjustment(request):
   
#     return render(request, 'stock/StockAdjustment.html')


@login_required(login_url='/')
@urls_name(name="Item")
def NewItem(request):
    db = request.user.company_id.db_name
    form = ItemForm(request.POST, request.FILES)

    item = Item.objects.using(db).all()
    item_category = Category.objects.using(db).all()
    sub_category = Sub_Category.objects.using(db).all()
    set_current_user(request.user)
  
    if request.method == 'POST':
        choice = request.POST.get('category')
        choice2 = request.POST.get('sub_category')
        
        if form.is_valid():
            item_inst = form.save(commit=False) 
            item_inst.category_id = choice
            item_inst.sub_category_id = choice2
            item_inst.Userlogin = request.user.username
            item_inst.save(using=db) 

            item_id = item_inst.id 
            items = Item.objects.using(db).get(id=item_id) 
            notify = SetItemNotification(item=items, Userlogin=request.user.username)

            notify.save(using=db)
            messages.success(request,"Item was Created successfully")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ItemForm()
    context = {
        'form': form,
        'item': item,
        'item_category': item_category,
        'sub_category': sub_category,
    }
   
    return render(request, 'stock/NewItem.html', context)

@login_required(login_url='/')
@urls_name(name="Item")
def Update_Item(request, item_id):
    db = request.user.company_id.db_name

    item_category = Category.objects.using(db).all()
    item_sub_category = Sub_Category.objects.using(db).all()

    item_code =     Item.objects.using(db).all()

    edit_item = Item.objects.using(db).get(pk=item_id)

    form = EditItemForm(request.POST, request.FILES, instance=edit_item)

    files = request.FILES.getlist("image")
    choice = request.POST.get('category')
    choice2 = request.POST.get('sub_category')
    
    if request.method == 'POST':
       
        if form.is_valid():
            f = form.save(commit=False)
            f.category_id = choice
            f.sub_category_id = choice2
            f.user = request.user.username
            f.save(using=db)
            for i in files:
                ItemImage.objects.using(db).create(item=f, image=i)
            
                
            messages.success(request, "Item data has been updated successfully")
            return redirect('Stock:NewItem') 
        else:
            pass
            
            form = EditItemForm(instance=edit_item)


    return render(request, 'stock/EditItem.html', {'edit_item': edit_item, 'item_category': item_category,'item_sub_category': item_sub_category, 'item_code': item_code})


def add_item_tag(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        form = ItemTagForm(request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.save(using=db)
            return JsonResponse({'success': True, 'message': 'Item tag added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def add_item_size(request):
    db = request.user.company_id.db_name
    size = ItemSize(item_code=request.POST['item_code'], size=request.POST['size'])
    size.save(using=db)
    messages.success(request, "Size data has been updated successfully")
    return JsonResponse({'success': True, 'message': 'Item Size added successfully'})



def add_item_description(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        form = ItemDescriptionForm(request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.save(using=db)
            return JsonResponse({'success': True, 'message': 'Item description added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})



def add_item_specification(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        form = ItemSpecificationForm(request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.save(using=db)
            return JsonResponse({'success': True, 'message': 'Item specification added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


# ===== ADD ITEM BRAND =====
def add_item_brand(request):
    if request.method == 'POST':
        db = request.user.company_id.db_name
        form = ItemBrandForm(request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.save(using=db)
            return JsonResponse({'success': True, 'message': 'Item brand added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})



# ===== ADD ITEM COLOR =====
def add_item_color(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        form = ItemColorForm(request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.save(using=db)
            return JsonResponse({'success': True, 'message': 'Item brand added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


def coupon(request):
    db = request.user.company_id.db_name
    coupons = Coupon.objects.using(db).all()
    
    return render(request, 'stock/Coupon.html', {'coupons': coupons})

def AddCoupon(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        formdata = CouponForm(request.POST)
        if formdata.is_valid():
          
            form = formdata.save(commit=False)
            form.save(using=db)
            # messages.success(request,"Coupon was added successfully")
            return JsonResponse({'message': 'Form submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})

def EditCoupon(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        coupon = Coupon.objects.using(db).get(id=request.POST.get('id'))
        formdata = CouponForm(request.POST, instance=coupon)
        if formdata.is_valid():
          
            form = formdata.save(commit=False)
            form.save(using=db)
            # messages.success(request,"Coupon was added successfully")
            return JsonResponse({'message': 'Form submitted successfully!'})
        else:
           
            return JsonResponse({'success': False, 'message': 'Invalid request method'})

def DeleteCoupon(request, id):
    db = request.user.company_id.db_name
    coupon = Coupon.objects.using(db).get(id=id)
    coupon.delete()
    return redirect("Stock:Coupon")
    











def item_detail(request, item_id):
    db = request.user.company_id.db_name
    item = Item.objects.using(db).get(id=item_id)
    items = ItemImage.objects.using(db).filter(item=item_id,)
    return render(request, "stock/item_details.html", {"detail": item, "details": items})

@login_required(login_url='/')
@urls_name(name="Item")
def DeleteItem(request, id):
    db = request.user.company_id.db_name
    delete_item = Item.objects.using(db).get(id=id)
    delete_item.delete()
    messages.success(request, "Itemn deleted successfully")
    return redirect('Stock:NewItem')


@login_required(login_url='/')
@urls_name(name="Item Category")
def ItemCategory(request):
    db = request.user.company_id.db_name
    
    item_category = Category.objects.using(db).all()

  

    if request.method == "POST":

        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form_i = form.save(commit=False)
           
            form_i.save(using=db)
            messages.success(request, "Category Added Successful")
           
            return redirect('Stock:ItemCategory')
           
        else:
            pass
    else:
        form = CategoryForm()
   
    return render(request, 'stock/ItemCategory.html', {'item_category': item_category})
    
@login_required(login_url='/')
@urls_name(name="Item Category")
def EditItemCategory(request, id):
    db = request.user.company_id.db_name
    edit_cat = Category.objects.using(db).get(id=id)

    form = CategoryForm(request.POST, request.FILES, instance=edit_cat)
    
    if request.method == "POST":
        if form.is_valid():
            form_i = form.save(commit=False)
           
            form_i.save(using=db)
            messages.success(request, "Category data has been updated successfully")
            return redirect('Stock:ItemCategory')
    return render(request, 'stock/EditCategory.html', {'edit_cat': edit_cat})





# def OutletStockLevel(request):
   
#     return render(request, 'stock/OutletStockLevel.html')

# def WarehouseStockLevel(request):
   
#     return render(request, 'stock/WarehouseStockLevel.html')

# def StockLevelComparison(request):
   
#     return render(request, 'stock/StockLevelComparison.html')


def category_details(request, category_id):
    db = request.user.company_id.db_name
    category = Category.objects.using(db).get(id=category_id)
    subcategories = Sub_Category.objects.using(db).filter(main_category=category).values('name')

    category_data = {
        'id': category.id,
        'category_name': category.category_name,
        'description': category.description,
        'cat_img': category.cat_img.url if category.cat_img else None,
        'subcategories': list(subcategories),
    }


    return JsonResponse({'category': category_data})


import json

def update_item_category(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        main_category_name = request.POST.get('main_category')
        sub_category_name = request.POST.get('name')

      
        # Update the Category description
        category = Category.objects.using(db).get(category_name=main_category_name)
        category.description = sub_category_name
       
        category.save()

        # Insert multiple subcategories
        sub_categories = sub_category_name.split(',')

        for sub_category in sub_categories:
            Sub_Category.objects.using(db).create(main_category=category, name=sub_category)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

def get_sub_category(request, category_id):
    db = request.user.company_id.db_name
 
    if request.method == 'GET':
        category = Category.objects.using(db).get(id=category_id)
        data = Sub_Category.objects.using(db).filter(main_category=category).values() or []

    return JsonResponse({'data': list(data)}, safe=False)






@login_required(login_url='/')
@urls_name(name="Item Category")
def fetch_subcategories(request, category_id):
    db = request.user.company_id.db_name
    category = get_object_or_404(Category, using=db, id=category_id)
    subcategories = Sub_Category.objects.filter(main_category=category)

    # subcategory_list = [{'id': sub.id, 'name': sub.name} for sub in subcategories]

    # return JsonResponse({'subcategories': subcategory_list})
    return render(request, 'stock/ItemCategory.html', {'subcategories': subcategories})



class WarehouseStock:
    def __init__(self, Itemcode, searchItem, fromdate, todate, warehouse, db) -> None:
        self.item_code = Itemcode
        self.item_name = searchItem
        self.fromdate = fromdate
        self.todate = todate
        self.warehouse = warehouse
        self.db = db
        # self.run()
        
    def run(self):
        
        filter_conditions = Q()
        if self.fromdate and self.todate:
                from_date, to_date = getdate(self.fromdate, self.todate)
                filter_conditions &= Q(datetx__range=(from_date, to_date))

        if self.warehouse:
            filter_conditions &= Q(warehouse=self.warehouse)


        if self.item_name:
            filter_conditions &= Q(item=self.item_name)

        if self.item_code:
            filter_conditions &= Q(item_code=self.item_code)
        try:
            # stock_level = Check_StockLevel_By.objects.using(self.db).first().level
            stock_ = Check_StockLevel_By.objects.using(self.db).first() #.level or "NO"
      
            if stock_ is not None:
                stock_level = stock_.level
            else:
                stock_level = "NO"
        except Check_StockLevel_By.DoesNotExist:
            stock_level = "NO"
        
      
       
        if filter_conditions is not None: 
            shop = self.warehouse
            if  self.item_code or self.item_name: 
                itemList = Item.objects.using(self.db).filter(Q(generated_code=self.item_code) | Q(item_name=self.item_name))
            else:
                itemList = Item.objects.using(self.db).all()
               
        else:
            itemList = Item.objects.using(self.db).all()  

       
        data = []
        if stock_level == "YES":
            for x in itemList:
                qty,  low_stock_level = self.get_grand_total_from_warehouse_stockin(x.generated_code, CreateStockIn, filter_conditions,  self.db)
                #    itemList.update("'qty':" + str(qty))
                x.qty = qty
                x.outlet = self.warehouse
                x.low_stock_level =  low_stock_level
                entry(x, qty, self.warehouse, data)
                
        else:  
            for x in itemList:
                qty = self.warehouse_stock_log_level(x.generated_code, CreateStockInLog, CreateOutletStockInLog, filter_conditions, self.db)
                #    itemList.update("'qty':" + str(qty))
                x.qty = qty
                x.outlet = self.warehouse
                x.warehouse = self.warehouse
                entry(x, qty, self.warehouse, data)
               
        return itemList, data

    def get_grand_total_from_warehouse_stockin(self, item, table, filter_conditions, db):
      
        try:
            item = table.objects.using(db).get(filter_conditions, item_code=item)
            qty  = item.quantity
            low_stock_level = item.low_stock_level
        except table.DoesNotExist:
            qty = 0.00
            low_stock_level = 0.00
        except table.MultipleObjectsReturned:
            qty = table.objects.using(db).filter(filter_conditions).aggregate(total=Sum('quantity'))['total'] or 0.00
        return qty, low_stock_level
    
    def warehouse_stock_log_level(self, item, table1, table2, filter_conditions, db):
      
      # WHEN INSTANT STOCKLEVEL IS SET TO NO
      warehouse_queryset = table1.objects.using(db).filter(filter_conditions, item_code=item)
      warehousePurchase = warehouse_queryset.aggregate(total=Sum('quantity'))['total'] or 0.00
    #   warehouse = warehouse_queryset.first().warehouse
    #   low_stock_level = warehouse_queryset.first().low_stock_level
      # this represents the minuses in qty the shop/warehouse get
      transfer_from_outlet_to_warehouse = table1.objects.using(db).filter(outlet=self.warehouse,item_code=item).aggregate(total=Sum('quantity'))['total'] or 0.00
      transfer_from_warehouse_to_outlet = table2.objects.using(db).filter(filter_conditions, item_code=item).aggregate(total=Sum('quantity'))['total'] or 0.00
   

      add =  Decimal(warehousePurchase) + Decimal(transfer_from_outlet_to_warehouse)
      total =  add - Decimal(transfer_from_warehouse_to_outlet)
  
      return total
      

@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def NewStockin(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    item = Item.objects.using(db).all()


    invoiceID =  random_string_generator()

    
    if request.method == "POST":
           
        # outlet = User.objects.get(id = request.user.id).outlet
        # if outlet:
           add_stockin_invoice(request, db)
           return redirect('Stock:NewStokin')
        # else:
        #     messages.error(request, "Assign outlet to logged in user")
     
   
    context = {
        'supplier': supplier,
        'warehouse': warehouse,
        'outlet': outlet,
        'item': item,
       'invoiceID': 'INV_'+invoiceID,

    }
    return render(request, 'stock/NewStockin.html', context)
