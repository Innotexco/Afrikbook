import requests
import json
from django.shortcuts import render, redirect
from .models import customer_table, customer_invoice
from vendor.models import vendor_table
from account.models import *
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .utils import  generate_invoice_id, generate_customer_id

from .functions.customer import *
from .functions.salesquote import *
from .functions.salesorder import *
# from .functions.newsales import *
from .functions.newsalesfunc import *
from .functions.returninwards import *
from .functions.verifypayment import *
from django.db.models import Q
from Stock.models import Item, CreateStockIn
from settings.models import *
from client .models import shipping_addr
from client .api import is_endpoint_available
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name
from main .models import company_table

#Vendor functions
from vendor.functions.purchasequote import add_purchase_quote
from vendor.functions.purchaseorder import add_purchase_order
# import requests

# Create your views here.
@login_required(login_url='/')
@urls_name(name = "Customer")
def Customers(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()

    context = {
        'customers':customers,
    }
   
    return render(request, 'customer/Customers.html', context)

@login_required(login_url='/')
@urls_name(name="Customer")
def ViewCustomerDetails(request, id):
    db = request.user.company_id.db_name
    
    try:
        customer = customer_table.objects.using(db).get(customer_code=id)
        invoice = customer_invoice.objects.using(db).filter(cusID=id).values('invoiceID').distinct()
    #    invoice = list(customer_invoice.objects.filter(cusID=id).values())
    
    #    invoices = customer_invoice.objects.filter(cusID=id).values()

        unique_invoice = []
        for i in invoice:
           new_data = customer_invoice.objects.using(db).filter(cusID=id, invoiceID=i['invoiceID']).values()#.order_by('invoice_date')

           if new_data.exists():
               unique_invoice.append(new_data.first())

        try:
            credit = receivable.objects.using(db).filter(customer_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
            debit = receivable.objects.using(db).filter(customer_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
            balance = Decimal(credit) - Decimal(debit)
            
      
        except receivable.DoesNotExist:
            balance = "0.00"

        data = {
            'customer': {
                'name': customer.name,
                'phone': customer.phone,
                'code': customer.customer_code,
                'balance': format(balance, ".2f"),
            },
            'invoices': list(unique_invoice),
        }
       
        return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    


@login_required(login_url='/')
@urls_name(name="Customer")
def AddCustomer(request):
    db = request.user.company_id.db_name
    customer_code = generate_customer_id()


    customer = customer_table.objects.using(db).all()
    
    #Endpoint api 
    try:
        response = requests.get('https://console.afrikbook.com/address', timeout=10)
        if response.status_code == 200:
            data = response.json()

            for cus in customer:  
                ship_count = sum(0 for ship in data['ship'] if ship['addr_id_id'] == cus.id)
                cus.ship = ship_count
        else:
            for cus in customer:
                cus.ship = 0
    except requests.RequestException:
        messages.error(request, "Endpoint not available")
        #pass
    
    form = None
    if request.method == 'POST':
        # add_customer(request, db)
        form = add_customer(request, db)
     
    context = {
        'customers': customer,
        'customer_code': customer_code,
        'form': form
    }
    return render(request, "customer/NewCustomer.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def UpdateCustomer(request, id):
    db = request.user.company_id.db_name
    
    customer = customer_table.objects.using(db).get(id=id)
    customers = customer_table.objects.using(db).all()
   
    if request.method == 'POST':    
        update_customer(request, id, db)
        return redirect("customer:NewCustomer")
        
    context = {
        "customer": customer,
        "customers": customers
    }   
    return render(request, "customer/EditCustomer.html", context)

# @urls_name(name="Customer")

def delete_customer(request, id):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).get(id=id)
    customer.delete()
    messages.error(request, "Customer was deleted successfully")
    return redirect("customer:NewCustomer")

@login_required(login_url='/')
@urls_name(name="Customer")
def CusOpenBalance(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    if request.method == "POST":
        cus_open_balance(request, db)

    context = {
        "customers": customers,
        "accounts": accounts
    }
    return render(request, "customer/CustomerOpeningBalance.html", context)

@login_required(login_url='/')
@urls_name(name="Customer")
def RefundCustomer(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    form = None
    if request.method == "POST":
       form = refund_customer(request, db)

    context = {
        "customers": customers,
        "accounts": accounts,
        "form":form
    }
    return render(request, "customer/RefundCustomer.html", context)

@login_required(login_url='/')
@urls_name(name="Sales Invoices")
def SalesInvoice(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    # shipping_address = shipping_addr.objects.using('afrikbook_client').all()
    billing_address = billing_addr.objects.using('afrikbook_client').all()
    company = company_table.objects.get(id=request.user.company_id_id)

    stocked = CreateStockIn.objects.using(db).values_list('item_code', flat=True).distinct()
    # item = Item.objects.using(db).filter(generated_code__in=stocked)
    item = Item.objects.using(db).all()
    method = shipping_method.objects.using(db).all()

    #Endpoint api 
    try:
        response = requests.get('http://127.0.0.1:8000/address', timeout=10)
        if response.status_code == 200:
            shipping_address = response.json() 
        else:
            shipping_address = []
    except requests.RequestException:
       shipping_address = []
       
    invoice = generate_invoice_id()
    form = None
    if request.method == "POST":
        outlet = User.objects.get(id = request.user.id).outlet
        if outlet:
           form = add_new_sales(request, db)
        else:
            messages.error(request, "Assign outlet to logged in user")
     
    context = {
        'customers': customer,
        'vendor':vendor,
        'accounts': accounts,
        'items': item,
        'invoice':invoice,
        'form': form,
        'company': company,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'shipping_method': method
    }    
    return render(request, "customer/NewSales.html", context)



from main .views import send_email, send_email_with_pdf

@login_required(login_url='/')
@urls_name(name="Sales Quotes")
def AddSalesQuote(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    company = company_table.objects.get(id=request.user.company_id_id)
    form = None
    if request.method == "POST":
        selected = request.POST['accountType']
        if selected == "Customer":
           form = add_sales_quote(request, db)
        elif selected == "Vendor":
           form = add_sales_quote(request, db)
            # add_purchase_quote(request, db)
        else:
            messages.error(request, "Select customer or vendor")
        
        send_email()
     
    context = {
        
        'customers': customer,
        'vendor':vendor,
        'items': item,
        'form': form,
        'company': company
    }    
    return render(request, "customer/NewSalesQuote.html", context)


@login_required(login_url='/')
@urls_name(name="Sales Quotes")
def SalesQuote(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    # customer = customer_table.objects.all()
    # vendor = vendor_table.objects.all()
    # item = Item.objects.all()
    
    # if request.method == "POST":
    #     add_sales_quote(request)
     
    context = {
        
        'company': company,
    }
    return render(request, "customer/SalesQuote.html", context)

@login_required(login_url='/')
@urls_name(name="Sales Order")
def AddSalesOrder(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    company = company_table.objects.get(id=request.user.company_id_id)
    form = None
    if request.method == "POST":
        selected = request.POST['accountType']
       
        if selected == 'Customer':
           form = add_sales_order(request, db)
        elif selected == 'Vendor':
           form =  add_sales_order(request, db)
            # add_purchase_order(request, db)
        else:
            messages.error(request, "Select customer or vendor")
     
    context = {
        
        'customers': customer,
        'vendor':vendor,
        'items': item,
        'form':form,
        'company': company
    }    
    return render(request, "customer/NewSalesOrder.html", context)


@login_required(login_url='/')
@urls_name(name="Sales Order")
def SalesOrder(request):
    # customer = customer_table.objects.all()
    # item = Item.objects.all()

    # if request.method == "POST":
    #     add_sales_order(request)
     
    # context = {
        
    #     'customers': customer,
    #     'items': item
    # }   
    return render(request, "customer/SalesOrder.html")


def GetItemDetails(request, item_id):
    db = request.user.company_id.db_name 
    sales_type = request.GET.get('type')
   
    stock =    CreateOutletStockIn.objects.using(db).filter(item_code=item_id, outlet=request.user.outlet).count()
    
    if sales_type == "sales":
        if stock > 0:
            data, status = getItem(db, item_id)
            return JsonResponse(data, status=status)
        else:
        
            return JsonResponse({'error': 'Item not in '+request.user.outlet}, status=404)
    else:
        data, status = getItem(db, item_id)
        return JsonResponse(data, status=status)

def getItem(db, item_id):
    try:  
        item = Item.objects.using(db).get(generated_code=item_id)
        data = {
                'desc': item.description,
                'name': item.item_name,
                'unit': item.selling_price,
                'purchase': item.purchase_price,
                'generated_code': item.generated_code
            }
        # return JsonResponse(data)
        status = 200
    except Item.DoesNotExist: 
        data = {'error': 'Item not found'}
        status = 404
    return data, status
    
def GetReturnItemDetails(request,invoice, item_id):
    db = request.user.company_id.db_name
 
    try:
       
       item = customer_invoice.objects.using(db).get(invoiceID=invoice, itemcode=item_id)
       data = {
            'desc': item.item_description,
            'name': item.item_name,
            'qty': item.qty,
            'unit': item.amount,
            'purchase': item.purchaseP,
            'generated_code': item.itemcode
        }
       return JsonResponse(data)
    except customer_invoice.DoesNotExist: 
        
        return JsonResponse({'error': 'Item not found'}, status=404)
    

def GetCustomerDetails(request, id):
    db = request.user.company_id.db_name
    cusID = request.GET.get("cusID")
    
    lookup = Q(id__iexact=cusID) | Q(customer_code__iexact=cusID)
    try:
       customer = customer_table.objects.using(db).get(lookup)
       data = {
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'category': customer.category,
            'code': customer.customer_code,
            'company': customer.company_name,
            'instant_email': customer.instant_email,
            'balance': customer.Balance
        }
       return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    
def GetCustomerBalance(request, id):
    db = request.user.company_id.db_name
    try:
        credit = receivable.objects.using(db).filter(customer_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
        debit = receivable.objects.using(db).filter(customer_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
        data = Decimal(credit) - Decimal(debit)
        return JsonResponse(data, safe=False)
        
    except receivable.DoesNotExist: 
        return JsonResponse({'error': 'Customer not found'}, status=404)
    
def GetCustomer_or_VendorBalance(request,):
    db = request.user.company_id.db_name
    cusID = request.GET.get("ID")
    accountType = request.GET.get("type")
    if accountType == "Customer":
        id = customer_table.objects.using(db).get(id=cusID).customer_code
        try:
            credit = receivable.objects.using(db).filter(customer_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
            debit = receivable.objects.using(db).filter(customer_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
            data = Decimal(credit) - Decimal(debit)
            return JsonResponse(data, safe=False)
            
        except receivable.DoesNotExist: 
            
            return JsonResponse({'error': 'Customer not found'}, status=404)
    elif accountType == "Vendor":
        
        id = vendor_table.objects.using(db).get(id=cusID).custID
        try:
            credit = payable.objects.using(db).filter(vendor_id=id, type="Credit").aggregate(total=Sum('amount'))['total'] or 0.00
            debit = payable.objects.using(db).filter(vendor_id=id, type="Debit").aggregate(total=Sum('amount'))['total'] or 0.00
            data = Decimal(credit) - Decimal(debit)
            return JsonResponse(data, safe=False)
            
        except payable.DoesNotExist: 
            return JsonResponse({'error': 'Customer not found'}, status=404)
    else:
        return JsonResponse({'error': 'Customer not found'}, status=404)
        

def GetVendorDetails(request, id):
    db = request.user.company_id.db_name
    cusID = request.GET.get("venID")

    lookup = Q(id__iexact=cusID) | Q(custID__iexact=cusID)

    try:
       customer = vendor_table.objects.using(db).get(lookup)
       data = {
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'code': customer.custID,
            'company': customer.company_name,
            'address': customer.address,
        }
       return JsonResponse(data)
    except vendor_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required(login_url='/')
@urls_name(name="Returns Inwards")
def ViewReturnsInWards(request):
   
    return render(request, 'customer/ViewReturnsInWards.html')


@login_required(login_url='/')
@urls_name(name="Returns Inwards")
def ReturnInward(request):
    db = request.user.company_id.db_name
   
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    items = Item.objects.using(db).all()
    invoice_no = customer_invoice.objects.using(db).values("invoiceID").distinct().exclude(invoice_state="Cancelled")
    form = None 
    if request.method == 'POST':
        form = new_return_inwards(request, db)
    context = {
        'customers': customer,
        'vendors': vendor,
        'invoice_no': invoice_no,
        'items': items,
        'form': form,
    }
    
    return render(request, "customer/ReturnsInwards.html", context)

@login_required(login_url='/')
@urls_name(name="Returns Inwards")
def ViewCustomerReturnedItem(request, code, invoice):
    db = request.user.company_id.db_name
    if code:
        lookups = Q(id__iexact=code) | Q(customer_code__iexact=code)
   
        customer = customer_table.objects.using(db).filter(lookups).first()
    
        if customer is None:
            messages.error(request, "Customer with " + str(code) + " and "+ invoice +" does not exits")
            return redirect('customer:ViewReturnsInWards')
        else:
            invoice1 = customer_invoice.objects.using(db).filter(cusID=customer.pk, invoiceID=invoice).first()
            invoices = customer_invoice.objects.using(db).filter(cusID=customer.pk, invoiceID=invoice)
    context = { 
        "customer":customer,
        "invoice": invoice1,
        "invoices": invoices
        
    }    
    return render(request,"customer/ViewCustomerReturnedItem.html", context)


def ReturnedInwardChangeDate(request):
    db = request.user.company_id.db_name
    code = request.GET.get('cusID')
    invoiceID = request.GET.get('invoiceID')
    try:
        lookups = Q(id__iexact=code) | Q(customer_code__iexact=code)
   
        customer = customer_table.objects.using(db).get(lookups)
    
        invoice = customer_invoice.objects.using(db).filter(cusID=customer.pk, invoiceID=invoiceID).values().first()
      
        # serialized_data = list(invoice)
        data = {
            'customer': {
                'company': customer.company_name,
                'phone': customer.phone,
                'email': customer.email,
                'code': customer.customer_code,
                'address': customer.address,
                'balance': customer.Balance,
            },
            'invoice': invoice,
        }  
        return JsonResponse(data)
        
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    

def ChangeReturnInwardDate(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        invoice_id = request.POST['invoice_id']
        invoice_date = request.POST['invoice_date']
        new_date = request.POST['new_date']
       
        if new_date:

           invoice = customer_invoice.objects.using(db).filter(invoice_date=invoice_date, invoiceID=invoice_id)
           invoice.update(invoice_date=new_date) 
       

        #    messages.success(request, "Invoice date updated successfully")
           return JsonResponse(new_date, safe=False)
        else:
            return JsonResponse(new_date, safe=False) 


def get_customer_or_vendor(db, invoiceID):
    invoice = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
   
    if customer_table.objects.using(db).filter(customer_code=invoice.cusID):
        return "Customer"
    elif vendor_table.objects.using(db).filter(custID=invoice.cusID):
        return "Vendor"
    else:
        return "None"

def GetInvoiceDetails(request, invoice_id):
    db = request.user.company_id.db_name
    invoiceID = request.GET.get('invoiceId')
    
    try:
        # Fetch all fields related to the given invoice_id
        data = customer_invoice.objects.using(db).filter(invoiceID=invoiceID).values()
        
        
        

        accountType = get_customer_or_vendor(db, invoiceID)
        
        try:
            vat = Vat.objects.using(db).get(source=invoice_id).amount
        except Vat.DoesNotExist:
            vat = None

        serialized_data = {
            'invoice':list(data),
            'accountType':accountType,
            'vat': vat
        }

        return JsonResponse(serialized_data,  safe=False)
    except customer_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
   
from Stock.models import Check_StockLevel_By
from Stock.functions.functionHub.functionHub import *

def CheckItemQty(request):
    db = request.user.company_id.db_name
    item_id = request.GET.get('item_id')
  
    try:
    #    stock_level = Check_StockLevel_By.objects.using(db).first().level
        stock_ = Check_StockLevel_By.objects.using(db).first() #.level or "NO"
      
        if stock_ is not None:
            stock_level = stock_.level
        else:
            stock_level = "NO"
    except Check_StockLevel_By.DoesNotExist:
        stock_level = "NO"

    state = Qty_State(db, item_id)
    

    if state:
        outlet = request.user.outlet
        filter_sales_conditions = Q(outlet=outlet) #& Q(item_code=item_id)
        if stock_level == "YES":    
            qty = get_grand_total_from_outlet_stockin(item_id, CreateOutletStockIn,  outlet, db, filter_sales_conditions)           
        else:  
            qty = get_grand_total_from_stock_log(item_id, CreateOutletStockInLog, CreateStockInLog,  outlet, db, filter_sales_conditions, filter_sales_conditions)
      
    else:
        qty = 100000
    
    return JsonResponse(qty, safe=False)

def Qty_State(db, item_code):
    state = Item.objects.using(db).get(generated_code=item_code).qty_state
    
    if state == "Quantify":
        return True
    else:
        return False
    # try:
    #    qty = CreateOutletStockIn.objects.using(db).filter(item_code=item_id).first().quantity or 0
       
    #    return JsonResponse(qty, safe=False)
    # except CreateOutletStockIn.DoesNotExist: 
    #     
    #     return JsonResponse({'error': 'Item not found'}, status=404)

def StockCheckItemQty(request):
    db = request.user.company_id.db_name
    item_id = request.GET.get('item_id')
    try:
       stock_level = Check_StockLevel_By.objects.using(db).first().level
    except Check_StockLevel_By.DoesNotExist:
        stock_level = "NO"

    outlet = request.user.outlet
    filter_sales_conditions = Q(outlet=outlet) #& Q(item_code=item_id)
    if stock_level == "YES":    
        qty = get_grand_total_from_outlet_stockin(item_id, CreateOutletStockIn,  outlet, db, filter_sales_conditions)           
    else:  
         qty = get_grand_total_from_stock_log(item_id, CreateOutletStockInLog, CreateStockInLog,  outlet, db, filter_sales_conditions, filter_sales_conditions)
   
    return JsonResponse(qty, safe=False)
    # try:
    #    qty = CreateStockIn.objects.using(db).filter(item_code=item_id).first().quantity or 0
    
    #    return JsonResponse(qty, safe=False)
    # except CreateOutletStockIn.DoesNotExist: 
    #     return JsonResponse({'error': 'Item not found'}, status=404)

@login_required(login_url='/')
@urls_name(name="Customer")
def VerifiedPayment(request):
    db = request.user.company_id.db_name
    payments = evidentPayment.objects.using(db).filter(state="Verified").all()

    

    context = {
        'payments': payments
    }
    return render(request, 'customer/VerifiedPayment.html', context)


@login_required(login_url='/')
@urls_name(name="Customer")
def VerifyPayment(request):
    db = request.user.company_id.db_name
    accounts = chart_of_account.objects.using(db).all()
    payments = evidentPayment.objects.using(db).filter(state="Pending").order_by("-created_at")

    

    context = {
        'accounts': accounts,
        'payments': payments
    }
    return render(request, 'customer/VerifyPayment.html', context)

def Verify(request):
    db = request.user.company_id.db_name   
    runfunction = verify_payment(request, db)

    if runfunction:
        return JsonResponse({'message': "Payment Verified "}, safe=False)
    else:
        return JsonResponse({'message': "Error Verifying Payment"}, status=404)


def CancelSales(request):
    db = request.user.company_id.db_name 
    invoice = request.POST.get("invoice")
    cusID = request.POST.get("cusID")

    try:
        inital_invioice = customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID).first()
        cancel_invioice = customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID)
        accountType = get_customer_or_vendor(db, invoice)

        for item in cancel_invioice:
            outlet= request.user.outlet
            if inital_invioice.invoice_state == "Supplied":
                # Increase outlet stockin returned quatity
                IncreaseOutletStockinItemQuantity(db, outlet, item.itemcode, item.qty)
                
                CreateOutletStockinLog(db, item.invoice_date, item.invoiceID, item.order_no, item.customer_name, " ", outlet, item.Gdescription, item.item_name, item.item_descriptions, item.qty, item.token_id, item.Userlogin,  item.itemcode, item.unit_p, "")

        account = chart_of_account.objects.using(db).get(account_bankname="Sales account").account_id
        if inital_invioice.amount_paid == inital_invioice.amount_expected:
            #Paid
            if accountType == "Customer":
                cus = customer_table.objects.using(db).filter(customer_code=cusID)
                CreditReceivable(request, db, cus, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
            
            elif accountType == "Vendor":
                ven = vendor_table.objects.using(db).filter(custID=cusID)
                CreditPayable(request, db, ven, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
            
        elif inital_invioice.amount_paid != 0 and inital_invioice.amount_paid < inital_invioice.amount_expected:
            #Partly paid
            if accountType == "Customer":
                cus = customer_table.objects.using(db).filter(customer_code=cusID)
                CreditReceivable(request, db, cus, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
            
            elif accountType == "Vendor":
                ven = vendor_table.objects.using(db).filter(custID=cusID)
                CreditPayable(request, db, ven, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", account, inital_invioice.amount_paid)
                    
        else:
            if accountType == "Customer":
                cus = customer_table.objects.using(db).filter(customer_code=cusID)
                debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Inward")
                CreditReceivable(request, db, cus, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", debtor_account.account_id, inital_invioice.amount_paid)
                CreateLog(db, debtor_account, inital_invioice.amount_expected)
            elif accountType == "Vendor":
                ven = vendor_table.objects.using(db).filter(custID=cusID)
                debtor_account = chart_of_account.objects.using(db).get(account_bankname="Return Outward")
                CreditPayable(request, db, ven, inital_invioice.invoice_date, inital_invioice.Gdescription, "Transfer", debtor_account.account_id, inital_invioice.amount_paid)
                CreateLog(db, debtor_account, inital_invioice.amount_expected)


        #update customer invoice
        customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID).update(invoiceID = invoice + "_cancelled", invoice_state = "Cancelled", cancellation_status = "1")
                        
        return JsonResponse(True, safe=False)
    except customer_invoice.DoesNotExist:
        return JsonResponse(False, safe=False)


def Edit_incoice(request):
    db = request.user.company_id.db_name 
    if request.method == "POST":
        form = edit(request, db)

    # Redirect to the current URL
    return redirect('customer:ReturnInward')

def supply_pending_invoice(request):
    db = request.user.company_id.db_name 
    invoice = request.POST.get("invoice")
    cusID = request.POST.get("cusID")

    try:
        invioice = customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=cusID, invoice_state='Pending')
       
        return JsonResponse(True, safe=False)
    except customer_invoice.DoesNotExist:
        return JsonResponse(False, safe=False)
    



def get_shipping_cost(request, itemcode, city):
    db = request.user.company_id.db_name
    if request.method == 'GET':
        qty = request.GET.get('qty')
        try:
           address = shipping_addr.objects.using("afrikbook_client").get(id=city)
           try:
              cost = addressShippingPrice.objects.using(db).get(generated_code=itemcode, city=address.city, country=address.country).cost
              data = cost * decimal.Decimal(qty)
           except addressShippingPrice.DoesNotExist:
               data = 0.00
        except shipping_addr.DoesNotExist:
            data = 0.00
     
    return JsonResponse({'data': data}, safe=False)
