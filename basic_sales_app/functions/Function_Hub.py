from django.shortcuts import render, redirect, get_object_or_404;
from django.contrib import messages;
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse, JsonResponse,Http404;

from Stock.models import *
from customer.models import customer_invoice, customer_table
from settings.models import Warehouse
from Stock.Forms.stockTransferForm import*;
from basic_sales_app.Formss import*;
from Stock.utils import random_string_generator;

from django.db.models import Q
from datetime import datetime, date, timezone
from main.models import User
from forex_python.converter import CurrencyCodes
import os
from django.conf import settings
from settings.models import *

from account.models import chart_of_account
from customer.functions.generalFunction import DebitReceivable, CreditReceivable, CreateLog
from customer.functions.newsalesfunc import create_add_vat
from decimal import Decimal

# GET ALL CUSTOMER USING OUR QS STATEMENT
def retreiveAllCustomer(request):
    DB = get_DB(request)
    customer = customer_table.objects.using(DB).all()
    return customer;

#GET COMPANY DB 
def get_DB(request):
    DB = request.user.company_id.db_name
    return DB


# GET ALL ITEM USING OUR QS STATEMENT
def retreiveAllItem(request):
    DB = get_DB(request)
    item = Item.objects.using(DB).all().order_by('-id');
    return item;



# GET ONE ITEM USING OUR QS STATEMENT
def retreiveOneItem(request, pk):
    DB = get_DB(request)

    item = Item.objects.using(DB).get(id=pk)
    return item;



# GET ALL CATEGORY USING OUR QS STATEMENT
def retreiveAllCategory(request):
    DB = get_DB(request)
    category = Category.objects.using(DB).all()
    return category;



# FUNCITON USED BY currency_symbol() FOR CURRENCY SYMBOLS
def get_currency_symbol(currency):
    currency_codes = CurrencyCodes()
    if currency:
        get_symbol = currency_codes.get_symbol(currency)
        return get_symbol;


# GET CURRENCY SYMBOL FOR SALES CURRENCY (ALL PAGES)
def currency_symbol(request):
    DB = get_DB(request)
    try:
        profile = CreateProfile.objects.using(DB).all().first()
        
        get_symbol = get_currency_symbol(profile.currency)
        return get_symbol
    except:
        pass

# PAGINATION FUNCION USED BY getPaginator(qs, request)
def paginator_func(paginator, request):
    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
  
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    return page


# PAGINATION (ALL PAGES)
def getPaginator(qs, request):
    paginator = Paginator(qs, 20)
    page = paginator_func(paginator, request)
    return page



# FORMATTED DATE FUNCTION USED BY MOST FUNCTIONS
def getdate(fromdate, todate):
    if fromdate is not None and todate is not None:
        try:
            from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
            to_date = datetime.strptime(todate, '%Y-%m-%d').date()
            return from_date, to_date
        except ValueError:
            # Handle the case where the date string is not in the expected format
            return None, None
        

# PREVENTS ITME FROM APPREARING TWICE USED BY MOST FUNCTIONS
def Encountered(any,item):
   encountered_any = set()
   for i in any:
      # val = i.item
      val = getattr(i, item, None)
      if val not in encountered_any:
         encountered_any.add(val)
   return encountered_any

# GET CUSTOMER DETAILS FOR EDIT SALES HISTORY USER BY edit_sales_history(request, pk) IN EDIT SALES PAGE
def get_customerName_for_editing(getcate, item):
    Customer_name = []
    Customer_ID = []
    if item.customer_name == 'Casual Customer':
        Customer_ID.append('')
        Customer_name.append('Casual Customer')
    else:
        Customer_ID.append(item.cusID)
        Customer_name.append(item.customer_name)

    for i in getcate:
        if i.customer_code not in Customer_ID and i.name not in Customer_name:
            Customer_ID.append(i.customer_code)
            Customer_name.append(i.name)
    return Customer_name, Customer_ID;

# INSERT COLORS INTO COLOR TABLE
def InsertColors(request, get_color, generated_code):
    cleaned_data = [color.strip('[]') for color in get_color]
    combined_colors = ','.join(cleaned_data)
    DB = get_DB(request)
    create_color = ItemColor.objects.using(DB).create(item_code=generated_code, color_code=combined_colors)
    if create_color:
        pass


# GET ALL COLORS FROM COLOR TABLE A DISPLAY THEM ONCE
def get_all_colors(request):
    DB = get_DB(request)
    try:
        get_colors = ItemColor.objects.using(DB).all()
        colors = []
        colors_set = set()
        # Fetch all color codes and split them if they contain commas
        for color in get_colors:
            codes = color.color_code.split(',')
            colors_set.update(codes) 
        colors = list(colors_set)

        return colors;

    except ItemColor.DoesNotExist:
        return None;


# GET COLOR DATAILS (VIEW AND UPDATE ITEM PAGE)
def get_selected_colors(request, item):
    DB = get_DB(request)
    try:
        get_colors = ItemColor.objects.using(DB).get(item_code=item.generated_code)
        return get_colors;
    except ItemColor.DoesNotExist:
        return None;


# GET ALL CURRENCISE
def get_all_currencies():
    currency_code_list = ['NGN', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NZD', 'KRW', 'SGD', 'NOK', 'MXN', 'INR', 'RUB', 'ZAR', 'BRL', 'TRY', 'HKD', 'THB', 'IDR', 'TWD', 'DKK', 'PLN', 'PHP', 'HUF', 'CZK', 'ILS', 'CLP', 'AED', 'COP', 'SAR', 'MYR', 'RON', 'VND', 'ARS',  'EGP', 'PKR', 'UAH', 'KES', 'BDT', 'IQD', 'MAD', 'KWD', 'HNL', 'QAR', 'NPR', 'NAD', 'CRC', 'UYU', 'PYG', 'OMR', 'BHD', 'BOB', 'DOP', 'LBP', 'JMD', 'GYD', 'AFN', 'SZL', 'TND', 'YER', 'GHS', 'MZN', 'UZS', 'KHR', 'LRD', 'XAF', 'XCD', 'HTG', 'BZD', 'MVR', 'BND', 'MWK', 'SBD', 'GNF', 'XOF', 'LAK', 'XPF', 'WST', 'DJF', 'MNT', 'MOP', 'KGS', 'FJD', 'TOP', 'GMD', 'SLL', 'TJS', 'BWP', 'SCR', 'STD', 'LSL', 'AZN', 'SVC', 'KHR', 'RWF', 'MKD', 'VUV', 'DZD', 'SRD', 'ANG', 'MMK', 'BAM', 'GIP', 'TMT', 'FKP', 'GGP', 'IMP', 'JEP', 'SHP', 'TVD', 'ZMW', 'BYN', 'XAG', 'XAU', 'XPT', 'XPD', 'BIF']
    return currency_code_list


# LOOPED DATA USED BY MOST FUNCTIONS
def loop_data(all_left):
    invoice_acct = [({
        'cusID':sale.cusID,
        'customer_name':sale.customer_name,
        'item_name':sale.item_name,
        'unit_p':sale.unit_p,
        'qty':sale.qty,
        'amount':sale.amount,
        'amount_paid':sale.amount_paid,
        'payment_method':sale.payment_method,
        'invoiceID':sale.invoiceID,
        'id':sale.id,

        })
            for sale in all_left
        ]
    return invoice_acct;


# LOOPED ACCT RECEIVABLE DATA USED BY get_account_receiables(request) 
def acct_receivables_loop_data(all_left):
    acct_receiables = [({
        'customer_code':sale.customer_code,
        'name':sale.name,
        'Balance':sale.Balance,
        'phone':sale.phone,
        'address':sale.address,
        })
            for sale in all_left
        ]
    return acct_receiables;



# AJAX FUNCTION TO GET ITEM DATA ON $(DUCOMENT).READY(FUNCTION(){}) (SALESMENU PAGE)
def fetch_items_by_default(request):
    DB = get_DB(request)
    items = list(Item.objects.using(DB).values().order_by('-id'))
    if items:
        return JsonResponse({'items': items})
    else:
        pass


# FUNCTOIN USED BY SCANNED_CODE FUNCTION &
def getStocktransferTableDate(request, generated_code, getid):   
    DB = get_DB(request)
    try:
        getitem = Item.objects.using(DB).get(Q(**{generated_code:getid}))
        if getitem:
            return JsonResponse({'des': getitem.description, 'qty':getitem.size, 'image':str(getitem.image), 'item':getitem.item_name, 'price':getitem.selling_price, 'code':getitem.generated_code, 'wholesale_price':getitem.wholesale_price, 'id':getitem.id})
    except Item.DoesNotExist:
        pass



# AJAX FUNCTION TO GET ITEM DATA WHEN SEARCHED IN AN INPUT FIELD (SALESMENU PAGE)
def itemSearch(request):
    search = request.GET.get('searchItem')
    DB = get_DB(request)
    ifgood = False;
    try:
        if  search: 
            items = list(Item.objects.using(DB).filter(Q(item_name__icontains=search) | Q(generated_code__icontains=search)).values().order_by('-id'))
            ifgood = True;
        
        else:
            items = list(Item.objects.using(DB).values().order_by('-id'))
            ifgood = True;

        if ifgood:
            return JsonResponse({'items':items})
        
    except Item.DoesNotExist:
        pass



# BARBODER SCAN FUNCTION(TO RETREIVE DATA TO CART WHEN SCANNED) (SALESMENU PAGE)
def Scanned_code(request):
    searchItem = request.GET.get('searchItem')
    if searchItem is not None:
        # context['loader'] = 'Yes'
        return getStocktransferTableDate(request, 'generated_code', searchItem)

# FUNCTOIN USED BY SCANNED_CODE FUNCTION &
# def getStocktransferTableDate(request, generated_code, getid):   
#     try:
#         getitem = Item.objects.using(DB).get(Q(**{generated_code:getid}))
#         if getitem:
#             return JsonResponse({'des': getitem.description, 'qty':getitem.size, 'image':str(getitem.image), 'item':getitem.item_name, 'price':getitem.selling_price, 'code':getitem.generated_code, 'wholesale_price':getitem.wholesale_price, 'id':getitem.id})
#     except Item.DoesNotExist:
#         pass
        # return JsonResponse({'None':None})



# SALES FUNCTION (SALESMENU PAGE)
def makeSales(request, context):
    customer_name = request.POST.get('customer_name')
    cusID = request.POST.get('cusID')
    payment_method = request.POST.get('payment_method')
    invoiceID = request.POST.get('invoiceID')
    order_ID = request.POST.get('order_ID')
    amount_paid = request.POST.get('amount_paid')
    account = request.POST.get('t_account')
    transfer = request.POST.get('transfer_amount')
    cash = request.POST.get('cash_amount')
    vat = request.POST.get('vat_value')
    generated_code = request.POST.getlist('generated_code[]')
    item_name = request.POST.getlist('item_name[]')
    quantity = request.POST.getlist('quantity[]')
    selling_price = request.POST.getlist('selling_price[]')
    amount = request.POST.getlist('amount[]')
    
    invoice_date_ = date.today() 
    current_time = datetime.now().time()
    invoice_date = datetime.combine(invoice_date_, current_time)

    DB = get_DB(request)
    item_length = len(generated_code)
    for_count_down = len(generated_code)

    # vat = float(amount_paid) * 0.075
    total = float(amount_paid) 

    amount_paid = format(total, ".2f")
    amount_expected = format(total, ".2f")
 

    

    def purchase(generated_code, itemcode):
        total = 0.00
        price = Item.objects.using(DB).get(generated_code=itemcode).purchase_price
       
        for i in generated_code:
            purchaseP = Item.objects.using(DB).get(generated_code=i).purchase_price
            total += float(purchaseP)

        return total, float(price)

   

    i = 0
    ifgood = False;
    while i < item_length:
        total_purchase, purchase_p = purchase(generated_code, generated_code[i])
       
        to_be_stored = {
            'invoice_date': invoice_date,
            'due_date': invoice_date,
            'cusID':cusID, 
            'customer_name':customer_name, 
            'payment_method':payment_method, 
            'amount':amount[i],
            'invoiceID':invoiceID, 
            'order_ID':order_ID,
            'itemcode':generated_code[i], 
            'item_name': item_name[i], 
            'qty': quantity[i], 
            'unit_p': selling_price[i], 
            'amount_paid': amount_paid, 
            'amount_expected': amount_expected,
            'purchaseP': purchase_p,
            'total_purchaseP': total_purchase,
            'outlet': request.user.outlet, 
            'Userlogin':request.user,

        }
        
        sale = customer_invoice.objects.using(DB).create(**to_be_stored)
        try:
            outlet = request.user.outlet
            update_outlet = CreateOutletStockIn.objects.using(DB).get(outlet=outlet, item_code=generated_code[i])

            outletQTY = update_outlet.quantity
            newQty = float(outletQTY) - float(quantity[i])
            update_outlet.quantity = newQty
            # update_outlet.save(using=DB)
        except CreateOutletStockIn.DoesNotExist:
            pass
        
        for_count_down -= 1
        i = i+1
    if for_count_down == 0:
        if sale:
            # expected = -float(amount_expected)
            if cusID:
                cus = customer_table.objects.using(DB).get(customer_code=cusID)
                getBal = cus.Balance
                # setbal = float(getBal) + expected
                # cus.Balance = setbal
                cus.invoice += 1  
                cus.save(using=DB)
                DebitReceivable(request, DB, cus, invoice_date, "POS Sales", payment_method, account, amount_paid)
                
                # vat_fmt = format(vat, ".2f")
                create_add_vat(DB, invoiceID, vat)
            if account:
                if payment_method == "Transfer":
                    account = chart_of_account.objects.using(DB).get(account_id=account)
                    CreditReceivable(request, DB, cus, invoice_date, "POS Sales", payment_method, account.account_id, amount_paid)
                    CreateLog(DB, account, amount_paid) 
                else:
                    transfer_account = chart_of_account.objects.using(DB).get(account_id=account)
                    CreditReceivable(request, DB, cus, invoice_date, "POS Sales", "Transfer", account ,transfer)
                    CreateLog(DB, transfer_account, transfer)
                    
                    cash_account = chart_of_account.objects.using(DB).get(account_bankname="Sales account")
                    CreditReceivable(request, DB, cus, invoice_date, "POS Sales", "Cash", account, cash)
                    CreateLog(DB, cash_account, cash)
            else:
                if payment_method != "Cheque":
                   account = chart_of_account.objects.using(DB).get(account_bankname="Sales account")
                   CreditReceivable(request, DB, cus, invoice_date, "POS Sales", payment_method, account.account_id, amount_paid)
                else:
                    account = chart_of_account.objects.using(DB).get(account_bankname="Account Receivable")
                CreateLog(DB, account, amount_paid)   

            context['success_message'] = 'Request successfully';
            return context['success_message'];
        else:
            context['error_message'] = 'Request Failed';
            return context['error_message']


# GET ITEM BY CATEGORY FROM THE CATEGORY SEARCH (SALESMENU PAGE)
def Get_item_by_CategoryID(request):
    DB = get_DB(request)
    category_id = request.GET.get('category_id')
    items = Item.objects.using(DB).filter(category_id=category_id).order_by('-id')
    if items:
        items_data = [{'id': item.id, 'item_name': item.item_name, 'generated_code': item.generated_code, 'selling_price': item.selling_price, 'image': str(item.image)} for item in items]
        return items_data
    

# GET ALL ITEM (SALESMENU PAGE)

def fetch_all_items(request):
    DB = get_DB(request)
    items = Item.objects.using(DB).all().order_by('-id')

    items_data = [{'id': item.id, 'item_name': item.item_name, 'generated_code': item.generated_code, 'selling_price': item.selling_price, 'image': str(item.image)} for item in items]

    return JsonResponse({'items': items_data})


# GET CUSTOMER & INVOICE DETAILS 
def CUS_invoice(request, slug, invoiceID):
    DB = get_DB(request)
    customer_sales_history = customer_invoice.objects.using(DB).filter(Q(**{invoiceID:slug})).order_by('-id')
    customer = None
    getcusID = None
    try:
        customer = customer_table.objects.using(DB).get(customer_code=slug)
    except customer_table.DoesNotExist:
        try:
            getcusID = customer_invoice.objects.using(DB).filter(invoiceID=slug).first()
            customer = customer_table.objects.using(DB).get(customer_code=getcusID.cusID)

        except:
            pass
    except:
        pass

    TotalInvoice = len(customer_sales_history)
    currency =  currency_symbol(request)
    context = {
        'CSH':customer_sales_history,
        'customer':customer,
        'currency':currency,
        'TotalInvoice':TotalInvoice,
        'TotalAmount':sum(i.amount for i in  customer_sales_history),
        'otherField':getcusID,
    }
    return context



# FORLOOP SALES DATA USED BY UpdateCancelSales(request) (CANCEL SALES PAGE)
def loopfor_cancelsales(page):
    cancel_sale = [({
        'customer_name':cancel.customer_name,
        'item_name':cancel.item_name,
        'unit_p':cancel.unit_p,
        'qty':cancel.qty,
        'amount':cancel.amount,
        'amount_paid':cancel.amount_paid,
        'payment_method':cancel.payment_method,
        'id':cancel.id,
        })
            for cancel in page.object_list]
    return cancel_sale


# CANCEL SALES FUNCTION (CANCEL SALES PAGE)
def UpdateCancelSales(request):
    id = request.GET.get('id')
    DB = get_DB(request)
    undateCancelSales = customer_invoice.objects.using(DB).get(id=id)
    undateCancelSales.invoice_state = 'Cancelled'
    undateCancelSales.save(using=DB)

    if undateCancelSales:
        customer_sales_history = customer_invoice.objects.using(DB).exclude(invoice_state='Cancelled').order_by('-id')
        page = getPaginator(customer_sales_history, request)

        cancel_sale = loopfor_cancelsales(page)
        return JsonResponse({'data': cancel_sale})


# FUNCTION FOR SEARCH SALES DATA (CANCEL SALES PAGE)
def Search_for_sales(request):
    fromdate = request.GET.get('fromdate')
    todate = request.GET.get('todate')
    search = request.GET.get('search')
    DB = get_DB(request)
    ifgood = False;
    try:
        if  fromdate or todate:
            M_D, T_D = getdate(fromdate, todate)
            get_Sales_history =  customer_invoice.objects.using(DB).exclude(invoice_state='Cancelled').order_by('-id').filter(Q(invoice_date__range=(M_D, T_D))).order_by('-id')
            ifgood = True;
        else:
            get_Sales_history =  customer_invoice.objects.using(DB).exclude(invoice_state='Cancelled').order_by('-id')
            ifgood = True;

        if  search:
            get_Sales_history = customer_invoice.objects.using(DB).exclude(invoice_state='Cancelled').filter(Q(invoiceID__icontains=search) | Q(customer_name__icontains=search) | Q(itemcode__icontains=search) | Q(item_name__icontains=search)).order_by('-id');
            ifgood = True;
        
        else:
            get_Sales_history =  customer_invoice.objects.using(DB).exclude(invoice_state='Cancelled').order_by('-id')
            ifgood = True;

        if ifgood:
            page = getPaginator(get_Sales_history, request)
            sales_data = loopfor_cancelsales(page)
            return JsonResponse({'data':sales_data})
        
    except customer_invoice.DoesNotExist:
        pass


# GET SUB-CATEGORY USED BY AddItemForSales(request) & SaleMenu(request)
def category_subcategory(request, getcate):
    encountered_categories = Encountered(getcate,'category_name');
    DB = get_DB(request)
    category_ID = []
    for id in encountered_categories:
        getsubcate = Category.objects.using(DB).filter(category_name=id).first();
        if getsubcate.id not in category_ID:
            category_ID.append(getsubcate.id)
    return encountered_categories, category_ID;


# CATEGORY AND CATEGORYID FOR EDITING (UPDATE ITEM PAGE)
def get_item_for_editing(request, getcate, item):
    encountered_categories = Encountered(getcate,'category_name');
    DB = get_DB(request)

    category_name = []
    category_ID = []
    if item.category:
        getfirstsubcate = Category.objects.using(DB).get(id=item.category_id);
        category_ID.append(item.category_id)
        category_name.append(getfirstsubcate.category_name)

    for i in encountered_categories:
        getsubcate = Category.objects.using(DB).filter(category_name=i).first();
        if getsubcate.id not in category_ID and i not in category_name:
            category_ID.append(getsubcate.id)
            category_name.append(i)
    return category_name, category_ID;





# **************************** ITEM COLOR UPDATE FUNCTION USRED BY update_item(request, pk) (ITEM UPDATE PAGE) *****************************


def add_new_color(request, get_color, generated_code, context):
    DB = get_DB(request)
    cleaned_data = [color.strip('[]') for color in get_color]
    combined_colors = ','.join(cleaned_data)
    try:
        get_color_data = ItemColor.objects.using(DB).get(item_code=generated_code)
        if get_color_data:
            get_color_data.color_code=combined_colors
            get_color_data.save(using=DB)

            context['success_message'] = 'Item Updated Successfully';
    except ItemColor.DoesNotExist:
        create_color = ItemColor.objects.using(DB).create(item_code=generated_code, color_code=combined_colors)
        if create_color:
            context['success_message'] = 'Item Updated Successfully';


def update_color_func(request, update_color, generated_code, context):
    DB = get_DB(request)
    cleaned_data = [color.strip('[]') for color in update_color]
    combined_colors = ','.join(cleaned_data)
    try:
        get_color_data = ItemColor.objects.using(DB).get(item_code=generated_code)
        if get_color_data:
            updated_color_str = get_color_data.color_code + ',' + combined_colors
            get_color_data.color_code=updated_color_str
            get_color_data.save(using=DB)

            context['success_message'] = 'Item Updated Successfully';
    except ItemColor.DoesNotExist:
        context['error_message'] = 'No color found on this item to update, it\'s best you add new colors';



def item_Update_for_colors(request, context):
    update_color = request.POST.getlist('update_color[]')
    get_color = request.POST.getlist('color[]')
    get_state = request.POST.get('state')
    generated_code = request.POST.get('generated_code')

    if get_color != [] and  update_color != []:
        context['error_message'] = 'Please select either add new colors or update the existing colors';
    else:
        if get_color != []:
            add_new_color(request, get_color, generated_code, context)
        else:
            pass

        if update_color != []:
            update_color_func(request, update_color, generated_code, context)
        else:
            pass

        
# **************************** ITEM COLOR UPDATE FUNCTION USRED BY update_item(request, pk) (ITEM UPDATE PAGE)  *****************************



# ADD ITEM TO OUTLET USEED BY tockIn(request) (STOCKIN PAGAE)
def add_stockin(request, context):
  
    token_id = request.POST.get('token_id')
    outlet = request.POST.get('outlet')
    description = request.POST.get('description')
    item_code = request.POST.getlist('item_code[]')
    item_decription = request.POST.getlist('item_decription[]')
    item = request.POST.getlist('item[]')
    quantity = request.POST.getlist('quantity[]')
    selling_price = request.POST.getlist('selling_price[]')
    wholesale_price = request.POST.getlist('wholesale_price[]')
    item_length = len(item_code)
    for_count_down = len(item_code)
    DB = get_DB(request)
    i = 0
    ifgood = False;
    while i < item_length:
        if item_code[i] != '_ _Choose an Option_ _':
            to_be_stored = {
                'outlet':outlet, 
                'token_id':token_id, 
                'description':description,
                'quantity':quantity[i],
                'item_code': item_code[i], 
                'item_decription':item_decription[i], 
                'item':item[i], 
                'selling_price':selling_price[i], 
                'wholesale_price':wholesale_price[i],
                'Userlogin':request.user,
            }
            try:
                pass
                stockin = CreateOutletStockIn.objects.using(DB).get(Q(item_code= item_code[i]), Q(outlet=outlet))
                old_qty = stockin.quantity
                new_qty = float(old_qty) + float(quantity[i])
                stockin.quantity = new_qty
                stockin.save(using=DB)
                stockinLOG = CreateOutletStockInLog.objects.using(DB).create(**to_be_stored)
                ifgood = True;
            except CreateOutletStockIn.DoesNotExist:
                
                stockin = CreateOutletStockIn.objects.using(DB).create(**to_be_stored)
                stockinLOG = CreateOutletStockInLog.objects.using(DB).create(**to_be_stored)
                if stockin and stockinLOG:
                    ifgood = True;

        for_count_down -= 1
        i = i+1
    if for_count_down == 0:
        if ifgood:
            context['success_message'] = 'Item Stocked-in Successfully';


# GET STOCKIN HISTORY FUNCTION USEED BY stockin_history(request) (STOCKING HISTORY PAGE)
def get_stockin_history(request):
    fromdate = request.GET.get('fromdate')
    todate = request.GET.get('todate')
    searchItem = request.GET.get('searchItem')
    DB = get_DB(request)
    # get_history = CreateOutletStockInLog.objects.using(DB).all();
    ifgood = False;
    if  fromdate or todate:
        try:
            M_D, T_D = getdate(fromdate, todate)
            get_history = CreateOutletStockInLog.objects.using(DB).filter(Q(datetx__range=(M_D, T_D)));
            ifgood = True;
        except CreateOutletStockInLog.DoesNotExist:
            get_history = CreateOutletStockInLog.objects.using(DB).all();
            ifgood = True;
    

    if  searchItem:
        try:
            get_history = CreateOutletStockInLog.objects.using(DB).filter(Q(item__icontains=searchItem) | Q(item_code__icontains=searchItem) | Q(Userlogin__icontains=searchItem) | Q(selling_price__icontains=searchItem));
            ifgood = True;
        except CreateOutletStockInLog.DoesNotExist:
            get_history = CreateOutletStockInLog.objects.using(DB).all();
            ifgood = True;
    


    if ifgood:
        result = [({
            'datetx': data.datetx if data and data.datetx is not None else None,
            'item': data.item if data and data.item is not None else None,
            'item_code': data.item_code if data and data.item_code is not None else None,
            'selling_price': data.selling_price if data and data.selling_price is not None else None,
            'quantity': data.quantity if data and data.quantity is not None else None,
            'manufacture_date': data.manufacture_date if data and data.manufacture_date is not None else None,
            'expiry_date': data.expiry_date if data and data.expiry_date is not None else None,
            'token_id': data.token_id if data and data.token_id is not None else None,
            'Userlogin': data.Userlogin if data and data.Userlogin is not None else None,
            'id': data.id if data and data.id is not None else None,
            })
            for data in get_history
            ]
        return result;
   

# USED TO ADD AND UPDATE USED BY add_user(request) (ADD USER PAGE)
def AddUserFunction(request, context, form):
    if 'add_user' in request.POST:
        btn = request.POST.get('add_user')
        DB = get_DB(request)
        if btn == 'Create User':
            if form.is_valid():
            
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')

                user = form.save(commit=False)
                user.set_password(form.cleaned_data.get('password'))
                new_user = user.save(using=DB)
                # new_user = User.objects.using(DB).create_user(username, email, password)
                context["success_message"] =  'User Added Successfully' 
                # else:
                #     context["error_message"] =  'Request Failed' 
            else:
                context['formerror'] = form

        elif  btn == 'Update User':
            id = request.POST.get('id')
            update_user = User.objects.using(DB).get(id=id)
            update = RegisterForm(request.POST or None, instance=update_user)
            context['user_form'] = update
            if update.is_valid():
                save_withDB = update.save(commit=False)
                save_withDB.save(using=DB)

                context["success_message"] =  'User Account updated' 
            else:
                context['formerror'] = form

                context["error_message"] =  'Request Failed' 



# GET CURRENCIES(PLUS THE ONE ALREADY EXISTING)  USED BY add_profile(request) (ADD PROFILE PAGE)
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


# UPDATE AND EDIT PROFILE USED BY add_profile(request) (ADD PROFILE PAGE)
def update_edit_profile(request, profile_form, profiledata, context):
    DB = get_DB(request)
    getdata = profile_form.cleaned_data
    if profiledata.count() > 0:
        updateProfile           = CreateProfile.objects.using(DB).update(**getdata)
        if updateProfile :
            context["success_message"] =  'Profile Successfully Updated' 
    else:
        save_withDB = profile_form.save(commit=False)
        save_withDB.save(using=DB)
        if profile_form:
            context["success_message"] =  'Profile Successfully Created' 
        else:
            context["error_message"] =  'Failed to create profile' 



# EDIT USER ACCT USING AJAX TO FETCH DATA FOR EDITING (THE FUCNTION SHOULD BE CALLED FETCH USER ACCT) (ADD USER PAGE)
def edit_user(request):
    id = request.GET.get('id');
    DB = get_DB(request)
    try:
        getuser = User.objects.using(DB).get(id=id)
        return JsonResponse({'username':getuser.username, 'email':getuser.email, 'update':'Update User', 'password':getuser.password})
    except User.DoesNotExist:
        pass



# DELETE USER ACCT USING AJAX (ADD USER PAGE)
def Delete_user(request):
    id = request.GET.get('id');
    DB = get_DB(request)
    try:
        getuser = User.objects.using(DB).get(id=id)
        deleted = getuser.delete()
        if deleted:
            users = User.objects.using(DB).all()
            alluser = [({
            'date_joined':user.date_joined,
            'username':user.username,
            'email':user.email,
            'last_login':user.last_login,
            'Token_ID':user.Token_ID,
            'id':user.id,
            })
                for user in users
            ]
            return JsonResponse({'data':alluser})
    except User.DoesNotExist:
        pass


# DELETE ITEM USING AJAX (ADD ITEM PAGE)
def Delete_Item(request):
    id = request.POST.get('id');
    DB = get_DB(request)
    try:
        getItem_byID = Item.objects.using(DB).get(id=id)
        path = getItem_byID.image.url
        file_system_path = os.path.join(settings.MEDIA_ROOT, path[len(settings.MEDIA_URL):])
        if os.path.exists(file_system_path):
            os.remove(file_system_path)
       
        # else:
             

        deleted = getItem_byID.delete()

        if deleted:
            itemleft = Item.objects.using(DB).all().order_by('-id')
            allitem = [({
            'id':item.id,
            'item_name':item.item_name,
            'generated_code':item.generated_code,
            'category':item.category.category_name,
            'sub_category':item.sub_category,
            'selling_price':item.selling_price,
            'wholesale_price':item.wholesale_price,
            'image':item.image.url,
            'discount_price':item.discount_price,
            'discount_percentage':item.discount_percentage,
            })
                for item in itemleft
            ]
            return JsonResponse({'data':allitem})
    except Item.DoesNotExist:
        pass



# DELETE CUSTOMER ACCT USING AJAX (ADD CUSTOMER PAGE)
def deleteAccount(request):
    DB = get_DB(request)
    acctid = request.GET.get('id');
    if acctid:
        customer = customer_table.objects.using(DB).get(id=acctid)
        delete_acct= customer.delete()
        if delete_acct:
            all_left = retreiveAllCustomer(request);
            customer_acct = [({
               'name':acct.name,
                'phone':acct.phone,
                'email':acct.email,
                'address':acct.address,
                'company_name':acct.company_name,
                'id':acct.id,
                'category':acct.category,
                })
                    for acct in all_left
                ]
            return JsonResponse({'data':customer_acct})
        



# DELETE STOCK-IN HISTORY USING AJAX (STOCK-IN HISTORY PAGE)
def Delete_Stockin_History(request):
    acctid = request.GET.get('id');
    DB = get_DB(request)
    if acctid:
        customer = CreateOutletStockInLog.objects.using(DB).get(id=acctid)
        delete_acct= customer.delete()
        if delete_acct:
            all_left = CreateOutletStockInLog.objects.using(DB).all().order_by('-id');
            customer_acct = [({
               'datetx':acct.datetx,
                'item':acct.item,
                'item_code':acct.item_code,
                'selling_price':acct.selling_price,
                'quantity':acct.quantity,
                'manufacture_date':acct.manufacture_date,
                'expiry_date':acct.expiry_date,
                'token_id':acct.token_id,
                'Userlogin':acct.Userlogin,
                'id':acct.id,
                })
                    for acct in all_left
                ]
            return JsonResponse({'data':customer_acct})



# DELETE SALES HISTORY USING AJAX (SALES HISTORY PAGE)
def Delete_sales_history(request):
    salesID = request.GET.get('id');
    DB = get_DB(request)
    if salesID:
        invoice = customer_invoice.objects.using(DB).get(id=salesID)
        delete_acct= invoice.delete()
        if delete_acct:
            all_left = customer_invoice.objects.using(DB).all().order_by('-id');
            invoice_acct = loop_data(all_left)
            return JsonResponse({'data':invoice_acct})



# SALES SEARCH FOR DATE RANGE AND SEARCH DATA ( SALES HISTORY AND CUSTOMER SALES HISTORY) 
def Sales_Data(request):
    fromdate = request.GET.get('fromdate')
    todate = request.GET.get('todate')
    searchItem = request.GET.get('searchItem')
    from_CSH = request.GET.get('from_CSH')
    DB = get_DB(request)
    ifgood = False;
    try:
        if  fromdate or todate:
            M_D, T_D = getdate(fromdate, todate)
            if from_CSH == 'CHS':
                get_Sales_history =  customer_invoice.objects.using(DB).exclude(Q(cusID__isnull=True) | Q(customer_name='Casual Customer')).filter(Q(invoice_date__range=(M_D, T_D))).order_by('-id')
            else:
                get_Sales_history= customer_invoice.objects.using(DB).filter(Q(invoice_date__range=(M_D, T_D)))
            ifgood = True;
        # else:
        #     if from_CSH == 'CHS':
        #             get_Sales_history =  customer_invoice.objects.using(DB).exclude(Q(cusID__isnull=True) | Q(customer_name='Casual Customer')).order_by('-id')
        #     else:
        #         get_Sales_history= customer_invoice.objects.using(DB).all()
        #     ifgood = True;


        if  searchItem:
            if from_CSH == 'CHS':
                get_Sales_history = customer_invoice.objects.using(DB).exclude(Q(cusID__isnull=True) | Q(customer_name='Casual Customer')).filter(Q(cusID__icontains=searchItem) | Q(customer_name__icontains=searchItem));
            else:
                get_Sales_history = customer_invoice.objects.using(DB).filter(Q(item_name__icontains=searchItem) | Q(itemcode__icontains=searchItem));
            ifgood = True;
        
        # else:
        #     if from_CSH == 'CHS':
        #             get_Sales_history =  customer_invoice.objects.using(DB).exclude(Q(cusID__isnull=True) | Q(customer_name='Casual Customer')).order_by('-id')
        #     else:
        #         get_Sales_history= customer_invoice.objects.using(DB).all()  
        #     ifgood = True;

        if ifgood:
            sales_data = loop_data(get_Sales_history)
            total_sum = sum(item.amount for item in get_Sales_history)

            return JsonResponse({'data':sales_data, 'total_sum':total_sum})
        
    except customer_invoice.DoesNotExist:
        pass



# FETCHED ACCOUNT RECIEVABLE USING AJAX (ACCOUNT RECEIVABLE PAGE)
def get_account_receiables(request):
    searchItem = request.GET.get('search')
    DB = get_DB(request)
    ifgood = False;
    try:
        if  searchItem:
            acct_receiables = customer_table.objects.using(DB).filter(Q(Balance__icontains='-') & Q(customer_code__icontains=searchItem) | Q(name__icontains=searchItem)).order_by('-id');
            ifgood = True;
        
        else:
            acct_receiables = customer_table.objects.using(DB).filter(Q(Balance__icontains='-')).order_by('-id')
            ifgood = True;

        if ifgood:
            data = acct_receivables_loop_data(acct_receiables)
            return JsonResponse({'data':data})
        
    except customer_table.DoesNotExist:
        pass
       

# CREDIT ACCT USED BY account_recievable(request) (ACCOUNT RECEIVABLE)
def Credit_acct(request, context):
    CustomerID =  request.POST.get('CustomerID')
    CreditAmount =  request.POST.get('CA')
    DB = get_DB(request)
    if CreditAmount != '':
        try:
            updatebalance = customer_table.objects.using(DB).get(customer_code=CustomerID)
            bal = updatebalance.Balance
            update_bal = float(bal) + float(CreditAmount)
            updatebalance.Balance = update_bal
            updatebalance.save(using=DB)

            if updatebalance:
                context['success_message'] = 'Account credited';
        except customer_table.DoesNotExist:
            pass
    else:
        context['error_message'] = 'Invalid Request';



# ADD TO CATEGORY PAGE USED BY ItemCategory(request)
def add_category(request, form, context):
    cate_name = form.cleaned_data.get('category_name');
    sub_cate = form.cleaned_data.get('description');
    DB = get_DB(request)
    existing_category = Category.objects.using(DB).filter(category_name=cate_name, description=sub_cate).first()

    if existing_category:
        # If it exists, don't save the new record
        context['error_message'] = 'Data already exists';
    else:
        save_withDB = form.save(commit=False);
        save_withDB.save(using=DB)

        if form:
            context['success_message'] = 'Category addedd successfully';



# GET CATEGORY DETAIL VIEW USED BY ItemCategory(request)
def get_category_detail(request, categoryID):
    DB = get_DB(request)
    category = Category.objects.using(DB).get(id=categoryID)

    subcategories = Category.objects.using(DB).filter(category_name=category.category_name).values('description')
    category_data = {
        'id': category.id,
        'category_name': category.category_name,
        'description': category.description,
        'cat_img': category.cat_img.url if category.cat_img else None,
        'subcategories': list(subcategories),
    }
    return category_data



# UPDATE / EDIT CATEGORY USED BY edit_category(request, pk)
def Update_category(request, form, context):
    DB = get_DB(request)
    update_all = form.cleaned_data
    cate_name = form.cleaned_data.get('category_name');
    sub_cate = form.cleaned_data.get('description');
    cat_img = form.cleaned_data.get('cat_img');
    token_id = form.cleaned_data.get('token_id');
    existing_category = Category.objects.using(DB).get(token_id=token_id)
    if existing_category:
        # updated = Category.objects.using(DB).filter(token_id=token_id).update(**update_all);
        existing_category.category_name    = cate_name
        existing_category.description      = sub_cate
        if cat_img is not None:
            existing_category.cat_img          = cat_img
        existing_category.save(using=DB)
        
        
        if existing_category:
            context['success_message'] = 'Category Updated Successfully';
    else:
        context['error_message'] = 'Request Failed';


# GET NEW ITEM SUBCATEGORY USED BY  AddItemForSales(request)
def getNewItemSubcat(request):
    getsub= request.GET.get('data')
    DB = get_DB(request)
    if getsub:
        getcategory = Category.objects.using(DB).get(id=getsub);
        getsubcate = Category.objects.using(DB).filter(category_name=getcategory.category_name);
        # output = '';
        if getsubcate:
            sub_categories = [({
                'id':i.id,
                'description':i.description,
                })
                    for i in getsubcate
                ]
            return sub_categories
        
        
def profileNotification(DB, context):

    # IF ITEMS ARE EXPIRED
    items = ExpiryDate.objects.using(DB).all()
    today = date.today()
    notify = None
    notify1 = None
    
    for i in items:
        i.rdays = (i.expiry_date - today).days
        if i.rdays < 1:
            notify = 1;
            context['notify'] = notify;
            if notify == 1:
                getExpiredItems = CreateOutletStockInLog.objects.using(DB).get(Q(item_code=i.item_code) & Q(token_id=i.token_id))
                getExpiredItems.status = 'expired'
                getExpiredItems.save(using=DB)
           

        if i.rdays >= 1:
            notify1 = 1;
            context['notify1'] = notify1;


    # IF PROFILE IS SET
    countProfile = CreateProfile.objects.using(DB).all()
    lenght = len(countProfile)
    if lenght > 0:
        count =  1
        context['count'] = count
        # return JsonResponse({'result': True})
    else:
        pass
