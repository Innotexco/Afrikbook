from django.shortcuts import render
from django.http import JsonResponse
from customer.models import  sales_order, sales_quote, payable
from vendor.models import Vendor_invoice
from django.db.models import Sum, F, Q
import decimal
from Stock.models import Item
from .function.date import convertDate


# Create your views here.

def purchase_report_filter_by_date(request):

    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    supplier = request.GET.get('supplier')
    operator = request.GET.get('operator')
    item = request.GET.get('item')
    
    

    filter_conditions = Q()

    if start_date_str and end_date_str:
        filter_conditions &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))
    
    if supplier:
        filter_conditions &= Q(cusID=supplier)
        
    if operator:
        filter_conditions &= Q(Userlogin=operator)
        
    if item:
        filter_conditions &= Q(item_name=item)

    data = []
    if filter_conditions:
        # Perform filtering based on the date range
        filtered_data = Vendor_invoice.objects.using(db).filter(filter_conditions).values()
        
        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)

    
    serializer_data = list(data)

    return JsonResponse(serializer_data, safe=False)



def payables_filter_by_date(request):
    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    vendor = request.GET.get('vendor')
    
    filter_conditions = Q()
    
    if start_date_str and end_date_str:
        pass
        filter_conditions &= Q(cur_datetime__date__range=(convertDate(start_date_str, end_date_str)))

           
    if vendor:
        filter_conditions &= Q(vendor_id=vendor)
    
    data = []
    if filter_conditions:   
        # Perform filtering based on the date range
        filtered_data = payable.objects.using(db).filter(filter_conditions).values() 
        for item in filtered_data:
            if item not in  data:
                data.append(item)
            

    total_amount = payable.objects.using(db).filter(filter_conditions).values().aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Calculate total amount where type is "Credit"
    credit_total = payable.objects.using(db).filter(Q(type="Credit"), filter_conditions).aggregate(total_credit=Sum("amount"))['total_credit'] or 0
    
    # Calculate total amount where type is "debit"
    debit_total = payable.objects.using(db).filter(Q(type="Debit"),  filter_conditions).aggregate(total_debit=Sum("amount"))['total_debit'] or 0
    
    # if credit_total is None:
    #         credit_total = '0.00'
    # if debit_total is None:
    #     debit_total = '0.00'

    serializer_data = list(data)
   
    def calbalance():
        # if decimal.Decimal(debit_total) > decimal.Decimal(credit_total):
        #       return   decimal.Decimal(debit_total) - decimal.Decimal(credit_total)
        return decimal.Decimal(credit_total) - decimal.Decimal(debit_total)
    
    balance = calbalance()

    response ={
        "serializer_data":serializer_data,
        "total_amount":total_amount,
        'credit_total':credit_total,
        'debit_total':debit_total,
        'balance':balance,
    }
    return JsonResponse(response, safe=False)


def aged_payables_filter_by_date(request):
    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    vendor = request.GET.get('vendor')
    
    filter_conditions = Q()
    
    if start_date_str and end_date_str:
        pass
        filter_conditions &= Q(invoice_date__date__range=(convertDate(start_date_str, end_date_str)))

           
    if vendor:
        filter_conditions &= Q(cusID=vendor)
    
    data = []
    if filter_conditions:   
        # Perform filtering based on the date range
        filtered_data = Vendor_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values() 
        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)
            
            
    amount_total = Vendor_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0
    amount_paid_total = Vendor_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid'] or 0
        
    total_amount = amount_total - amount_paid_total #Vendor_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values().aggregate(total_amount=Sum('amount_paid'))['total_amount'] or 0

   

    serializer_data = list(data)


    response ={
        "serializer_data":serializer_data,
        "total_amount":total_amount,
        
    }
    return JsonResponse(response, safe=False)





def payables_filter(request, value): 
    db = request.user.company_id.db_name
    if value is not None:
        lookups = Q(type__iexact=value) | Q(vendor_id__iexact=value) 
        
    # Perform filtering based on filter type
    filtered_data = payable.objects.using(db).filter(lookups).values()
    
    serializer_data = list(filtered_data)

    if value == 'Debit&Credit':
        serializer_data = list(payable.objects.using(db).all().values())
        # Calculate total amount where type is "credit"
        credit_total = payable.objects.using(db).filter(type="Credit").aggregate(total_credit=Sum("amount"))['total_credit']
        # Calculate total amount where type is "debit"
        debit_total = payable.objects.using(db).filter(type="Debit").aggregate(total_debit=Sum("amount"))['total_debit']
        amount_total = payable.objects.using(db).all().aggregate(total_amount=Sum("amount"))['total_amount']
        # balance = debit_total - credit_total
       
    elif value == 'Credit':
        # Calculate total amount where type is "credit"
        credit_total = payable.objects.using(db).filter(lookups).aggregate(total_credit=Sum("amount"))['total_credit']
        debit_total = '0.00'
        amount_total = payable.objects.using(db).filter(lookups).aggregate(total_amount=Sum("amount"))['total_amount']
    elif value == 'Debit':
        # Calculate total amount where type is "debit"
        debit_total = payable.objects.using(db).filter(lookups).aggregate(total_debit=Sum("amount"))['total_debit']
        credit_total = '0.00'
        amount_total = payable.objects.using(db).filter(lookups).aggregate(total_amount=Sum("amount"))['total_amount']

    elif payable.objects.using(db).filter(vendor_id=value).exists():
        
        # Calculate total amount where type is "credit"
        credit_total = payable.objects.using(db).filter(type="Credit",vendor_id=value).aggregate(total_credit=Sum("amount"))['total_credit']
        # Calculate total amount where type is "debit"
        debit_total = payable.objects.using(db).filter(type="Debit",vendor_id=value).aggregate(total_debit=Sum("amount"))['total_debit']
        amount_total = payable.objects.using(db).filter(vendor_id=value).aggregate(total_amount=Sum("amount"))['total_amount']

    if credit_total is None:
        credit_total = '0.00'
    if debit_total is None:
        debit_total = '0.00'
    if amount_total is None:
        amount_total = '0.00'
    elif not payable.objects.using(db).filter(vendor_id=value).exists():    
        credit_total = '0.00'
        debit_total = '0.00'
        balance = '0.00'
        amount_total = '0.00'

    def cal_balance():
        if decimal.Decimal(debit_total) > decimal.Decimal(credit_total):
              return   decimal.Decimal(debit_total) - decimal.Decimal(credit_total)
        return decimal.Decimal(credit_total) - decimal.Decimal(debit_total)
    
    balance = cal_balance()
    data = {
        'item': serializer_data,
        'credit_total':credit_total,
        'debit_total':debit_total,
        'balance':balance,
        'amount_total':amount_total
    }

    return JsonResponse(data)

def aged_payables_filter(request, value):
    db = request.user.company_id.db_name 
    if value is not None:
        lookups = Q(type__iexact=value) | Q(vendor_id__iexact=value) 
        
    # Perform filtering based on filter type
    filtered_data = payable.objects.using(db).filter(lookups, amount__lt=F('initial_amount')).values()
    
    serializer_data = list(filtered_data)

    

    if payable.objects.using(db).filter(vendor_id=value, amount__lt=F('initial_amount')).exists():
        
        # Calculate total amount where type is "credit"
        credit_total = payable.objects.using(db).filter(type="Credit",vendor_id=value, amount__lt=F('initial_amount')).aggregate(total_credit=Sum("amount"))['total_credit']
        # Calculate total amount where type is "debit"
        debit_total = payable.objects.using(db).filter(type="Debit",vendor_id=value, amount__lt=F('initial_amount')).aggregate(total_debit=Sum("amount"))['total_debit']
        amount_total = payable.objects.using(db).filter(vendor_id=value, amount__lt=F('initial_amount')).aggregate(total_amount=Sum("amount"))['total_amount']

        if credit_total is None:
            credit_total = '0.00'
        if debit_total is None:
            debit_total = '0.00'
        if amount_total is None:
            amount_total = '0.00'
    elif not payable.objects.using(db).filter(vendor_id=value, amount__lt=F('initial_amount')).exists():    
        credit_total = '0.00'
        debit_total = '0.00'
        balance = '0.00'
        amount_total = '0.00'

    def calbalance():
        if decimal.Decimal(debit_total) > decimal.Decimal(credit_total):
              return   decimal.Decimal(debit_total) - decimal.Decimal(credit_total)
        return decimal.Decimal(credit_total) - decimal.Decimal(debit_total)
    
    balance = calbalance()
    data = {
        'item': serializer_data,
        'credit_total':credit_total,
        'debit_total':debit_total,
        'balance':balance,
        'amount_total':amount_total
    }

    return JsonResponse(data)

def purchase_ladger_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    vendor = request.GET.get('vendor')
    item = request.GET.get('item')

    filter_conditions = Q()

    filter_conditions = Q()

    if start_date_str and end_date_str:
        filter_conditions &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))
    
    if vendor:
        filter_conditions &= Q(cusID=vendor)
    
        
    if item:
        filter_conditions &= Q(item_name=item)

    
    data = []
    if filter_conditions:
        filtered_data = Vendor_invoice.objects.using(db).filter(filter_conditions).values()
        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)

        amount_total = Vendor_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0
        amount_paid_tatal = Vendor_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid'] or 0
        
    
   
    if amount_total and amount_paid_tatal:
       balance = amount_total - amount_paid_tatal
    else:
        amount_total = "0.00"
        amount_paid_tatal = "0.00"
        balance = "0.00"
   
    serializer_data = list(data)
    data = {
        'serializer_data': serializer_data,
        'amount_total':amount_total,
        'amount_paid_total':amount_paid_tatal,
        'balance':balance
    }

    return JsonResponse(data)
from datetime import datetime


def getdate(request):
    from_date = None
    to_date = None
    toDate = request.GET.get('start_date')
    fromDate = request.GET.get('end_date')
    if toDate and fromDate is not None:
        from_date = datetime.strptime(fromDate, '%Y-%m-%d').date()
        to_date = datetime.strptime(toDate, '%Y-%m-%d').date()
    return from_date, to_date

def vendors_ledger_filter_by_date(request):
    db = request.user.company_id.db_name

    # start_date_str = request.GET.get('start_date')
    # end_date_str = request.GET.get('end_date')
    start_date_str, end_date_str = getdate(request)
    # Perform filtering based on the date range
    filtered_data = Vendor_invoice.objects.using(db).filter(invoice_date__range=(start_date_str, end_date_str)).values()

    data = []

    for item in filtered_data:
        if item['invoiceID'] not in [d['invoiceID'] for d in data]:
            data.append(item)
  

    amount_tatal = Vendor_invoice.objects.using(db).filter(invoice_date__range=(start_date_str, end_date_str)).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount']
    amount_paid_tatal = Vendor_invoice.objects.using(db).filter(invoice_date__range=(start_date_str, end_date_str)).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid']
   
    if amount_tatal and amount_paid_tatal:
       balance = amount_tatal - amount_paid_tatal
    else:
        amount_tatal = "0.00"
        amount_paid_tatal = "0.00"
        balance = "0.00"
 
    serializer_data = list(data)
    data = {'serializer_data':serializer_data, 'amount_total':amount_tatal,'amount_paid_total':amount_paid_tatal,'balance':balance}
    return JsonResponse(data)

def vendor_ledger_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    cusID = request.GET.get('cusID')

    filter_conditions = Q(cusID=cusID)
    
    if start_date_str and end_date_str:
        filter_conditions &= Q(invoice_date__date__range=(convertDate(start_date_str, end_date_str)))
        
    if filter_conditions:
        # Perform filtering based on the date range
        filtered_data = Vendor_invoice.objects.using(db).filter(filter_conditions).values().distinct()
        

        amount_tatal = Vendor_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount']
        amount_paid_tatal = Vendor_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid']

    if amount_tatal and amount_paid_tatal:
       balance = amount_tatal - amount_paid_tatal
    else:
        amount_tatal = "0.00"
        amount_paid_tatal = "0.00"
        balance = "0.00"



    serializer_data = list(filtered_data)
    data = {'serializer_data':serializer_data, 'amount_total':amount_tatal,'amount_paid_total':amount_paid_tatal,'balance':balance}
    return JsonResponse(data)


def purchase_order_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')


    # Perform filtering based on the date range
    filtered_data = sales_order.objects.using(db).filter(order_date__range=convertDate(start_date_str, end_date_str)).values()
    
    serializer_data = list(filtered_data)

    return JsonResponse(serializer_data, safe=False)

def purchase_quote_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')


    # Perform filtering based on the date range
    filtered_data = sales_quote.objects.using(db).filter(quote_date__range=convertDate(start_date_str, end_date_str)).values()
    
    serializer_data = list(filtered_data)

    return JsonResponse(serializer_data, safe=False)





# OLD FUNCTION
def purchase_filter(request, value):
    db = request.user.company_id.db_name
    if value is not None:
        lookups = Q(invoiceID__iexact=value) | Q(cusID__iexact=value) | Q(item_name__iexact=value) #| Q(invoice_state__iexact=value)
       
    amount_total = None
    paid_total = None
    # Perform filtering based on filter type
    item = Item.objects.using(db).filter(item_name=value)
    if item.exists():
        filtered_data = Vendor_invoice.objects.using(db).filter(lookups).values()  #[:1]
        
    else:
        filtered_data = Vendor_invoice.objects.using(db).filter(lookups).values() [:1]
        
        paid_total = Vendor_invoice.objects.using(db).filter(lookups).values_list("amount_paid", flat=True).first()
        amount_total = Vendor_invoice.objects.using(db).filter(lookups).values_list("amount_expected", flat=True).first()
       
    

    sales_total = Vendor_invoice.objects.using(db).filter(lookups).values("invoiceID").distinct().count()
    qty_total = Vendor_invoice.objects.using(db).filter(lookups).aggregate(total_qty=Sum("qty"))['total_qty']
    if amount_total is None:
         amount_total = Vendor_invoice.objects.using(db).filter(lookups).aggregate(total_amount=Sum("amount_expected"))['total_amount']


         paid_total = Vendor_invoice.objects.using(db).filter(lookups).aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid']

   
    if amount_total and paid_total:
       balance = amount_total - paid_total
    else:
        amount_total = "0.00"
        paid_total = "0.00"
        balance = "0.00"
   
    serializer_data = list(filtered_data)
    data = {
        'item': serializer_data,
        'sales_total':sales_total,
        'qty_total':qty_total,
        'amount_total':amount_total,
        'amount_paid_total':paid_total,
        'balance':balance
    }

    return JsonResponse(data)