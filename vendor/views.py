from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages 


from .models import vendor_table, Vendor_Quote, Vendor_Order, Vendor_Return, Vendor_invoice

# from account.models import Payment_method, StockIn_Log, Stock_In, account_log, Outlet_StockIn, Outlet_StockIn_Log, chart_of_account
from account.models import *
from settings.models import *

from Stock.models import *
from customer.models import customer_invoice, payable, Vat
from main.models import User

from .functions.vendorfunc import *
from .functions.purchasequote import add_purchase_quote, update_purchase_quote
from .functions.purchaseorder import add_purchase_order
from .functions.ReturnOutward import add_return_item
from .functions.purchaseinvoice import add_purchase_invoice

from django.http.response import JsonResponse


from routers.page_permission import  urls_name
from Stock.utils import random_string_generator;
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from itertools import zip_longest






@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def NewPurchase(request):
    db = request.user.company_id.db_name
    account = chart_of_account.objects.using(db).filter(account_id__startswith='2')
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    payment = Payment_method.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    item = Item.objects.using(db).all()


    invoiceID =  random_string_generator()

    
    if request.method == "POST":
           
        # outlet = User.objects.get(id = request.user.id).outlet
        # if outlet:
           add_purchase_invoice(request, db)
        # else:
        #     messages.error(request, "Assign outlet to logged in user")
     
   
    context = {
        'account': account,
        'supplier': supplier,
        'warehouse': warehouse,
        'payment': payment,
        'outlet': outlet,
        'item': item,
       'invoiceID': 'INV_'+invoiceID,

    }
    return render(request, 'vendor/NewPurchase.html', context)

from datetime import datetime

   
def getdate(fromdate, todate):
   from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
   to_date = datetime.strptime(todate, '%Y-%m-%d').date()
   return from_date, to_date

def getStockAdjustmentData(request, db):
   if request.method == 'GET':
      getinvoiceID = request.GET.get('invoiceID')
      getidcode = request.GET.get('idcode')
      if getinvoiceID and getidcode:
        ifFailed = {'failed': "No Data Found"}
        try: 
            getid = Vendor_invoice.objects.using(db).get(Q(invoiceID=getinvoiceID,) & Q(id=getidcode))
        except Vendor_invoice.DoesNotExist:
            return ifFailed
        # try:
        #     getid = CreateOutletStockInLog.objects.using(db).get(Q(invoice_no=getinvoiceID,) & Q(id=getidcode))
        # except CreateOutletStockInLog.DoesNotExist:
        #     pass

        fetchonce = {
            'item':getid.item_name,
            'invoice_no':getid.invoiceID,
            'date':getid.invoice_date,
            'description':getid.item_descriptions,
            'qty':getid.qty,
            'id':getid.id,
         }
        if fetchonce:
            return fetchonce
        else:
            return ifFailed



def getStockAdjustmentDate2(request, context, db, con):
   if request.method == 'GET':
        getfromdate = request.GET.get('fromdate')
        gettodate = request.GET.get('todate')
        invoice = request.GET.get('invoice')
        sortbyItem = request.GET.get('sortbyItem')
        failed = {'failed': "No Data Found"}
        if getfromdate and gettodate:
            from_date, to_date =getdate(getfromdate, gettodate)
            try:
                getstockin_log = Vendor_invoice.objects.using(db).filter(Q(invoice_date__range=(from_date, to_date)) & con)
            except Vendor_invoice.DoesNotExist:
                return failed
            
        if sortbyItem is not None:
            try:
                getstockin_log = Vendor_invoice.objects.using(db).filter(Q(itemcode=sortbyItem) & con)
            except Vendor_invoice.DoesNotExist:
                return failed
          
        if invoice is not None and invoice != '_ _Choose Item_ _':
            try:
                getstockin_log = Vendor_invoice.objects.using(db).filter(Q(invoiceID=invoice) & con)
            except Vendor_invoice.DoesNotExist:
                return failed
          
        if sortbyItem or invoice or getfromdate and gettodate is not None:
        
            if getstockin_log:
                # Vendor_invoice
                result_stockinlog = [({
                    'id': stockinlog.id if stockinlog and stockinlog.id is not None else None,
                    'datetx': stockinlog.invoice_date if stockinlog and stockinlog.invoice_date is not None else None,
                    'invoice_no': stockinlog.invoiceID if stockinlog and stockinlog.invoiceID is not None else None,
                    'item': stockinlog.item_name if stockinlog and stockinlog.item_name is not None else None,
                    'quantity': stockinlog.qty if stockinlog and stockinlog.qty is not None else None,
                    'item_decription': stockinlog.item_descriptions if stockinlog and stockinlog.item_descriptions is not None else None,
                    'token_id': stockinlog.token_id if stockinlog and stockinlog.token_id is not None else None,
                    })
                    for stockinlog in getstockin_log
                ]
                return result_stockinlog
            else:
                return failed


def stock_adjustment_arithmetic_logic(stockinQty, form_qty, getqty):
    if float(form_qty) > float(getqty.qty):
        currentQty = float(form_qty) - float(getqty.qty)
        stockinQtyNew = float(stockinQty) + float(currentQty)
        return stockinQtyNew
        # stockinQty.save(using=db)
        # stockinLog qty update
        
    else:
        currentQty = float(getqty.qty) - float(form_qty)
        stockinQtyNew = float(stockinQty) - float(currentQty)
        return stockinQtyNew
        # stockinLog qty update
        

@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def cancle_invoice(request, context, form_invoiceID, db, form_id):
    payable_qs = payable.objects.using(db).all()
    getqty_outlet_stockinlog=None
    getqty_stockinlog=None

    try:
        vendorInv = Vendor_invoice.objects.using(db).get(invoiceID=form_invoiceID, id=form_id)
        amount_paid = vendorInv.amount_paid
        amount_expected = vendorInv.amount_expected
        # check if the items were fully paid for
        if amount_paid == amount_expected:
            payable_qs = payable.objects.using(db).create(
                type='Credit', 
                transaction_id=form_invoiceID, 
                amount=vendorInv.amount, 
                vendor_name=vendorInv.vendor_name,
                payment_method='Cash',
                Userlogin=request.user,
            )


        # check if the items were partly paid for
        if amount_paid < amount_expected:
            payable_qs = payable.objects.using(db).create(
                type='Credit', 
                transaction_id=form_invoiceID, 
                amount=amount_paid, 
                vendor_name=vendorInv.vendor_name,
                payment_method='Cash',
                Userlogin=request.user,
            )

        
        # check if the items were not paid for
        if amount_paid == 0.00:
            liability_qs = Liability_account.objects.using(db).create(
                type='Credit', 
                transaction_id=form_invoiceID, 
                amount=vendorInv.amount, 
                vendor_name=vendorInv.vendor_name,
                payment_method='Cash',
                Userlogin=request.user,
            )
        try:
            getqty_stockinlog = CreateStockInLog.objects.using(db).get(invoice_no=form_invoiceID, item_code=vendorInv.itemcode)
            getqty_stockinlog.quantity = 0
            getqty_stockinlog.status = 'Cancelled'
            getqty_stockinlog.save(using=db)

        except CreateStockInLog.DoesNotExist:
            pass

        try:
            getqty_outlet_stockinlog = CreateOutletStockInLog.objects.using(db).get(invoice_no=form_invoiceID, item_code=vendorInv.itemcode)
            getqty_outlet_stockinlog.quantity = 0
            getqty_outlet_stockinlog.status = 'Cancelled'
            getqty_outlet_stockinlog.save(using=db)
        except CreateOutletStockInLog.DoesNotExist:
            pass
        if getqty_stockinlog is not None:
            try:
                get_qty_from_stockin = CreateStockIn.objects.using(db).get(warehouse=getqty_stockinlog.warehouse, item_code=getqty_stockinlog.item_code)
                stockinQty =get_qty_from_stockin.quantity
                get_qty_from_stockin.quantity = float(stockinQty) - float(vendorInv.qty)
                # stockin qty update
                get_qty_from_stockin.save(using=db)
            except CreateStockIn.DoesNotExist:
                pass
        if getqty_outlet_stockinlog is not None:
            try:
                get_qty_from_stockin = CreateOutletStockIn.objects.using(db).get(warehouse=getqty_outlet_stockinlog.warehouse, item_code=getqty_outlet_stockinlog.item_code)
                stockinQty =get_qty_from_stockin.quantity
                get_qty_from_stockin.quantity = float(stockinQty) - float(vendorInv.qty)
                # Outletstockin qty update
                get_qty_from_stockin.save(using=db)
            except CreateOutletStockIn.DoesNotExist:
                pass

    except Vendor_invoice.DoesNotExist:
        context['error_message']   = 'Data Not Found'
    
    

    if vendorInv and get_qty_from_stockin:
            vendorInv.qty = 0
            vendorInv.amount_paid  = amount_expected
            vendorInv.cancellation  = 1
            vendorInv.save(using=db)
            context['success_message'] = 'Invoice has been canceled'
    else:
        context['error_message']   = 'Cancellation Failed'


# @login_required(login_url="/")
# @urls_name(name="Purchase Invoices")
def update_invoice(db, context, form_id, form_invoiceID, form_qty, request):
    # Convert qty to integer early (with fallback)
    try:
        form_qty = int(form_qty)
    except (ValueError, TypeError):
        form_qty = 0
        context['error_message'] = 'Invalid quantity value'
        return

    # Default initial quantity
    stockinQty = 0
    getqty_outlet_stockinlog = None
    getqty_stockinlog = None
    vendorInv = None  # ← initialize here so it's always defined

    try:
        vendorInv = Vendor_invoice.objects.using(db).get(invoiceID=form_invoiceID, id=form_id)

        # Update regular stock-in log if exists
        try:
            getqty_stockinlog = CreateStockInLog.objects.using(db).get(
                invoice_no=form_invoiceID,
                item_code=vendorInv.itemcode
            )
            getqty_stockinlog.quantity = form_qty
            getqty_stockinlog.save(using=db)
        except CreateStockInLog.DoesNotExist:
            pass

        # Update outlet stock-in log if exists
        try:
            getqty_outlet_stockinlog = CreateOutletStockInLog.objects.using(db).get(
                invoice_no=form_invoiceID,
                item_code=vendorInv.itemcode
            )
            getqty_outlet_stockinlog.quantity = form_qty
            getqty_outlet_stockinlog.save(using=db)
        except CreateOutletStockInLog.DoesNotExist:
            pass

        # Update main stock quantity (warehouse)
        if getqty_stockinlog is not None:
            try:
                get_qty_from_stockin = CreateStockIn.objects.using(db).get(
                    warehouse=getqty_stockinlog.warehouse,
                    item_code=getqty_stockinlog.item_code
                )
                stockinQty = get_qty_from_stockin.quantity
                get_qty_from_stockin.quantity = stock_adjustment_arithmetic_logic(
                    stockinQty, form_qty, vendorInv
                )
                get_qty_from_stockin.save(using=db)
            except CreateStockIn.DoesNotExist:
                pass

        # Update main stock quantity (outlet) — only if no warehouse log
        elif getqty_outlet_stockinlog is not None:
            try:
                get_qty_from_stockin = CreateOutletStockIn.objects.using(db).get(
                    warehouse=getqty_outlet_stockinlog.warehouse,
                    item_code=getqty_outlet_stockinlog.item_code
                )
                stockinQty = get_qty_from_stockin.quantity
                get_qty_from_stockin.quantity = stock_adjustment_arithmetic_logic(
                    stockinQty, form_qty, vendorInv
                )
                get_qty_from_stockin.save(using=db)
            except CreateOutletStockIn.DoesNotExist:
                pass

        else:
            context['error_message'] = 'No matching stock-in log found'

    except Vendor_invoice.DoesNotExist:
        context['error_message'] = 'Invoice not found'
        # No return here — continue to log if possible, or return early if you prefer
        # return

    # Create adjustment log — safe because stockinQty is always set
    Stock_Adjustment_Log = StockAdjustmentLog.objects.using(db).create(
        invoice_no=form_invoiceID,
        initial_qty=stockinQty,
        new_qty=form_qty,
        item_code=vendorInv.itemcode if vendorInv else None,  # ← safe access
        Userlogin=request.user.username,
        type='purchase',
    )

    # Only update invoice if it exists
    if vendorInv:
        vendorInv.qty = form_qty
        vendorInv.save(using=db)
        context['success_message'] = 'Quantity Updated'
    else:
        context['error_message'] = 'Update Failed - Invoice not found'
        

def updateStockAdjustmentData(request, context, db):
   if request.method == 'POST':
        form_qty = request.POST.get('modalNewqty')
        form_id = request.POST.get('modalID')
        form_invoiceID = request.POST.get('modalinvoiceID')
        # UPDATE INVOICE
        if 'update_invoice' in request.POST:
            update_invoice(db, context, form_id, form_invoiceID, form_qty, request)
        

        # CANCLE INVOICE
        if 'cancle_invoice' in request.POST:
            cancle_invoice(request, context, form_invoiceID, db, form_id)



# ********************************************************************************************************

@login_required(login_url="/")
@urls_name(name = "Purchase Adjustment")
def PurchaseAdjustment(request):
    db = request.user.company_id.db_name
    # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
    vendorInvoice = Vendor_invoice.objects.using(db).filter(~Q(cancellation=1))
    # outlet_stockin_log = CreateStockInLog.objects.using(db).all()
    # outlet_stockin_log = CreateOutletStockInLog.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    getitem = Item.objects.using(db).all();
    context = {
      'allinvoice': vendorInvoice,
      'items': getitem,
      'warehouse': warehouse,
      'outlet': outlet,
    }
 
   # function to fetch data for update(when edit btn is clicked)
    data = getStockAdjustmentData(request, db)
    if data:
        # do not assign a key to data
        return JsonResponse(data)
    # update function
    updateStockAdjustmentData(request, context, db)

   # get function
    stockinlog=getStockAdjustmentDate2(request, context, db, ~Q(cancellation=1))
    if stockinlog:
        return JsonResponse({'stockin':stockinlog})


    return render(request, 'vendor/PurchaseAdjustment.html', context)

# ********************************************************************************************************



# ********************************************************************************************************
         
@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def CanclePurchaseInvoice(request):
    db = request.user.company_id.db_name
    # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
    vendorInvoice = Vendor_invoice.objects.using(db).filter(~Q(cancellation=1))
    # outlet_stockin_log = CreateStockInLog.objects.using(db).all()
    # outlet_stockin_log = CreateOutletStockInLog.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    getitem = Item.objects.using(db).all();
    context = {
      'allinvoice': vendorInvoice,
      'items': getitem,
      'warehouse': warehouse,
      'outlet': outlet,
    }

   
#     # update function
#     updateStockAdjustmentData(request, context, db)

#    # get function
#     stockinlog=getStockAdjustmentDate2(request, context, db, ~Q(cancellation=1))
#     if stockinlog:
#         return JsonResponse({'stockin':stockinlog})


    return render(request, 'vendor/CanclePurchaseInvoice.html', context)

# ********************************************************************************************************


# ********************************************************************************************************
         
@login_required(login_url="/")
@urls_name(name="Purchase Invoices")
def viewCanclePurchase(request):
    db = request.user.company_id.db_name
    # allinvoice = customer_invoice.objects.filter(invoiceID='11971')
    vendorInvoice = Vendor_invoice.objects.using(db).filter(Q(cancellation=1))
    # outlet_stockin_log = CreateStockInLog.objects.using(db).all()
    # outlet_stockin_log = CreateOutletStockInLog.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    outlet = sales_outlet.objects.using(db).all()
    getitem = Item.objects.using(db).all();
    context = {
      'allinvoice': vendorInvoice,
      'items': getitem,
      'warehouse': warehouse,
      'outlet': outlet,
    }

   
   # get function
    stockinlog=getStockAdjustmentDate2(request, context, db, Q(cancellation=1))
    if stockinlog:
        return JsonResponse({'stockin':stockinlog})


    return render(request, 'vendor/viewCanclePurchase.html', context)

# ********************************************************************************************************


def GetSubCategory(request, id):
    db = request.user.company_id.db_name
    try:
        vendor = vendor_table.objects.using(db).get(id=id)
        data = {
                'name': vendor.name,
            }
        return JsonResponse(data)
    except vendor_table.DoesNotExist: 
        return JsonResponse({'error': 'Vendor not found'}, status=404)






# def GetVendorDetails(request, id):
#     db = request.user.company_id.db_name
#     venID =   request.POST.get('venID')
#     lookup = Q(id__iexact=venID) | Q(custID__iexact=venID)
#     try:
#         vendor = vendor_table.objects.using(db).get(Q(lookup))
#         data = {
#                 'name': vendor.name,
#                 'phone': vendor.phone,
#                 'email': vendor.email,
#                 'custID': vendor.custID,
#                 'company_name': vendor.company_name,
#                 'address': vendor.address,
#             }
#         return JsonResponse(data)
#     except vendor_table.DoesNotExist:
#         return JsonResponse({'error': 'Vendor not found'}, status=404)


def GetVendorDetails(request, id):
    db = request.user.company_id.db_name
    venID = request.GET.get('venID')  
    
    if not venID:
        return JsonResponse({'error': 'No vendor ID provided'}, status=400)
    
    lookup = Q(id=venID) | Q(custID__iexact=venID)
    try:
        vendor = vendor_table.objects.using(db).get(lookup)
        data = {
            'name': vendor.name,
            'phone': vendor.phone,
            'email': vendor.email,
            'custID': vendor.custID,
            'company_name': vendor.company_name,
            'address': vendor.address,
        }
        return JsonResponse(data)
    except vendor_table.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)
    except vendor_table.MultipleObjectsReturned:
        return JsonResponse({'error': 'Multiple vendors found'}, status=400)




def GetItemDetails(request, item_id):
    db = request.user.company_id.db_name
    try:
        item = Item.objects.using(db).get(generated_code=item_id)
        data = {
                    'desc': item.description,
                    'name': item.item_name,
                    'unit': item.selling_price,
                    'amount': item.purchase_price
                }
        return JsonResponse(data)
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def GetInvoiceDetails(request, invoice_id):
    db = request.user.company_id.db_name
    invoiceID = request.GET.get('invoiceID')
    try:
        # Fetch all fields related to the given invoice_id
        data = Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).values()
        
       
        def get_customer_or_vendor():
            invoice = Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
            if invoice:
                try:
                    vendor_table.objects.using(db).filter(custID=invoice.cusID)
                    return "Vendor"
                except vendor_table.DoesNotExist:
                    return "None"
            else:
                return "None"

        accountType = get_customer_or_vendor()
        
        try:
            vat = Vat.objects.using(db).get(source=invoiceID).amount
        except Vat.DoesNotExist:
            vat = None

        # Serialize the queryset to JSON

        serialized_data = {
            'invoice':list(data),
            'accountType':accountType,
            'vat': vat
        }

        return JsonResponse(serialized_data,  safe=False)
    except Vendor_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
   



@login_required(login_url='/')
@urls_name(name = "Purchase Quotes")
def NewPurchaseQuote(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()

    if request.method == "POST":
        add_purchase_quote(request, db)
    
    context = {
        
        'supplier': supplier,
        'item': item
    }

    return render(request, 'vendor/NewPurchaseQuote.html', context)


@login_required(login_url='/')
@urls_name(name = "Purchase Quotes")
def UpdatePurchaseQuote(request, pk):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    instance = Vendor_Quote.objects.using(db).get(pk=pk)
    quotes = Vendor_Quote.objects.using(db).filter(quote_ID=instance.quote_ID)
    item = Item.objects.using(db).all()

    if request.method == "POST":
        update_purchase_quote(request, instance, db)
    
    context = {
        
        'supplier': supplier,
        'instance': instance,
        'quotes': quotes,
        'item': item
    }

    return render(request, 'vendor/UpdatePurchaseQuote.html', context)
  
  

@login_required(login_url='/')
@urls_name(name = "Purchase Quotes")
def ViewPurchaseQuote(request):
    db = request.user.company_id.db_name
    purchase_quote = Vendor_Quote.objects.using(db).all()
   
    return render(request, 'vendor/ViewPurchaseQuote.html', {'purchase_quote': purchase_quote})



@login_required(login_url='/')
@urls_name(name = "Purchase Order")
def NewPurchaseOrder(request):
    db = request.user.company_id.db_name
    supplier = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    
    if request.method == "POST":
        add_purchase_order(request, db)
     
    context = {
        
        'supplier': supplier,
        'item': item
    }
   
    return render(request, 'vendor/NewPurchaseOrder.html', context)

@login_required(login_url='/')
@urls_name(name = "Purchase Order")
def ViewPurchaseOrder(request):
    db = request.user.company_id.db_name
    purchase_order = Vendor_Order.objects.using(db).all()
   
    return render(request, 'vendor/ViewPurchaseOrder.html', {'purchase_order': purchase_order})


@login_required(login_url='/')
@urls_name(name = "Returns Outwards")
def ReturnItems(request):
    db = request.user.company_id.db_name
    payment = Payment_method.objects.using(db).all()
    supplier = vendor_table.objects.using(db).all()
    warehouse = Warehouse.objects.using(db).all()
    amount = Vendor_Order.objects.using(db).all()
    item = Item.objects.using(db).all()
    account = chart_of_account.objects.using(db).filter(account_bankname__icontains="Return Outward")
    
    if request.method == "POST":
        add_return_item(request, db)
     
    context = {
        'payment': payment,
        'warehouse': warehouse,
        'supplier': supplier,
        'amount': amount,
        'items': item,
        'accounts': account
    }
   
    return render(request, 'vendor/ReturnItems.html', context)

@login_required(login_url='/')
@urls_name(name = "Returns Outwards")
def ViewReturnOutwards(request):
    db = request.user.company_id.db_name
    return_outwards = Vendor_Return.objects.using(db).all()
   
    return render(request, 'vendor/ViewReturnOutwards.html', {'return_outwards': return_outwards})

@login_required(login_url='/')
@urls_name(name = "Returns Outwards")
def GetReturnOutwardItemDetails(request, invoice, item_id):
    db = request.user.company_id.db_name
  
    try:
       item = Vendor_invoice.objects.using(db).get(invoiceID=invoice, itemcode=item_id)
      
       data = {
            'desc': item.item_descriptions,
            'name': item.item_name,
            'qty': item.qty,
            'unit': item.amount,
            'generated_code': item.itemcode
        }
       return JsonResponse(data)
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)


@login_required(login_url="/")
@urls_name(name='Vendor')
def register_vendor(request):
    db = request.user.company_id.db_name
    form = VendorRegistrationForm(request.POST or None)
    display_vendor = vendor_table.objects.using(db).all()

    if request.method == "POST":
        add_vendor(request, db)

    context = {
        "form": form,
        "display_vendor": display_vendor
    }
    return render(request, 'vendor/AddVendor.html', context)


@login_required(login_url="/")
@urls_name(name='Vendor')
def update_vendor(request, id):
    db = request.user.company_id.db_name
    vendor = vendor_table.objects.using(db).get(id = id)
    
    if request.method == "POST":
        edit_vendor(request, id, db)
        return redirect('vendor:view_vendor')
        

    context = {
        'vendor': vendor
    }
    return render(request, 'vendor/EditVendor.html', context)


@login_required(login_url="/")
@urls_name(name='Vendor')
def view_vendor(request):
    db = request.user.company_id.db_name
    display_vendor = vendor_table.objects.using(db).all()

    context = {
        "display_vendor": display_vendor
    }
    return render(request, 'vendor/ViewVendor.html', context)


@login_required(login_url="/")
@urls_name(name='Vendor')
def delete_vendor(request, id):
    db = request.user.company_id.db_name
    delete_vendor = vendor_table.objects.using(db).get(id=id)
    delete_vendor.delete()
    messages.success(request, "Vendor deleted successfully")
    return redirect('vendor:register_vendor')




# ==== VIEW USER INFORMATION ====
def view_user_information(request, username):
    db = request.user.company_id.db_name
    account = vendor_table.objects.using(db).get(username=username)

    following = False

    muted = None

    if request.user.is_authenticated:

        if request.user.id == account.id:
            return redirect("profile")
        
        followers = account.followers.filter(
            followed_by__id = request.user.id
        )

        if followers.exists():
            following = True

    if following:
        queryset = followers.first()
        if queryset.muted:
            muted = True
        else:
            muted = False

    context = {
        "account": account,
        "following": following,
        "muted": muted,
    }

    return render(request, "user_information.html", context)




