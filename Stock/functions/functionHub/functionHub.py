from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,Http404;
from django.views.decorators.csrf import csrf_exempt;
import json
from datetime import datetime
from itertools import zip_longest
from decimal import Decimal


from Stock.models import *;
from  customer.models import *;
from Stock.Forms.forms import *
from Stock.Forms.new_categoryForm import*;
from Stock.Forms.new_itemForm import*;
from Stock.Forms.stockTransferForm import *;
from Stock.Forms.StockoutForm import*;
# from Stock.functions.functionHub.Stokinfunctions import *
from Stock.functions.verifyFunctions.verify import *
from Stock.functions.globalFunctions.globalFunctions import *

from vendor.models import vendor_table
from vendor.forms import VendorInovoiceForm
from django.contrib import messages


def getdate(fromdate, todate):
   from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
   to_date = datetime.strptime(todate, '%Y-%m-%d').date()
   return from_date, to_date


def getStockOutInvoiceData(getinvoiceID, context, db):
      context['loader'] = 'Yes'
      cusName = getonedata(getinvoiceID, 'customer_name', db)
      getordernumber = getonedata(getinvoiceID, 'order_ID', db)
      items =  getCustomerPurchasedItems(getinvoiceID, db)
      total, vat =  Calculate(getinvoiceID, Decimal(7.5), db)
      formatted_vat = '{:.2f}'.format(vat)
      return JsonResponse({'cusName': cusName, 'getordernumber': getordernumber, 'data':items, 'subtotal':total, "vat":formatted_vat})
   

def verifyStockout(request, context, db):
   # a post method
   getinvoiceIDPOST = request.POST.get('getinvoiceID')
   if request.method == "POST":
      getinvoice = customer_invoice.objects.using(db).filter(invoiceID=getinvoiceIDPOST, status=0);
      getlent = len(getinvoice)
      allgood = False
      for i in getinvoice:
         context['loader'] = 'Yes'
         i.status = 1
         i.save(using=db)
         if i:
            allgood = True
         else:
            allgood = False
         getlent -=1
      if getlent == 0:
         context['loader'] = 'No'
         if allgood:
            context["success_message"] =  'Item Successfully StockedOut'
         else:
            context["error_message"] =  'StockedOut Failed'



def getStocktransferTableDate(getid, context, db):   
    getitem = Item.objects.using(db).get(generated_code=getid)
    if getitem:
        return JsonResponse({'des': getitem.description, 'qty':getitem.size, 'item':getitem.item_name, 'price':getitem.selling_price, 'code':getitem.generated_code, 'wholesale_price':getitem.wholesale_price, 'id':getitem.id})
    
def ifemptyfunction(request,id, sender, buttonoutlet, db):
  
   err = "Item not found in " + sender if sender != '' and '_ _select' not in sender  else "Item not found because you haven\'t selected store"
   get_buttonoutlet = request.GET.get(buttonoutlet)
   if get_buttonoutlet == 'outlet':
      try:
         getitem = CreateOutletStockIn.objects.using(db).get(item_code=id, outlet=sender)
         getQty = getitem.quantity
         if getQty:
            return JsonResponse({'getQty':getQty})
      except CreateOutletStockIn.DoesNotExist:
         return JsonResponse({'failed':err })
   else:
 
      try:
         # getitem = CreateOutletStockIn.objects.using(db).get(item_code=id, warehouse=sender)
         getitem = CreateStockIn.objects.using(db).get(item_code=id, warehouse=sender)
         getQty = getitem.quantity
         if getQty:
            return JsonResponse({'getQty':getQty})
      except CreateStockIn.DoesNotExist:
         return JsonResponse({'failed':err })
   


def DoSomething(checkexist, quantity, item, i, context, INT, db):
    oldQty = checkexist.quantity
   
    if oldQty < int(quantity[i]):
        context["error_message"] = f"We only have {oldQty} {item[i]} left"
        
    # ELSE USE A JS ALERT TO TRANSFER ANYWAY
    else:
      if INT == 'Yes':
         newQty = float(oldQty) - float(quantity[i])
         checkexist.quantity = newQty
         checkexist.save(using=db)
      return True


def DoSomethingElse(context,item, i, store):
    context["error_message"] =  item[i] +' Item not found in '+ store 
    return False


def getStockInLog(request, db):
   StockInLog = None
   search = request.GET.get('transferType')

   if search == 'W_W' or search == 'O_W':
      StockInLog = CreateStockInLog

   if search == 'W_O' or search == 'O_O':
      StockInLog = CreateOutletStockInLog

   ifFailed = {'failed': "No Data Found"}
   if StockInLog is not None:
      getUnverified = StockInLog.objects.using(db).filter(status='Unverified', transfer=search)
      if getUnverified :
         unverified = [
            (
               {
                  'id': item.id if item and item.id is not None else None,
                  'datetx': item.datetx if item and item.datetx is not None else None,
                  'items': item.item if item and item.item is not None else None,
                  'outlet': item.outlet if item and item.outlet is not None else None,
                  'warehouse': item.warehouse if item and item.warehouse is not None else None,
                  'token_id': item.token_id if item and item.token_id is not None else None,
                  'quantity': item.quantity if item and item.quantity is not None else None,
                  'item_code': item.item_code if item and item.item_code is not None else None,
                  'transfer': item.transfer if item and item.transfer is not None else None,
               })
               for item in getUnverified
            ]
         
         return unverified
      else:
         return ifFailed
      # return JsonResponse({'data': stockLevel, 'totalqty': total_quantity})
      # context['Unverified'] = getUnverified


def getTransferHistory(request, db):
   selectItem     = request.GET.get('selectItem')
   selectFrom     = request.GET.get('selectFrom')
   selectTo       = request.GET.get('selectTo')
   searchcode     = request.GET.get('searchItem')
   fromdate       = request.GET.get('fromdate')
   todate         = request.GET.get('todate')
   selectTransfer = request.GET.get('selectTransfer')
   from_date = None
   to_date = None
   filterdata = None;
   if request.method == 'GET':
      # ifFailed = {'failed': "No Data Found"}
      # if searchcode or fromdate or todate:
      if fromdate and todate is not None:
         from_date, to_date =getdate(fromdate, todate)
      if selectItem or selectFrom and selectTo or searchcode or fromdate and todate is not None:
         filterdata1 =  CreateStockInLog.objects.using(db).filter(Q(status='Verified'), Q(item=selectItem)  | Q(warehouse=selectFrom) & Q(outlet=selectTo) | Q(transfer=selectTransfer) | Q(datetx__range=(from_date, to_date)) | Q(item_code=searchcode))
         filterdata2 =  CreateOutletStockInLog.objects.using(db).filter(Q(status='Verified'), Q(item=selectItem)  | Q(warehouse=selectFrom) & Q(outlet=selectTo) | Q(transfer=selectTransfer) | Q(datetx__range=(from_date, to_date)) | Q(item_code=searchcode))
         filterdata = list(zip_longest(filterdata1, filterdata2))

         if filterdata:
            result = [({
                  'datetx': data.datetx if data and data.datetx is not None else data2.datetx,
                  'item_code': data.item_code if data and data.item_code is not None else data2.item_code,
                  'item': data.item if data and data.item is not None else data2.item,
                  'selling_price': data.selling_price if data and data.selling_price is not None else data2.selling_price,
                  'quantity': data.quantity if data and data.quantity is not None else data2.quantity,
                  'warehouse': data.warehouse if data and data.warehouse is not None else data2.warehouse,
                  'outlet': data.outlet if data and data.outlet is not None else data2.outlet,
                  'token_id': data.token_id if data and data.token_id is not None else data2.token_id,
                  'Userlogin': data.Userlogin if data and data.Userlogin is not None else data2.Userlogin,
                  'ref_no': data.ref_no if data and data.ref_no is not None else data2.ref_no,
                  'id': data.id if data and data.id is not None else data2.id,
                  })
                  for data, data2 in filterdata
               ]
            return result
      # else:
      #    return ifFailed

   


def getStockAdjustmentData(request, model, db):
   if request.method == 'GET':
      getinvoiceID = request.GET.get('invoiceID')
      getidcode = request.GET.get('idcode')
      if getinvoiceID or getidcode:
         ifFailed = {'failed': "No Data Found"}
         
         getid = model.objects.using(db).get(Q(id=getidcode))
         fetchonce = {
            'item':getid.item,
            'invoice_no':getid.invoice_no,
            'date':getid.datetx,
            'description':getid.item_decription,
            'qty':getid.quantity,
            'id':getid.id,
         }
         if fetchonce:
            return fetchonce
         else:
            return ifFailed

         


def getStockAdjustmentDate(request, model, context, db):
   if request.method == 'GET':
      getfromdate = request.GET.get('fromdate')
      gettodate = request.GET.get('todate')
      sortbyWareHh = request.GET.get('sortbyWareHh')
      sortbyItem = request.GET.get('sortbyItem')
      failed = {'failed': "No Data Found"}
      if getfromdate and gettodate:
         from_date, to_date =getdate(getfromdate, gettodate)
         getstockdata = model.objects.using(db).filter(Q(datetx__range=(from_date, to_date)) & ~Q(status='Cancelled'))
         if getstockdata:
            getstock = getstockdata
      if sortbyItem or sortbyWareHh is not None:
         # whatever is in outlet is what i have in stock(installed) so i sort by outlet, that is == warehouse(sortby)
         getstock = model.objects.using(db).filter(Q(outlet=sortbyWareHh) | Q(item_code=sortbyItem) & ~Q(status='Cancelled'))
         if getstock:
            result = [({
                  'id': data.id if data and data.id is not None else None,
                  'datetx': data.datetx if data and data.datetx is not None else None,
                  'invoice_no': data.invoice_no if data and data.invoice_no is not None else None,
                  'item': data.item if data and data.item is not None else None,
                  'quantity': data.quantity if data and data.quantity is not None else None,
                  'item_decription': data.item_decription if data and data.item_decription is not None else None,
                  'token_id': data.token_id if data and data.token_id is not None else None,
                  })
                  for data in getstock
               ]
            return result
         else:
            return failed




def updateStockAdjustmentData(request, model, model2, store, context, db):
   if request.method == 'POST':
      form_qty = request.POST.get('modalNewqty')
      form_id = request.POST.get('modalID')
      form_invoiceID = request.POST.get('modalinvoiceID')
      

      
      try:
         getqty = model.objects.using(db).get(id=form_id)
         get_qty_from_stockin = model2.objects.using(db).get(Q(**{store:getqty.outlet}), Q(item_code=getqty.item_code))
         stockinQty =get_qty_from_stockin.quantity
         if form_invoiceID is None:
            form_invoiceID = getqty.token_id
            
         if float(form_qty) > float(getqty.quantity):
            currentQty = float(form_qty) - float(getqty.quantity)
            get_qty_from_stockin.quantity = float(stockinQty) + float(currentQty)
            # stockinLog qty update
            getqty.quantity = form_qty
            getqty.save(using=db)
         else:
            currentQty = float(getqty.quantity) - float(form_qty)
            get_qty_from_stockin.quantity = float(stockinQty) - float(currentQty)
            # stockinLog qty update
            getqty.quantity = form_qty
            getqty.save(using=db)

         # stockin qty update
         get_qty_from_stockin.save(using=db)
         Stock_Adjustment_Log = StockAdjustmentLog.objects.using(db).create(
            invoice_no=form_invoiceID,
            initial_qty=stockinQty,
            new_qty=get_qty_from_stockin.quantity,
            item_code=getqty.item_code,
            Userlogin=request.user,               
            type='stock',               
         )

         if getqty and get_qty_from_stockin and Stock_Adjustment_Log:
           context['success_message'] = 'Quantity Updated'
         else:
           context['error_message']   = 'Update Failed'

      except model.DoesNotExist:
         context['error_message']   = 'Data Not found'


def ItemCategory(request, context, form):
   db = request.user.company_id.db_name

   if request.method == 'POST':

      if form.is_valid():
         category_name = form.cleaned_data.get('category_name')
         sub_category = form.cleaned_data.get('sub_category')
         try:
            Category.objects.using(db).get(Q(category_name=category_name), Q(sub_category=sub_category))
            context["error_message"] = 'Data already exists'
         except Category.DoesNotExist:
            form.save(using=db)
            context['success_message']    = 'Category Saved'
            context['forms']              = NewCategoryForm()
            # context['getcategory']        = getcate

      else:
          
         pass
   else:
      pass
    


def getNewItemSubcat(request):
   
   getsub= request.GET.get('data')
   getsubcate = Category.objects.filter(category_name=getsub);
   # output = '';
   if getsubcate:
      sub_categories = [i.sub_category for i in getsubcate]
      return sub_categories

def saveNewItemdata(request,form, context, forms):
   db = request.user.company_id.db_name

   # POST NEW ITEM DATA
   if request.method == 'POST':
         if form.is_valid():
            form.save(using=db)
            context['success_message'] = 'New item Saved'
            context['form'] = forms
         else:
             context['error_message'] = 'Failed to save';

from django.db.models import Sum
from decimal import Decimal

def get_grand_total_from_outlet_stockin(item, table, outlet, db, filter1):
   
   try:
      qty = transfer_to_outlet = table.objects.using(db).get(filter1, item_code=item).quantity
   except table.DoesNotExist:
      qty = 0.00
   except table.MultipleObjectsReturned:
      qty = table.objects.using(db).filter(filter1, item_code=item).aggregate(total=Sum('quantity'))['total'] or 0.00
   return qty


def get_grand_total_from_stock_log(item, table1, table2, storeData, db, filter1, filter2):
     
      # WHEN INSTANT STOCKLEVEL IS SET TO NO
      transfer_to_outlet = table1.objects.using(db).filter(filter1, item_code=item).aggregate(total=Sum('quantity'))['total'] or 0.00
      # transfer_to_outlet = table1.objects.using(db).filter(Q(outlet=storeData) & Q(item_code=item)).aggregate(total=Sum('quantity'))['total'] or 0.00

      # this represents the minuses in qty the shop/warehouse get
      transfer_from_outlet_to_oulet = table1.objects.using(db).filter(filter1, Q(warehouse=storeData) & Q(item_code=item)).aggregate(total=Sum('quantity'))['total'] or 0.00
      transfer_to_warehouse = table2.objects.using(db).filter(filter1, Q(warehouse=storeData) & Q(item_code=item)).aggregate(total=Sum('quantity'))['total'] or 0.00
      
      salesQty = customer_invoice.objects.using(db).filter(filter2,itemcode=item,  cancellation_status="0", status="1").aggregate(total=Sum('qty'))['total'] or 0.00
      # salesQty = customer_invoice.objects.using(db).filter(itemcode=item, outlet="", cancellation_status="0", status="1").aggregate(total=Sum('qty'))['total'] or 0.00
      
      
      minus =  Decimal(transfer_from_outlet_to_oulet) + Decimal(transfer_to_warehouse) + Decimal(salesQty)
      total = Decimal(transfer_to_outlet) - minus 
      
     
      return total

def warehouse_stock_log_level(item, table1, table2, warehouse, db):
      # WHEN INSTANT STOCKLEVEL IS SET TO NO
      warehousePurchase = table1.objects.using(db).filter(Q(warehouse=warehouse) & Q(item_code=item)).aggregate(total=Sum('quantity'))['total'] or 0.00

      # this represents the minuses in qty the shop/warehouse get
      transfer_from_outlet_to_warehouse = table1.objects.using(db).filter(Q(outlet=warehouse) & Q(item_code=item)).aggregate(total=Sum('quantity'))['total'] or 0.00
      transfer_from_warehouse_to_outlet = table2.objects.using(db).filter(Q(warehouse=warehouse) & Q(item_code=item)).aggregate(total=Sum('quantity'))['total'] or 0.00
   
      
      add =  Decimal(warehousePurchase) + Decimal(transfer_from_outlet_to_warehouse)
      total =  add - Decimal(transfer_from_warehouse_to_outlet)
      
      # total_pluses = sum(item.quantity for item in all_pluses)
      # total_minuses = sum(item.quantity for item in minuses_within_table)
      # total_minuses2 = sum(item.quantity for item in minuses_outside_table)
      # final_total_minuses = total_minuses + total_minuses2
      # grandtotal = total_pluses - final_total_minuses
      return total


def getitem(val, db):
   getval = Item.objects.using(db).get(generated_code=val)
   return getval


def get_data_from_main_tables(request, table, store, db):
   getitemcode = request.GET.get('Itemcode')
   getitemname = request.GET.get('searchItem')
   getstore     = request.GET.get('store')
   fromdate    = request.GET.get('fromdate')
   todate      = request.GET.get('todate')
   INSTOCKLEVEL = request.session.get('level', 'NO')
   getstock2 = False
   from_date = None
   to_date = None
   if fromdate and todate is not None:
      from_date, to_date =getdate(fromdate, todate)

   if getitemcode or getitemname or getstore or fromdate and todate is not None:
      getstock2 = table.objects.using(db).filter(Q(datetx__range=(from_date, to_date)) | Q(item_code=getitemcode) | Q(item=getitemname) | Q(**{store:getstore}))#**{store:storeData}
   return getstock2, INSTOCKLEVEL

def stocklevelfinalresult(stockLevel, item, grandtotal, INSTOCKLEVEL, data, db):

   # WHEN INSTANT STOCKLEVEL IS SET TO YES
   if INSTOCKLEVEL == 'YES':
      grandtotal = item.quantity
   stockLevel.append({
      'id': item.id if item and item.id is not None else None,
      'datetx': item.datetx if item and item.datetx is not None else None,
      'items': item.item if item and item.item is not None else None,
      'qty': grandtotal if item and grandtotal is not None else None,
      'itemcode': item.item_code if item and item.item_code is not None else None,
      'store': data if item and data is not None else None,
      'low_stock_level': item.low_stock_level if item and item.low_stock_level is not None else None,
      'wholesale_price': getitem(item.item_code, db).wholesale_price if item else item.wholesale_price,
      'selling_price': getitem(item.item_code, db).selling_price if item else item.selling_price,
   })
   return stockLevel

def getOutletStockLevel(request, db):
   result, INSTOCKLEVEL = get_data_from_main_tables(request, CreateOutletStockIn, 'outlet', db)
   if result :
      total_quantity = sum(item.quantity for item in result)
      stockLevel = []
      for item in result:
         grandtotal = get_grand_total_from_stock_log(item, CreateOutletStockInLog, CreateStockInLog,  item.outlet, db)
         stockLevels = stocklevelfinalresult(stockLevel, item, grandtotal, INSTOCKLEVEL, item.outlet, db)
      return stockLevels, total_quantity


def getWarehouseStockLevel(request, db):
   result, INSTOCKLEVEL = get_data_from_main_tables(request, CreateStockIn, 'warehouse', db)
   if result:
      total_quantity = sum(item.quantity for item in result)
      stockLevel= []
      for item in result:
         grandtotal = get_grand_total_from_stock_log(item, CreateStockInLog, CreateOutletStockInLog,  item.warehouse, db)
         stockLevels = stocklevelfinalresult(stockLevel, item, grandtotal, INSTOCKLEVEL, item.warehouse, db)
      return  stockLevels, total_quantity




# def getStockLevelComparison(request):
#    getitemcode = request.GET.get('Itemcode')
#    getitemname = request.GET.get('searchItem')
#    getshop = request.GET.get('selectshop')
#    getwarehouse = request.GET.get('selectwarehouse')
#    INSTOCKLEVEL = request.session.get('level', 'NO')
#    combined_data=[]
#    grandtotalforwarehouse= None
#    grandtotaforshop= None
#    getstock1 = CreateStockIn.objects.filter(Q(item_code=getitemcode) | Q(item=getitemname) | Q(warehouse=getwarehouse))
#    getstock2 = CreateOutletStockIn.objects.filter(Q(item_code=getitemcode) | Q(item=getitemname) | Q(outlet=getshop))
#    compare_data = list(zip_longest(getstock1, getstock2))
#    total_quantity1 = sum(item.quantity for item in getstock1)
#    total_quantity2 = sum(item.quantity for item in getstock2)
   

#    if getstock1 or getstock2:
#       for item1, item2 in compare_data:
#          if item1:
#             grandtotalforwarehouse = (item1, CreateStockInLog, CreateOutletStockInLog,   item1.warehouse)
#          if item2:
#             grandtotaforshop = get_grand_total_from_stock_log(item2, CreateOutletStockInLog, CreateStockInLog,  item2.outlet,)

#          if INSTOCKLEVEL == 'YES':
#             if item1:
#                grandtotalforwarehouse = item1.quantity
#             if item2:
#                grandtotaforshop       = item2.quantity
#          combined_data.append(
#                {
#                   'id': item1.id if item1 and item1.id is not None else item2.id,
#                   'items': item1.item if item1 and item1.item is not None else item2.item,
#                   'qty1': grandtotalforwarehouse if item1 and grandtotalforwarehouse is not None else None,
#                   'qty2': grandtotaforshop if item2 and grandtotaforshop is not None else None,
#                   'datetx': item1.datetx if item1 and item1.datetx is not None else item2.datetx,
#                   'itemcode': item1.item_code if item1 and item1.item_code is not None else item2.item_code,
#                   'store1': item1.warehouse if item1 and item1.warehouse is not None else None,
#                   'store2': item2.outlet if item2 and item2.outlet is not None else None,
#                })
#       return combined_data, total_quantity1, total_quantity2
   



def getStockLevelComparison(request, db):
   getitemcode = request.GET.get('Itemcode')
   getitemname = request.GET.get('searchItem')
   getshop = request.GET.get('selectshop')
   getwarehouse = request.GET.get('selectwarehouse')
   INSTOCKLEVEL = Check_StockLevel_By.objects.using(db).first() #request.session.get('level', 'NO')
   combined_data=[]
   grandtotalforwarehouse= None
   grandtotaforshop= None
   if getitemcode or getitemname or getshop or getwarehouse :
      getstock1 = CreateStockIn.objects.using(db).filter(Q(item_code=getitemcode) | Q(item=getitemname) | Q(warehouse=getwarehouse))
      getstock2 = CreateOutletStockIn.objects.using(db).filter(Q(item_code=getitemcode) | Q(item=getitemname) | Q(outlet=getshop))
      compare_data = list(zip_longest(getstock1, getstock2))
      total_quantity1 = sum(item.quantity for item in getstock1)
      total_quantity2 = sum(item.quantity for item in getstock2)
      

      if getstock1 or getstock2:
         for item1, item2 in compare_data:
            if item1:
               grandtotalforwarehouse = get_grand_total_from_stock_log(item1, CreateStockInLog, CreateOutletStockInLog,   item1.warehouse, db)
            if item2:
               grandtotaforshop = get_grand_total_from_stock_log(item2, CreateOutletStockInLog, CreateStockInLog,  item2.outlet, db)

            if INSTOCKLEVEL == 'YES':
               if item1:
                  grandtotalforwarehouse = item1.quantity
               if item2:
                  grandtotaforshop       = item2.quantity
            combined_data.append(
                  {
                     'id': item1.id if item1 and item1.id is not None else item2.id,
                     'items': item1.item if item1 and item1.item is not None else item2.item,
                     'qty1': grandtotalforwarehouse if item1 and grandtotalforwarehouse is not None else None,
                     'qty2': grandtotaforshop if item2 and grandtotaforshop is not None else None,
                     'datetx': item1.datetx if item1 and item1.datetx is not None else item2.datetx,
                     'itemcode': item1.item_code if item1 and item1.item_code is not None else item2.item_code,
                     'store1': item1.warehouse if item1 and item1.warehouse is not None else None,
                     'store2': item2.outlet if item2 and item2.outlet is not None else None,
                  })
         return combined_data, total_quantity1, total_quantity2
   



def add_stockin_invoice(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    invoice_id = request.POST.get('invoiceID')
    order_id = request.POST.get('orderID')

    account_id = request.POST.get('account_id')
    warehouse = request.POST.get('warehouse')
    p_method = request.POST.get('source')
    outlet = request.POST.get('outlet')
    vendor_name = request.POST.get('vendor_name')
    Gdescription = request.POST.get('Gdescription')
    invoice_date = request.POST.get('invoice_date')
    due_date = request.POST.get('due_date')
    item_name = request.POST.getlist('item_name')
    itemcode = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities = request.POST.getlist('qty[]')
    unit = request.POST.getlist('unit[]')
    discount = request.POST.getlist('discount[]')
    amount = request.POST.getlist('amount[]')
    total = request.POST.get('total')
    vat = request.POST.get('vat')
    amount_paid = request.POST.get('amount_paid')
    amount_expected = request.POST.get('amount_expected')
    


    # total = float(request.POST['total'])
  
    if p_method == "Cash":
        amount_paid = total
        amount_expected = total
    else:
        amount_paid = 0.00
        amount_expected = total


    transaction_source = "Purchase"
    source = "New Stock"

    if vendor_name:
        ven = vendor_table.objects.using(db).get(id=vendor_name)
       

    
    # Count the number of records in the Sales_Outlet model
    # outlet_count = sales_outlet.objects.count()
    check_outlet = User.objects.get(id = request.user.id).outlet

    stock_in = CreateStockIn.objects.using(db).all()
    

    for i in range(len(itemcode)):

            # Check if the itemcode (value) is equal to 0

        if str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            vendor_invoice_form_data = {
                'cusID': ven.custID,
                'vendor_name': ven.name,
                'invoiceID': invoice_id,
                'orderID': order_id,
                'Gdescription': Gdescription,
                'invoice_date': invoice_date,
                'due_date' : due_date,
                'amount_paid' : amount_paid,
                'amount_expected': amount_expected,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_descriptions': item_descriptions[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'total': total
            }
            
            vendor_form = VendorInovoiceForm(vendor_invoice_form_data)
            
            
            if vendor_form.is_valid():
                
               form_i = vendor_form.save(commit=False)
               form_i.Userlogin = request.user.username
               # form_i.save(using=db)

                
                # stock_in = Stock_In.objects.filter(warehouse=warehouse, item_code=itemcode).first()
               
               if outlet is not "":
                  try:
                        stock_in_outlet_query = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode[i])
                        stock_in_outlet_query.quantity = int(stock_in_outlet_query.quantity) + int(quantities[i])
                        stock_in_outlet_query.save(using=db)
                  except CreateOutletStockIn.DoesNotExist:
                        saveOutlet(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i)
                        saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, None)

                  if not message_displayed:     
                     messages.success(request, "Items Stocked in successfully")
                     message_displayed = True  # Update the message_displayed variable      
               else:
                  ## INSTANT TRANSFER
                  if warehouse is None:
                     messages.error(request, "Select outlet or warehouse")
                  else:
                     # STOCK IN WAREHOUSE
                     if warehouse is not '':
                           try:
                              stock_in_query = CreateStockIn.objects.using(db).get(warehouse=warehouse, item_code=itemcode[i])
                              stock_in_query.quantity += int(quantities[i])
                              stock_in_query.save(using=db)
                           except CreateStockIn.DoesNotExist:
                              saveStockin(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)
                           saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i)

                     if not message_displayed:
                           
                        messages.success(request, "Items Stocked in successfullyy")
                        message_displayed = True  # Update the message_displayed variable
            else:
                return HttpResponse('error')
            





def saveStockin(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i):
    stock_in = CreateStockIn(
        supplier=vendor_name,
        invoice_no=invoice_id,
        order_no=order_id,
        warehouse=warehouse,
        description=Gdescription,
        item=item_name[i],
        item_decription=item_descriptions[i],
        quantity=int(quantities[i]),
        manufacture_date=invoice_date,
        expiry_date=due_date,
        item_code=itemcode[i],
        Userlogin = request.user.username
    )
    stock_in.save(using=db)


def saveStockinLog(invoice_date, vendor_name, invoice_id, order_id, warehouse, Gdescription, item_name, item_descriptions, quantities, due_date, itemcode, request, db, i):
    stock_in = CreateStockInLog(
        supplier=vendor_name,
        invoice_no=invoice_id,
        order_no=order_id,
        outlet=warehouse,
        description=Gdescription,
        item=item_name[i],
        item_decription=item_descriptions[i],
        quantity=int(quantities[i]),
        manufacture_date=invoice_date,
        expiry_date=due_date,
        item_code=itemcode[i],
        Userlogin = request.user.username
    )
    stock_in.save(using=db)


def saveOutlet(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i):
    outlet_stockin = CreateOutletStockIn(
            datetx = invoice_date,
            supplier = vendor_name,
            invoice_no=invoice_id,
            order_no=order_id,
            outlet = check_outlet,
            description = Gdescription,
            item = item_name[i],
            item_decription = item_descriptions[i],
            quantity = int(quantities[i]),
            item_code = itemcode[i],
            Userlogin = request.user.username
        )
    outlet_stockin.save(using=db)

def saveOutletLog(invoice_date, vendor_name, invoice_id, order_id, check_outlet, Gdescription, item_name, item_descriptions, quantities, itemcode, request, db, i, ware):

    warehouse = None
    if ware is not None:
        warehouse = ware
    outlet_stockin_log = CreateOutletStockInLog(
        datetx = invoice_date,
        supplier = vendor_name,
        invoice_no=invoice_id,
        order_no=order_id,
        outlet = check_outlet,
        warehouse = warehouse,
        description = Gdescription,
        item = item_name[i],
        item_decription = item_descriptions[i],
        quantity = quantities[i],
        item_code = itemcode[i],
        Userlogin = request.user.username
    )
    outlet_stockin_log.save(using=db)