from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import JsonResponse

from Stock.models import *
from customer.models import customer_invoice, customer_table
from Stock.Forms.stockTransferForm import*;
from .Formss import *
from Stock.utils import random_string_generator;
from django.db.models import Q
from datetime import datetime
from main.models import User
from basic_sales_app.functions.Function_Hub import *
from django.contrib.auth.decorators import login_required
from Stock.setCurrentUsers import set_current_user
from django.conf import settings
from itertools import zip_longest
from customer.utils import generate_customer_id

# Create your views here.
def basicSalePoint(request):
    return render(request, 'basic_sales/basic_sales_point.html', {})


@login_required(login_url="/")
def SaleMenu(request):
    DB = get_DB(request)

    casual_customer(DB)

    category = retreiveAllCategory(request)
    customer = retreiveAllCustomer(request)
    item = retreiveAllItem(request)
   
    encountered_categories, category_ID = category_subcategory(request, category)
    get_symbol =  currency_symbol(request)
    vat = request.session.get('autoA_VAT', 'Yes')
    fetch = list(zip(encountered_categories, category_ID))
    randomtoken = random_string_generator()

    context = {
        'customers': customer,
        'get_symbol': get_symbol,
        'VAT': vat,
        'items': item,
        'category': fetch,
        'invoiceID': 'InvoiceID_'+randomtoken,
        'order_ID': 'Order_ID_'+randomtoken,
        'accounts': chart_of_account.objects.using(DB).all()
    }

    if request.method == 'POST':
        makeSales(request, context)
        

    if request.method == 'GET':
        items_data = Get_item_by_CategoryID(request)
        if items_data:
            return JsonResponse({'items': items_data})
        

    profileNotification(DB, context)
    return render(request, 'basic_sales/sales_menu.html', context)


def casual_customer(DB):
    try:
        cus = customer_table.objects.using(DB).get(name="Casual Customer")
    except customer_table.DoesNotExist:
        cus = customer_table.objects.using(DB).create(
            name="Casual Customer",
            phone="1234",
            category="Retail",
            company_name= "Casual Customer",
            email= "casualCustomer@gmail.com",
            customer_code= generate_customer_id()
            )

@login_required(login_url="/")
def SalesHistory(request):
    DB = get_DB(request)
    
    customer_sales_history = customer_invoice.objects.using(DB).all().order_by('-id')
    # distinct_values = customer_invoice.objects.using(DB).values_list('invoiceID', flat=True).distinct().order_by('-id')
    # invoiceid = customer_invoice.objects.using(DB).values_list('invoiceID', flat=True).distinct()
    # getSalesHistory = customer_invoice.objects.using(DB).distinct().exclude(invoiceID__in=invoiceid)
    total_sum = sum(item.amount for item in customer_sales_history)
    page =  getPaginator(customer_sales_history, request)

    currency = currency_symbol(request)
    context = {
        'CSH':page,
        'currency_symbol':currency,
        'total_sum':total_sum,
    }
    profileNotification(DB, context)
    return render(request, 'basic_sales/sales_history.html', context)


@login_required(login_url="/")
def Sales_history_details(request, slug):
    context = CUS_invoice(request, slug, 'invoiceID')
    DB = get_DB(request)
    otherField = customer_invoice.objects.using(DB).filter(Q(invoiceID=slug)).first()
    fieldwithSameID = customer_invoice.objects.using(DB).filter(Q(invoiceID=slug))
    context['InvoiceOnly'] = 'InvoiceOnly'
    if request.method == 'POST':
        if 'MakeChanges' in request.POST:
            amount = request.POST.get('amount');
            amtPaid = request.POST.get('amountPaid');
            try:
                getCusByID = customer_table.objects.using(DB).get(customer_code=otherField.cusID)
            except:
                pass
            
            minusAmountPaid = float(amount) - float(amtPaid)
            for i in fieldwithSameID:
                i.amount_paid = amtPaid
                if minusAmountPaid > 0:
                    i.amount_expected = minusAmountPaid
                i.save(using=DB)

            if minusAmountPaid < 0:
                
                # it means customer isn't owing
                CustomerCurrentBalance = abs(minusAmountPaid)

                getCusByID.Balance = float(getCusByID.Balance) + float(CustomerCurrentBalance);
                getCusByID.save(using=DB)

            else:
                # it means customer is owing
                getCusByID.Balance = float(getCusByID.Balance) + float(-minusAmountPaid);
                getCusByID.save(using=DB)

            context['success_message'] = 'Account Updated';
    

    profileNotification(DB, context)
    return render(request, 'basic_sales/Sales_history_details.html', context)




def get_item_list(get_one_only, allOthers):
    if get_one_only is not None:
        itemName = []
        Item_code = []
        itemName.append(get_one_only.item_name)
        Item_code.append(get_one_only.itemcode)
        for i in allOthers:
            if i.item_name not in itemName and i.generated_code not in Item_code:
                itemName.append(i.item_name)
                Item_code.append(i.generated_code)

        return itemName, Item_code
    else:
        return allOthers




@login_required(login_url="/")
def edit_sales_history(request, pk):
    DB = get_DB(request)
    salesDetailes = customer_invoice.objects.using(DB).get(id=pk)
    GetOtherAmount = customer_invoice.objects.using(DB).exclude(id=pk).filter(invoiceID=salesDetailes.invoiceID)
    getotherFields = customer_invoice.objects.using(DB).filter(invoiceID=salesDetailes.invoiceID)

    form = SalesUpdateForm(request.POST or None, instance=salesDetailes)
    customer = retreiveAllCustomer(request)
    allitem = retreiveAllItem(request)
    itemName, Item_code =  get_item_list(salesDetailes, allitem)
    items =  list(zip(itemName, Item_code))
    Customer_name, Customer_ID =  get_customerName_for_editing(customer, salesDetailes)
    customers = list(zip(Customer_name, Customer_ID))
    TotalInvoice = len(getotherFields)

    context = {
        'update_form':form,
        'salesDetailes':salesDetailes,
        'customers':customers,
        'items':items,
        'TotalAmount':sum(i.amount for i in  getotherFields),
        'TotalInvoice':TotalInvoice,
        'GetOtherInvoices':GetOtherAmount,
    }
    
    if request.method == 'POST':
        if 'UpdateSalesHistory'  in request.POST:
            if form.is_valid():
              
                save_withDB = form.save(commit=False)
                cusID = form.cleaned_data.get('cusID');
                itemcode = form.cleaned_data.get('itemcode');
                qty = form.cleaned_data.get('qty');
                try:
                    getCusByID = customer_table.objects.using(DB).get(customer_code=cusID)
                except:
                    pass

                # UPDATE CUSTOMER DETAILS IF CHANGED
                if cusID is not None: # if it isn't a Casual Customer then update the name of the changed customer
                    for i in getotherFields:
                        i.customer_name = getCusByID.name
                        i.cusID = cusID
                        i.save(using=DB)
                    salesDetailes.customer_name = getCusByID.name
                    salesDetailes.save(using=DB)

                else:
                    for i in getotherFields:
                        i.customer_name = 'Casual Customer'
                        i.cusID = None
                        i.save(using=DB)
                    # salesDetailes.customer_name = 'Casual Customer'
                    
                # update the item name when changed
                getItemByID = Item.objects.using(DB).get(generated_code=itemcode)
                salesDetailes.item_name = getItemByID.item_name

                # update amount when qty changes
                totalAmount = float(qty) * float(getItemByID.selling_price)
                salesDetailes.amount = totalAmount
                salesDetailes.save(using=DB)

                total_amount = sum(i.amount for i in  GetOtherAmount)
                total = float(total_amount) + float(totalAmount)

                # if not a registered customer
                if cusID is None:
                    # if confirmed that casual customer has paid in full(important!), execute the below line of code
                    for i in getotherFields:
                        i.amount_paid = total
                        
                else:
                    # update customer balance when qty changes

                    minusAmountPaid = float(total) - float(salesDetailes.amount_paid)

                    if minusAmountPaid < 0:
                        
                        # it means customer isn't owing
                        CustomerCurrentBalance = abs(minusAmountPaid)

                        getCusByID.Balance = float(getCusByID.Balance) + float(CustomerCurrentBalance);
                        getCusByID.save(using=DB)
                    else:
                        # it means customer is owing
                        getCusByID.Balance = float(getCusByID.Balance) + float(-minusAmountPaid);
                        getCusByID.save(using=DB)

                save_withDB.save(using=DB)
                context['success_message'] = 'Account Updated';
            else:
                context['errors'] = form.errors



        # else:
        #     context['errors'] = form.errors


    profileNotification(DB, context)
    return render(request, 'basic_sales/edit_salesHistory.html', context)



@login_required(login_url="/")
def authAmount(request):
    if request.method == 'GET':
        DB          = get_DB(request)
        pk          = request.GET.get('ID')
        itemCode    = request.GET.get('data')
        qty         = request.GET.get('qty')
        # update amount when qty changes
        # if qty is type.float:
        #     pass
        
        salesDetailes = customer_invoice.objects.using(DB).get(id=pk)
        GetOtherAmount = customer_invoice.objects.using(DB).exclude(id=pk).filter(invoiceID=salesDetailes.invoiceID)
        # getotherFields = customer_invoice.objects.using(DB).filter(invoiceID=salesDetailes.invoiceID)
        getItemByID = Item.objects.using(DB).get(generated_code=itemCode)

        totalAmount = float(qty) * float(getItemByID.selling_price)
        
        total_amount = sum(i.amount for i in  GetOtherAmount)

        total = float(total_amount) + float(totalAmount)
        minusAmountPaid = float(total) - float(salesDetailes.amount_paid)

        if minusAmountPaid < 0:

            # it means customer isn't owing
            CustomerCurrentBalance = abs(minusAmountPaid)
            return JsonResponse({'CustomerCurrentBalance': CustomerCurrentBalance,})

        else:
            # it means customer is owing
            Balance = minusAmountPaid;
            return JsonResponse({'Balance': Balance, 'total':total})





@login_required(login_url="/")
def Cus_Sales_history_details(request, slug):
    context = CUS_invoice(request, slug, 'cusID')
    DB = get_DB(request)
    profileNotification(DB, context)
    return render(request, 'basic_sales/Sales_history_details.html', context)


@login_required(login_url="/")
def CancelSales(request):
    DB = get_DB(request)
    customer_sales_history = customer_invoice.objects.using(DB).exclude(invoice_state='Cancelled').order_by('-id')
    page = getPaginator(customer_sales_history, request)
    currency= currency_symbol(request)
    context = {
        'currency':currency,
        'page':page,
    }
    profileNotification(DB, context)
    return render(request, 'basic_sales/cancel_sales.html', context)



@login_required(login_url="/Login")
def AddItemForSales(request):
    DB = get_DB(request)

    form = ItemForm(request.POST, request.FILES)
    item = retreiveAllItem(request);
    getcate =retreiveAllCategory(request);
    encountered_categories, category_ID = category_subcategory(request, getcate)
    fetch = list(zip(encountered_categories, category_ID))
    page = getPaginator(item, request)
    currency= currency_symbol(request)
    set_current_user(request.user)
    context = {
        'currency': currency,
        'form': form,
        'item': page,
        'getcate': fetch,
        'errors': form.errors,
    }
    if request.method == 'POST':
        id = request.POST.get('category')
        if form.is_valid():
            save_withDB = form.save(commit=False);
            save_withDB.category_id = id
            save_withDB.save(using=DB)

            item_id = save_withDB.id 
            items = Item.objects.using(DB).get(id=item_id) 
            notify = SetItemNotification(item=items, Userlogin=request.user.username)
            notify.save(using=DB)
            if save_withDB:
                context['success_message'] = 'Item Created Successfully';
        else:
            context['formerror'] = form

        get_color = request.POST.getlist('color[]')
        generated_code = request.POST.get('generated_code')
        if get_color != []:
           InsertColors(request, get_color, generated_code)
        else:
            pass

   
    sub_categories = getNewItemSubcat(request)
    if sub_categories:
        return JsonResponse({'data': sub_categories})
    
    profileNotification(DB, context)
    return render(request, 'basic_sales/AddItem.html', context)




@login_required(login_url="/Login")
def update_item(request, pk):
    item = retreiveOneItem(request, pk);
    form = ItemUpdateForm(request.POST, request.FILES or None, instance=item)
    getcate =retreiveAllCategory(request);
    category_name, category_ID = get_item_for_editing(request, getcate, item)
    fetch = list(zip(category_name, category_ID))
    context = {
        'form': form,
        'item': item,
        'getcate': fetch,
        'getSubcate': item.sub_category,
    }

    get_all_color = get_all_colors(request)
    if get_all_color:
        context['all_colors'] = get_all_color;

    get_colors = get_selected_colors(request, item)
    if get_colors:
        code = get_colors.color_code
        split_color = code.split(',')
        context['get_colors'] = split_color;
   
    oldImagepath = None
    try:
        oldImagepath = item.image.url
    except:
        pass
    DB = get_DB(request)

    if request.method == 'POST':
        
        if 'update_item' in request.POST:
            id = request.POST.get('category')
            if form.is_valid():
                getImg = form.cleaned_data.get('image')
                if getImg is not None:
                    if oldImagepath is not None:
                        file_system_path = os.path.join(settings.MEDIA_ROOT, oldImagepath[len(settings.MEDIA_URL):])
                        if os.path.exists(file_system_path):
                            os.remove(file_system_path)
                        # else:

                save_withDB = form.save(commit=False);
                save_withDB.category_id = id
                save_withDB.save(using=DB)

                context['success_message'] = 'Item Updated Successfully';
            else:
                pass

        if 'add_auxilaries' in request.POST:
            item_Update_for_colors(request, context)
    profileNotification(DB, context)
    return render(request, 'basic_sales/update_item.html', context)


@login_required(login_url="/Login")
def stockIn(request):
    DB = get_DB(request)
    form = W_W_Form(request.POST or None)
    listitems = Item.objects.using(DB).all()
    randomtoken = random_string_generator()   
    context = {
        'listitems' : listitems,
        'form' : form,
        'tokenID': 'Token_'+randomtoken,
    }
    getid = request.GET.get('data')
    if getid is not None:
        return getStocktransferTableDate(request, 'generated_code', getid)
    
    if request.method == 'POST':
        add_stockin(request, context)
    profileNotification(DB, context)
    return render(request, 'basic_sales/stockin.html', context)



# ********************************************************************************************************

def getitem(val, db):
   getval = Item.objects.using(db).get(generated_code=val)
   return getval



def get_data_from_main_tables(request, table, store, db):
   getitemcode = request.GET.get('Itemcode')
   getitemname = request.GET.get('searchItem')
   getstore     = request.GET.get('store')
   fromdate    = request.GET.get('fromdate')
   todate      = request.GET.get('todate')
#    INSTOCKLEVEL = request.session.get('level', 'NO')
   getstock2 = False
   from_date = None
   to_date = None
   if fromdate and todate is not None:
      from_date, to_date =getdate(fromdate, todate)

   if getitemcode or getitemname or getstore or fromdate and todate is not None:
      getstock2 = table.objects.using(db).filter(Q(datetx__range=(from_date, to_date)) | Q(item_code=getitemcode) | Q(item=getitemname) | Q(**{store:getstore}))#**{store:storeData}
   return getstock2


def stocklevelfinalresult(stockLevel, item, data, db):

   # WHEN INSTANT STOCKLEVEL IS SET TO YES
#    if INSTOCKLEVEL == 'YES':
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

def get_grand_total_from_stock_log(item, table1, table2, storeData, db):
    # WHEN INSTANT STOCKLEVEL IS SET TO NO(meaning we are getting stocklevel from the stockin_logs and not stockin(this could be the stockin or outletstockin tables or models)) RUN THE BELOW CODE

    # fetching to get all the times the quantity field was incremented
    allincrements = table1.objects.using(db).filter(Q(outlet=storeData) & Q(item_code=item.item_code))

    #  fetching to get all the times the quantity field was decremented
    decrements_withinTable = table1.objects.using(db).filter(Q(warehouse=storeData) & Q(item_code=item.item_code))
    decrements_outsideTable = table2.objects.using(db).filter(Q(warehouse=storeData) & Q(item_code=item.item_code))

    
    total_increment = sum(item.quantity for item in allincrements)
    total_decrement1 = sum(item.quantity for item in decrements_withinTable)
    total_decrement2 = sum(item.quantity for item in decrements_outsideTable)
    total_decrement = total_decrement1 + total_decrement2
    grandtotal = total_increment - total_decrement

    return grandtotal

def getOutletStockLevel(request, db):
   result = get_data_from_main_tables(request, CreateOutletStockIn, 'outlet', db)
   if result :
      total_quantity = sum(item.quantity for item in result)
      stockLevel = []
      for item in result:
        #  grandtotal = get_grand_total_from_stock_log(item, CreateOutletStockInLog, CreateStockInLog,  item.outlet, db)
         stockLevels = stocklevelfinalresult(stockLevel, item, item.outlet, db)
      return stockLevels, total_quantity


@login_required(login_url="/Login")
def OutletStockLevel(request):
    db = request.user.company_id.db_name
    getstock = CreateOutletStockIn.objects.using(db).all()
    total_quantity = sum(item.quantity for item in getstock)
#    total = [get_grand_total_from_stock_log(item, CreateOutletStockInLog, CreateStockInLog,  item.outlet, db) for item in getstock]
#    level = request.session.get('level', 'NO')
#    listedloop = list(zip_longest(getstock, total))
    shop = sales_outlet.objects.using(db).all()
    context = {
      'stock' : getstock,
      'totalqty' : total_quantity,
    #   'level' : level,
      'shop' : shop,
    }

    stock_level_data= getOutletStockLevel(request, db)
    if stock_level_data is not None:
      stockLevel, total_quant = stock_level_data
      return JsonResponse({'data': stockLevel, 'totalqty': total_quant})
   
    profileNotification(db, context)

    return render(request, 'basic_sales/OutletStockLevel.html', context)

# ********************************************************************************************************




@login_required(login_url="/Login")
def checkout_summary(request):
    get_symbol =currency_symbol(request)
    context = {
        'get_symbol' : get_symbol,
    }
    DB = get_DB(request)
    profileNotification(DB, context)
    return render(request, 'basic_sales/checkout_summary.html', context)


@login_required(login_url="/Login")
def stockin_history(request):
    DB = get_DB(request)
   
    get_history = CreateOutletStockInLog.objects.using(DB).all().order_by('-id')
    page = getPaginator(get_history, request)
    currency = currency_symbol(request)
    if request.method == 'GET':
        result = get_stockin_history(request)
        if result:
            return JsonResponse({'data': result})
        
    context = {
        # 'get_history':get_history,
        'page': page,
        'currency': currency,
    }
    profileNotification(DB, context)
    return render(request, 'basic_sales/stockin_history.html', context)



@login_required(login_url="/Login")
def view_item(request, pk):
    DB = get_DB(request)
    view_item = retreiveOneItem(request, pk);
    currency = currency_symbol(request)
    context = {
        'item': view_item,
        'currency': currency,
    }
    try:
        other_item = Item.objects.using(DB).exclude(Q(id=pk)).filter(Q(category_id=view_item.category_id));
        context['other_item'] = other_item;
    except Item.DoesNotExist:
       context['other_item'] = None;

    get_colors = get_selected_colors(request, view_item)
    if get_colors:
        code = get_colors.color_code
        split_color = code.split(',')
        context['get_colors'] = split_color;
    profileNotification(DB, context)
    return render(request, 'basic_sales/view_item.html', context)

@login_required(login_url="/Login")
def add_user(request):
    DB = get_DB(request)
    form = RegisterForm(request.POST or None)
    randomtoken = random_string_generator() 
    Users = User.objects.using(DB).all()

    context = {
        'user_form': form,
        'users': Users,
        'submit': False,
        'token': 'Token_'+randomtoken,
    }

    if request.method == 'POST':
        AddUserFunction(request, context, form)
    profileNotification(DB, context)
    return render(request, 'basic_sales/add_user.html', context)

@login_required(login_url="/Login")
def autovat(request):
    activate = request.POST.get('activate',)
    redirectTo = request.POST.get('redirectTo')
    if 'activateVAt' in request.POST:
        AAV = request.session['autoA_VAT'] = activate
        if AAV:
            return redirect(redirectTo)
    context={}
    DB = get_DB(request)
    profileNotification(DB, context)
    return render(request, 'basic_sales/VATmodal.html', context)


@login_required(login_url="/Login")
def add_profile(request):
    DB = get_DB(request)
    profile_form = ProfileSetupForm(request.POST, request.FILES or None)
    profiledata = CreateProfile.objects.using(DB).all()
    randomtoken = random_string_generator() 
    all_currencies = get_all_currencies()
    get_one_only = profiledata.first()
    get_currency = get_currency_by_name(get_one_only, all_currencies)
    context = {
        'form': profile_form,
        'submit': False,
        'token': 'Token_'+randomtoken,
        'all_currencies': get_currency,
        'profile':get_one_only
    }
    if request.method == 'POST':
        if 'addprofile' in request.POST:
            if profile_form.is_valid():
                update_edit_profile(request, profile_form, profiledata, context)
            else:
                context['formerror'] = profile_form
                context["error_message"] =  'Form is not valid' 
      
    if profiledata.count() > 0:
        context['submit'] = 'Update Profile'
    else:
        context['submit']  = 'Create Profile'

    profileNotification(DB, context)
    return render(request, 'basic_sales/add_profile.html', context)



@login_required(login_url="/Login")
def add_customer(request):
    DB = get_DB(request)

    form = CustomerForm(request.POST, None)
    customer = retreiveAllCustomer(request)
    randomtoken = random_string_generator()
    page = getPaginator(customer, request)
    context = {
        'customers':page,
        'form':form,
        'customer_code':'CUS_'+randomtoken,
        'token_id':'Token_'+randomtoken,
    }
    
    if request.method == 'POST':
        if form.is_valid():
            save_withDB = form.save(commit=False)
            save_withDB.save(using=DB)
            if form:
                context['success_message'] = 'Account Created';

        else:
            context['errors'] = form.errors
    profileNotification(DB, context)
    return render(request, 'basic_sales/add_customer.html', context)

@login_required(login_url="/Login")
def edit_customer(request, pk):
    DB = get_DB(request)
    customer = customer_table.objects.using(DB).get(id=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    context = {
        'update_form':form,
        'customer':customer,
    }
    
    if request.method == 'POST':
        DB = get_DB(request)
        if form.is_valid():
            save_withDB = form.save(commit=False)
            update_customer_acct =  save_withDB.save(using=DB)
            context['success_message'] = 'Account Updated';
        else:
            context['errors'] = form.errors
    profileNotification(DB, context)
    return render(request, 'basic_sales/edit_customer.html', context)


@login_required(login_url="/Login")
def customer_history(request):
    DB = get_DB(request)
    customer_sales_history = customer_invoice.objects.using(DB).exclude(Q(cusID__isnull=True) | Q(customer_name='Casual Customer')).order_by('-id')
    page = getPaginator(customer_sales_history, request)
    total_sum = sum(item.amount for item in customer_sales_history)
    currency = currency_symbol(request)
    context = {
        'CSH':page,
        'currency':currency,
        'total_sum':total_sum,
        
    }
    profileNotification(DB, context)
    return render(request, 'basic_sales/customer_history.html', context)




@login_required(login_url="/Login")
def account_recievable(request):
    DB = get_DB(request)
    customer_account_recievable = customer_table.objects.using(DB).filter(Q(Balance__icontains='-')).order_by('-id');
    totalBalance = sum(i.Balance for i in customer_account_recievable)
    page = getPaginator(customer_account_recievable, request)
    currency = currency_symbol(request)
    context = {
        'page': page,
        'currency': currency,
        'totalBalance': totalBalance,
    }

    if request.method == 'GET':
        try:
            id =  request.GET.get('id')
            updatebalance = customer_table.objects.using(DB).get(customer_code=id)
            if updatebalance:
                return JsonResponse({'cusID': updatebalance.customer_code, 'balance':updatebalance.Balance})
        except:
            pass

    if request.method == 'POST':
        if 'credit_account' in request.POST:
            Credit_acct(request, context)
    profileNotification(DB, context)
    return render(request, 'basic_sales/account_recievable.html', context)


@login_required(login_url="/Login")
def ItemCategory(request):
    form = NewCategoryForm(request.POST, request.FILES)
    getcate =retreiveAllCategory(request).order_by('-id');
    randomtoken = random_string_generator()

    context = {
       'form' : form,
       'getcategory': getcate,
       'token_id':'Token_'+randomtoken,
    }

    if request.method == 'POST':
        if form.is_valid():
            add_category(request, form, context)
        else:
            context['formerror'] = form;
            context['error_message'] = 'Request Failed';
    
    
    
    categoryID = request.GET.get('categoryID');
    if categoryID is not None:
        category_data = get_category_detail(request, categoryID)
        if category_data:
            return JsonResponse({'category': category_data})
    DB = get_DB(request)
    profileNotification(DB, context)
    return render(request, 'basic_sales/ItemCategory.html', context)

@login_required(login_url="/Login")
def theBase(request):
    countProfile = CreateProfile.objects.using(db).all()
    lenght = len(countProfile)
    context = { }
    if lenght > 0:
        count =  1
        context['count']= count
        return JsonResponse({'result': True})

    else:
        pass



@login_required(login_url="/Login")
def edit_category(request, pk):
    DB = get_DB(request)
    form = NewCategoryForm(request.POST, request.FILES)
    getcate = Category.objects.using(DB).get(id=pk)
    context = {
        'getcate':getcate,
        'form':form,
    }
    if request.method == 'POST':
        if form.is_valid():
            Update_category(request, form, context)
        else:
            context['error_message'] = 'Request Failed';
    profileNotification(DB, context)
    return render(request, 'basic_sales/edit_category.html', context);
