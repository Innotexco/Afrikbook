from django.shortcuts import render
from django.http import JsonResponse
from customer.models import customer_invoice, receivable, sales_order, sales_quote
from journal.models import new_journal_entry
from django.db.models import Sum, F, Q
import decimal
from Stock.models import Item
from .function.date import convertDate
# Create your views here.




def sales_report_filter_by_date(request):
    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    invoice = request.GET.get('invoice')
    invoice_state = request.GET.get('invoice_state')
    customer = request.GET.get('customer')
    item = request.GET.get('item')
    
    
    # Combine all filter conditions with AND operator
    filter_conditions = Q()

    if start_date_str and end_date_str:
        

        filter_conditions &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))

    if invoice:
        filter_conditions &= Q(invoiceID=invoice)

    if invoice_state:
        filter_conditions &= Q(invoice_state=invoice_state)

    if customer:
        filter_conditions &= Q(cusID=customer)

    if item:
        filter_conditions &= Q(item_name=item)

    data = []
    if filter_conditions:
      
        # Perform filtering based on the date range
        filtered_data = customer_invoice.objects.using(db).filter(filter_conditions).values()
        
        sales_total = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total=Sum("amount_expected"))['total']
        qty_total = customer_invoice.objects.using(db).filter(filter_conditions).aggregate(total_qty=Sum("qty"))['total_qty']

        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)
       

    serializer_data = list(data)
    data = {
        'serializer_data': serializer_data,
        'sales_total':sales_total,
        'qty_total':qty_total
    }

    return JsonResponse(data)


    
def receivable_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    type = request.GET.get('type')
    customer = request.GET.get('customer')
    
    filter_conditions = Q()
    
    if start_date_str and end_date_str:
        pass
        filter_conditions &= Q(cur_datetime__date__range=(convertDate(start_date_str, end_date_str)))

    if type:
        if type == "Debit&Credit":
           filter_conditions &= Q(type="Debit") | Q(type="Credit")
        else:
           filter_conditions &= Q(type=type)
           
    if customer:
       
        filter_conditions &= Q(customer_id=customer)
    
    data = []
    if filter_conditions:   
        # Perform filtering based on the date range
        filtered_data = receivable.objects.using(db).filter(filter_conditions).values() 
        for item in filtered_data:
            if item not in  data:
                data.append(item)
            

    total_amount = receivable.objects.using(db).filter(filter_conditions).values().aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Calculate total amount where type is "Credit"
    credit_total = receivable.objects.using(db).filter(Q(type="Credit"), filter_conditions).aggregate(total_credit=Sum("amount"))['total_credit'] or 0
    
    # Calculate total amount where type is "debit"
    debit_total = receivable.objects.using(db).filter(Q(type="Debit"),  filter_conditions).aggregate(total_debit=Sum("amount"))['total_debit'] or 0
    
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


def aged_receivable_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    customer = request.GET.get('customer')
    
    filter_conditions = Q()
    
    if start_date_str and end_date_str:
        pass
        filter_conditions &= Q(cur_datetime__date__range=(convertDate(start_date_str, end_date_str)))

           
    if customer:
        filter_conditions &= Q(cusID=customer)
    
    data = []
    if filter_conditions:   
        # Perform filtering based on the date range
        filtered_data = customer_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values() 
        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)
                
    amount_total = customer_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0
    amount_paid_total = customer_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid'] or 0
        

    total_amount = amount_total - amount_paid_total #customer_invoice.objects.using(db).filter(Q(amount_paid__lt=F('amount_expected')) & filter_conditions).values().aggregate(total_amount=Sum('amount_paid'))['total_amount'] or 0

    

    serializer_data = list(data)

    response ={
        "serializer_data":serializer_data,
        "total_amount":total_amount,
    }
    return JsonResponse(response, safe=False)

def sales_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    

    # Perform filtering based on the date range
    filtered_data = customer_invoice.objects.using(db).filter(invoice_date__range=convertDate(start_date_str, end_date_str)).values().distinct()
    
    serializer_data = list(filtered_data)

    return JsonResponse(serializer_data, safe=False)


def aged_recievable_filter(request, value):
    db = request.user.company_id.db_name

    if value is not None:
        lookups = Q(type__iexact=value) | Q(customer_id__iexact=value) 
        
    # Perform filtering based on filter type
    filtered_data = receivable.objects.using(db).filter(lookups, amount__lt=F('initial_amount')).values()
    
    serializer_data = list(filtered_data)

    if value == 'Debit&Credit':
        serializer_data = list(receivable.objects.using(db).all().values())
        # Calculate total amount where type is "credit"
        credit_total = receivable.objects.using(db).filter(type="Credit", amount__lt=F('initial_amount')).aggregate(total_credit=Sum("amount"))['total_credit']
        # Calculate total amount where type is "debit"
        debit_total = receivable.objects.using(db).filter(type="Debit", amount__lt=F('initial_amount')).aggregate(total_debit=Sum("amount"))['total_debit']
        amount_total = receivable.objects.using(db).all().aggregate(total_amount=Sum("amount"))['total_amount']
        # balance = debit_total - credit_total
       
    elif value == 'Credit':
        # Calculate total amount where type is "credit"
        credit_total = receivable.objects.using(db).filter(lookups, amount__lt=F('initial_amount')).aggregate(total_credit=Sum("amount"))['total_credit']
        debit_total = '0.00'
        amount_total = receivable.objects.using(db).filter(lookups, amount__lt=F('initial_amount')).aggregate(total_amount=Sum("amount"))['total_amount']
    elif value == 'Debit':
        # Calculate total amount where type is "debit"
        debit_total = receivable.objects.using(db).filter(lookups).aggregate(total_debit=Sum("amount"))['total_debit']
        credit_total = '0.00'
        amount_total = receivable.objects.using(db).filter(lookups, amount__lt=F('initial_amount')).aggregate(total_amount=Sum("amount"))['total_amount']

    elif receivable.objects.using(db).filter(customer_id=value).exists():
        
        # Calculate total amount where type is "credit"
        credit_total = receivable.objects.using(db).filter(type="Credit",customer_id=value, amount__lt=F('initial_amount')).aggregate(total_credit=Sum("amount"))['total_credit']
        # Calculate total amount where type is "debit"
        debit_total = receivable.objects.using(db).filter(type="Debit",customer_id=value, amount__lt=F('initial_amount')).aggregate(total_debit=Sum("amount"))['total_debit']
        amount_total = receivable.objects.using(db).filter(customer_id=value, amount__lt=F('initial_amount')).aggregate(total_amount=Sum("amount"))['total_amount']

        if credit_total is None:
            credit_total = '0.00'
        if debit_total is None:
            debit_total = '0.00'
        if amount_total is None:
            amount_total = '0.00'
    elif not receivable.objects.using(db).filter(customer_id=value).exists():    
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

def profit_loss_filter_by_date(request):
    db = request.user.company_id.db_name 

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

   

    sales_total = customer_invoice.objects.using(db).filter(invoice_date__range=(convertDate(start_date_str, end_date_str))).values("invoiceID").distinct().count()
    sales_return = customer_invoice.objects.using(db).filter(invoice_date__range=(convertDate(start_date_str, end_date_str)), invoice_state="Cancelled").values("invoiceID").distinct().count()
    goods_sold = customer_invoice.objects.using(db).filter(invoice_date__range=(convertDate(start_date_str, end_date_str)), invoice_state="Supplied").values("invoiceID").aggregate(total_goods_sold=Sum("amount_paid"))['total_goods_sold']

   
    data = {
        'sales_total':sales_total,
        'sales_return':sales_return,
        'goods_sold':goods_sold
    }

    return JsonResponse(data)

def customers_ledger_filter_by_date(request):
    db = request.user.company_id.db_name 
   
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    filter_conditions = Q()
    
    if start_date_str and end_date_str:
        filter_conditions  &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))


    data = []
    if filter_conditions:
        filtered_data =  customer_invoice.objects.using(db).filter(filter_conditions).values()

        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)
       


    amount_tatal = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0
    amount_paid_tatal = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid'] or 0
   
    if amount_tatal and amount_paid_tatal:
       balance = amount_tatal - amount_paid_tatal
    else:
        amount_tatal = "0.00"
        amount_paid_tatal = "0.00"
        balance = "0.00"
 
    serializer_data = list(data)
    data = {'serializer_data':serializer_data, 'amount_total':amount_tatal,'amount_paid_total':amount_paid_tatal,'balance':balance}
    return JsonResponse(data)

def customer_ledger_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    cusID = request.GET.get('cusID')

    filter_conditions = Q(cusID=cusID)
    
    if start_date_str and end_date_str:
        filter_conditions  &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))


    
    if filter_conditions:
        filtered_data =  customer_invoice.objects.using(db).filter(filter_conditions).values()

    

    amount_tatal = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0
    amount_paid_tatal = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid'] or 0
   
    if amount_tatal and amount_paid_tatal:
       balance = amount_tatal - amount_paid_tatal
    else:
        amount_tatal = "0.00"
        amount_paid_tatal = "0.00"
        balance = "0.00"

    serializer_data = list(filtered_data)
    data = {'serializer_data':serializer_data, 'amount_total':amount_tatal,'amount_paid_total':amount_paid_tatal,'balance':balance}
    return JsonResponse(data)

def sales_ladger_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    customer = request.GET.get('customer')
    item = request.GET.get('item')
   
    # Combine all filter conditions with AND operator
    filter_conditions = Q()

    if start_date_str and end_date_str:
        

        filter_conditions &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))

    if item:
        filter_conditions &= Q(item_name=item)


    if customer:
        filter_conditions &= Q(cusID=customer)
    
    data = []
    if filter_conditions:
        # Perform filtering based on the date range
        filtered_data = customer_invoice.objects.using(db).filter(filter_conditions).values()
        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)
                
        
        amount_total = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0

    

   
    serializer_data = list(data)
    data = {
        'serializer_data': serializer_data,
        'amount_total':amount_total,
    }

    return JsonResponse(data)

def sales_order_filter_by_date(request):
    db = request.user.company_id.db_name
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')


    # Perform filtering based on the date range
    filtered_data = sales_order.objects.using(db).filter(order_date__range=(convertDate(start_date_str, end_date_str))).values()
    
    serializer_data = list(filtered_data)

    return JsonResponse(serializer_data, safe=False)

def sales_quote_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')


    # Perform filtering based on the date range
    filtered_data = sales_quote.objects.using(db).filter(quote_date__range=(convertDate(start_date_str, end_date_str))).values()
    
    serializer_data = list(filtered_data)

    return JsonResponse(serializer_data, safe=False)




def return_inwards_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    data = []
    filtered_data = customer_invoice.objects.using(db).filter(invoice_date__range=(convertDate(start_date_str, end_date_str)), invoice_state="Cancelled").values()
    for item in filtered_data:
        if item['invoiceID'] not in [d['invoiceID'] for d in data]:
            data.append(item)
   
    serializer_data = list(data)

    return JsonResponse(serializer_data, safe=False)

def journal_entry_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    data = []
    # Perform filtering based on the date range
    filtered_data = new_journal_entry.objects.using(db).filter(date__range=(convertDate(start_date_str, end_date_str))).values()
    for item in filtered_data:
        if item['invoiceID'] not in [d['invoiceID'] for d in data]:
            data.append(item)

   
    serializer_data = list(data)

    return JsonResponse(serializer_data, safe=False)








































# OLD FUNCTIONS
def sales_filter(request, value):
    db = request.user.company_id.db_name
 
    if value is not None:
        lookups = Q(invoiceID__iexact=value) | Q(cusID__iexact=value) | Q(item_name__iexact=value) | Q(invoice_state__iexact=value)
       
    amount_total = None
    # Perform filtering based on filter type
    if "Supplied"  in value:
        filtered_data = customer_invoice.objects.using(db).filter(lookups).values()  #[:1]
        
    elif "Pending"  in value:
        filtered_data = customer_invoice.objects.using(db).filter(lookups).values()  #[:1]
        
    elif "Cancelled"  in value:
        filtered_data = customer_invoice.objects.using(db).filter(lookups).values()  #[:1]

    elif Item.objects.using(db).filter(item_name=value).exists():
        filtered_data = customer_invoice.objects.using(db).filter(lookups, invoice_state="Supplied").values()  #[:1]
        
    else:
        filtered_data = customer_invoice.objects.using(db).filter(lookups, invoice_state="Supplied").values() [:1]
        
        amount_total = customer_invoice.objects.using(db).filter(lookups).values_list("amount_expected", flat=True).first()
       
    

    sales_total = customer_invoice.objects.using(db).filter(lookups).values("invoiceID").distinct().count()
    qty_total = customer_invoice.objects.using(db).filter(lookups).aggregate(total_qty=Sum("qty"))['total_qty']
    if amount_total is None:
         amount_total = customer_invoice.objects.using(db).filter(lookups, invoice_state="Supplied").aggregate(total_amount=Sum("amount_expected"))['total_amount']

   
    serializer_data = list(filtered_data)
    data = {
        'item': serializer_data,
        'sales_total':sales_total,
        'qty_total':qty_total,
        'amount_total':amount_total
    }

    return JsonResponse(data)

def recievable_filter(request, value): 
    db = request.user.company_id.db_name

    if value is not None:
        lookups = Q(type__iexact=value) | Q(customer_id__iexact=value) 
        
    # Perform filtering based on filter type
    filtered_data = receivable.objects.using(db).filter(lookups).values()
    
    serializer_data = list(filtered_data)

    if value == 'Debit&Credit':
        
        serializer_data = list(receivable.objects.using(db).all().values())
        
        # Calculate total amount where type is "credit"
        credit_total = receivable.objects.using(db).filter(type="Credit").aggregate(total_credit=Sum("amount"))['total_credit']
        
        # Calculate total amount where type is "debit"
        debit_total = receivable.objects.using(db).filter(type="Debit").aggregate(total_debit=Sum("amount"))['total_debit']
        
        amount_total = receivable.objects.using(db).all().aggregate(total_amount=Sum("amount"))['total_amount']
        # balance = debit_total - credit_total
       

        
    elif value == 'Credit':
        # Calculate total amount where type is "credit"
        credit_total = receivable.objects.using(db).filter(lookups).aggregate(total_credit=Sum("amount"))['total_credit']
        debit_total = '0.00'
        amount_total = receivable.objects.using(db).filter(lookups).aggregate(total_amount=Sum("amount"))['total_amount']
    elif value == 'Debit':
        # Calculate total amount where type is "debit"
        debit_total = receivable.objects.filter(lookups).aggregate(total_debit=Sum("amount"))['total_debit']
        credit_total = '0.00'
        amount_total = receivable.objects.using(db).filter(lookups).aggregate(total_amount=Sum("amount"))['total_amount']

    elif receivable.objects.using(db).filter(customer_id=value).exists():
        
        # Calculate total amount where type is "credit"
        credit_total = receivable.objects.using(db).filter(type="Credit",customer_id=value).aggregate(total_credit=Sum("amount"))['total_credit']
        # Calculate total amount where type is "debit"
        debit_total = receivable.objects.using(db).filter(type="Debit",customer_id=value).aggregate(total_debit=Sum("amount"))['total_debit']
        amount_total = receivable.objects.using(db).filter(customer_id=value).aggregate(total_amount=Sum("amount"))['total_amount']

    if credit_total is None:
        credit_total = '0.00'
    if debit_total is None:
        debit_total = '0.00'
    if amount_total is None:
        amount_total = '0.00'
    elif not receivable.objects.using(db).filter(customer_id=value).exists():
           
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



