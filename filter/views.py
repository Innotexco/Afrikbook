from django.shortcuts import render
from django.http import JsonResponse
from customer.models import customer_invoice, receivable, sales_order, sales_quote
from journal.models import new_journal_entry
from django.db.models import Sum, F, Q
import decimal
from Stock.models import Item
from .function.date import convertDate
from decimal import Decimal




def sales_report_filter_by_date(request):
    db = request.user.company_id.db_name
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    invoice = request.GET.get('invoice')
    invoice_state = request.GET.get('invoice_state')
    customer = request.GET.get('customer')
    item = request.GET.get('item')
    payment_method = request.GET.get('payment_method')

    # Ignore placeholder values from disabled select options
    if invoice_state in (None, '', 'Select state'):
        invoice_state = None
    if invoice in (None, '', 'Select Invoice'):
        invoice = None
    if customer in (None, '', 'Select Customer'):
        customer = None
    if item in (None, '', 'Select Item'):
        item = None
    if payment_method in (None, '', 'All payment methods'):
        payment_method = None

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

    if payment_method:
        filter_conditions &= Q(payment_method=payment_method)

    data = []
    sales_total = 0
    qty_total = 0
    if filter_conditions:
        qs = customer_invoice.objects.using(db).filter(filter_conditions)

        # Sort by payment method then date
        filtered_data = qs.order_by('payment_method', 'invoice_date', 'invoiceID').values(
            'cusID',
            'customer_name',
            'invoice_date',
            'invoiceID',
            'Gdescription',
            'amount_expected',
            'amount_paid',
            'qty',
            'Userlogin',
            'payment_method',
            'Cash',
            'Transfer',
            'Cheque',
            'POS',
            'Customer_account',
        )

        sales_total = qs.values('invoiceID').distinct().aggregate(total=Sum('amount_expected'))['total'] or 0
        qty_total = qs.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

        # Fallback payment methods from receivable (for older invoices with blank payment_method)
        invoice_ids = list(qs.values_list('invoiceID', flat=True).distinct())
        pm_from_recv = {}
        if invoice_ids:
            for row in receivable.objects.using(db).filter(token_id__in=invoice_ids).exclude(
                payment_method__isnull=True
            ).exclude(payment_method='').values('token_id', 'payment_method'):
                if row['token_id'] and row['token_id'] not in pm_from_recv:
                    pm_from_recv[row['token_id']] = row['payment_method']

        def resolve_payment_method(row):
            pm = (row.get('payment_method') or '').strip()
            if pm:
                return pm
            inv = row.get('invoiceID')
            if inv and inv in pm_from_recv:
                return pm_from_recv[inv]
            # Flag columns used by older save paths
            if str(row.get('Cash') or '0') not in ('0', '', 'None') and str(row.get('Transfer') or '0') not in ('0', '', 'None'):
                return 'Transfer and Cash'
            if str(row.get('Transfer') or '0') not in ('0', '', 'None'):
                return 'Transfer'
            if str(row.get('Cash') or '0') not in ('0', '', 'None'):
                return 'Cash'
            if str(row.get('Cheque') or '0') not in ('0', '', 'None'):
                return 'Cheque'
            if str(row.get('POS') or '0') not in ('0', '', 'None'):
                return 'POS'
            if str(row.get('Customer_account') or '0') not in ('0', '', 'None'):
                return 'Customer Balance'
            return ''

        seen = set()
        for row in filtered_data:
            inv = row.get('invoiceID')
            if inv in seen:
                continue
            seen.add(inv)
            inv_date = row.get('invoice_date')
            data.append({
                'cusID': row.get('cusID') or '',
                'customer_name': row.get('customer_name') or '',
                'invoice_date': inv_date.strftime('%Y-%m-%d %H:%M:%S') if inv_date else '',
                'invoiceID': inv or '',
                'Gdescription': row.get('Gdescription') or '',
                'amount_expected': str(row.get('amount_expected') or 0),
                'amount_paid': str(row.get('amount_paid') or 0),
                'qty': str(row.get('qty') or 0),
                'Userlogin': row.get('Userlogin') or '',
                'payment_method': resolve_payment_method(row),
            })

    return JsonResponse({
        'serializer_data': data,
        'sales_total': str(sales_total) if sales_total is not None else '0',
        'qty_total': str(qty_total) if qty_total is not None else '0',
    })


    
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
    end_date_str   = request.GET.get('end_date')
    customer       = request.GET.get('customer')

    filter_conditions = Q()

    if start_date_str and end_date_str:
        start_date, end_date = convertDate(start_date_str, end_date_str)
        filter_conditions &= Q(invoice_date__range=(start_date, end_date))

    if customer:
        filter_conditions &= Q(cusID=customer)

    # Base queryset — only invoices with outstanding balance
    base_qs = customer_invoice.objects.using(db).filter(
        Q(amount_paid__lt=F('amount_expected')) & filter_conditions
    )

    # ── Deduplicate by invoiceID at query level ───────────────────────────
    seen        = set()
    unique_data = []
    for item in base_qs.order_by('invoiceID', 'id'):
        if item.invoiceID not in seen:
            seen.add(item.invoiceID)
            unique_data.append({
                'invoice_date':    str(item.invoice_date) if item.invoice_date else '',
                'cusID':           item.cusID,
                'customer_name':   item.customer_name,
                'invoiceID':       item.invoiceID,
                'Gdescription':    item.Gdescription or '—',
                'amount_paid':     str(item.amount_paid),
                'amount_expected': str(item.amount_expected),
                'balance':         str(item.amount_expected - item.amount_paid),
            })

    # ── Totals — per unique invoice, not per line ─────────────────────────
    unique_invoices = base_qs.values('invoiceID').distinct()

    amount_total = customer_invoice.objects.using(db).filter(
        invoiceID__in=unique_invoices
    ).values('invoiceID').distinct().aggregate(
        total=Sum('amount_expected')
    )['total'] or Decimal('0.00')

    amount_paid_total = customer_invoice.objects.using(db).filter(
        invoiceID__in=unique_invoices
    ).values('invoiceID').distinct().aggregate(
        total=Sum('amount_paid')
    )['total'] or Decimal('0.00')

    total_outstanding = amount_total - amount_paid_total

    return JsonResponse({
        'serializer_data': unique_data,
        'total_amount':    str(total_outstanding),
    }, safe=False)





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
        if item['invoice_no'] not in [d['invoice_no'] for d in data]:
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



