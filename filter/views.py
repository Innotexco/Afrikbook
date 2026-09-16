from django.shortcuts import render
from django.http import JsonResponse
from customer.models import customer_invoice, receivable, sales_order, sales_quote
from journal.models import new_journal_entry, loan_account
from journal.fuctions.loan_schedule import apply_loan_charges_to_receivables
from django.db.models import Sum, F, Q
import decimal
from Stock.models import Item
from .function.date import convertDate
from decimal import Decimal
from main.utils import paginate_queryset




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


    
def _empty_receivable_page():
    return {
        "serializer_data": [],
        "total_amount": 0,
        "credit_total": 0,
        "debit_total": 0,
        "opening_balance": 0,
        "balance": 0,
        "closing_balance": 0,
        "page": 1,
        "num_pages": 1,
        "count": 0,
        "start_index": 0,
        "end_index": 0,
        "has_previous": False,
        "has_next": False,
        "previous_page": None,
        "next_page": None,
    }


def receivable_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    tx_type = request.GET.get('type')
    customer = request.GET.get('customer')

    if tx_type in (None, '', 'Select type'):
        tx_type = None
    if customer in (None, '', 'Select Customer'):
        customer = None

    if not start_date_str or not end_date_str:
        return JsonResponse(_empty_receivable_page(), safe=False)

    start_date, end_date = convertDate(start_date_str, end_date_str)

    prior_qs = receivable.objects.using(db).filter(date__lt=start_date)
    period_qs = receivable.objects.using(db).filter(date__range=(start_date, end_date))
    if customer:
        prior_qs = prior_qs.filter(customer_id=customer)
        period_qs = period_qs.filter(customer_id=customer)

    prior_debit = prior_qs.filter(type="Debit").aggregate(total=Sum("amount"))["total"] or 0
    prior_credit = prior_qs.filter(type="Credit").aggregate(total=Sum("amount"))["total"] or 0
    opening_balance = decimal.Decimal(prior_debit) - decimal.Decimal(prior_credit)

    debit_total = period_qs.filter(type="Debit").aggregate(total_debit=Sum("amount"))["total_debit"] or 0
    credit_total = period_qs.filter(type="Credit").aggregate(total_credit=Sum("amount"))["total_credit"] or 0
    debit_total = decimal.Decimal(debit_total)
    credit_total = decimal.Decimal(credit_total)
    closing_balance = opening_balance + debit_total - credit_total

    table_qs = period_qs
    if tx_type and tx_type != "Debit&Credit":
        table_qs = table_qs.filter(type=tx_type)
    table_qs = table_qs.order_by('date', 'id')

    page_obj = paginate_queryset(request, table_qs)
    serializer_data = list(page_obj.object_list.values(
        'date', 'customer_name', 'description', 'customer_id',
        'transaction_id', 'type', 'amount', 'initial_amount', 'balance',
    ))

    return JsonResponse({
        "serializer_data": serializer_data,
        "total_amount": debit_total + credit_total,
        "credit_total": credit_total,
        "debit_total": debit_total,
        "opening_balance": opening_balance,
        "balance": closing_balance,
        "closing_balance": closing_balance,
        "page": page_obj.number,
        "num_pages": page_obj.paginator.num_pages,
        "count": page_obj.paginator.count,
        "start_index": page_obj.start_index() if page_obj.paginator.count else 0,
        "end_index": page_obj.end_index() if page_obj.paginator.count else 0,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
    }, safe=False)

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

    apply_loan_charges_to_receivables(db)

    # Base queryset — only invoices with outstanding balance
    base_qs = customer_invoice.objects.using(db).filter(
        Q(amount_paid__lt=F('amount_expected')) & filter_conditions
    )

    loan_id_by_ref = dict(
        loan_account.objects.using(db)
        .exclude(reference__isnull=True)
        .exclude(reference='')
        .values_list('reference', 'id')
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
                'loan_id':         loan_id_by_ref.get(item.invoiceID),
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

def compute_customer_ledger(entries_qs, start_date=None, end_date=None):
    """Build a customer AR ledger: Debit increases what is owed, Credit reduces it.

    Stored receivable.balance is not used — Debit rows store a customer running
    figure while Credit rows store the invoice remainder, so a true ledger
    balance is recomputed in date order.
    """
    opening_balance = decimal.Decimal('0.00')
    running = decimal.Decimal('0.00')
    entries = []

    for entry in entries_qs:
        amount = decimal.Decimal(str(entry.amount or 0))
        running += amount if entry.type == "Debit" else -amount

        if start_date and entry.date < start_date:
            opening_balance = running
            continue
        if end_date and entry.date > end_date:
            break

        entry.running_balance = running
        entries.append(entry)

    total_debit = sum(
        (decimal.Decimal(str(e.amount or 0)) for e in entries if e.type == "Debit"),
        decimal.Decimal('0.00'),
    )
    total_credit = sum(
        (decimal.Decimal(str(e.amount or 0)) for e in entries if e.type == "Credit"),
        decimal.Decimal('0.00'),
    )
    closing_balance = entries[-1].running_balance if entries else opening_balance

    return {
        'entries': entries,
        'opening_balance': opening_balance,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'closing_balance': closing_balance,
    }


def customers_ledger_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return JsonResponse({
            'serializer_data': [],
            'amount_total': '0.00',
            'amount_paid_total': '0.00',
            'balance': '0.00',
        })

    qs = customer_invoice.objects.using(db).filter(
        invoice_date__range=convertDate(start_date_str, end_date_str)
    ).order_by('invoiceID', 'id')

    unique_invoices = {}
    for item in qs:
        if item.invoiceID in unique_invoices:
            continue
        expected = decimal.Decimal(str(item.amount_expected or 0))
        paid = decimal.Decimal(str(item.amount_paid or 0))
        unique_invoices[item.invoiceID] = {
            'cusID': item.cusID,
            'customer_name': item.customer_name,
            'invoiceID': item.invoiceID,
            'amount_expected': expected,
            'amount_paid': paid,
            'balance': expected - paid,
        }

    customers = {}
    for inv in unique_invoices.values():
        key = inv['cusID']
        if key not in customers:
            customers[key] = {
                'cusID': inv['cusID'],
                'customer_name': inv['customer_name'],
                'invoiceID': inv['invoiceID'],
                'amount_expected': decimal.Decimal('0.00'),
                'amount_paid': decimal.Decimal('0.00'),
                'balance': decimal.Decimal('0.00'),
            }
        customers[key]['amount_expected'] += inv['amount_expected']
        customers[key]['amount_paid'] += inv['amount_paid']
        customers[key]['balance'] += inv['balance']

    rows = sorted(customers.values(), key=lambda row: (row['customer_name'] or '').lower())
    amount_total = sum((row['amount_expected'] for row in rows), decimal.Decimal('0.00'))
    amount_paid_total = sum((row['amount_paid'] for row in rows), decimal.Decimal('0.00'))
    balance = amount_total - amount_paid_total

    serializer_data = [
        {
            'cusID': row['cusID'],
            'customer_name': row['customer_name'],
            'invoiceID': row['invoiceID'],
            'amount_expected': str(row['amount_expected']),
            'amount_paid': str(row['amount_paid']),
            'balance': str(row['balance']),
        }
        for row in rows
    ]

    return JsonResponse({
        'serializer_data': serializer_data,
        'amount_total': str(amount_total),
        'amount_paid_total': str(amount_paid_total),
        'balance': str(balance),
    })

def customer_ledger_filter_by_date(request):
    db = request.user.company_id.db_name

    cusID = request.GET.get('cusID')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not cusID:
        return JsonResponse({"error": "Missing customer"}, status=400)

    start_date = convertDate(start_date_str, start_date_str)[0] if start_date_str else None
    end_date = convertDate(end_date_str, end_date_str)[0] if end_date_str else None

    entries_qs = receivable.objects.using(db).filter(
        customer_id__iexact=cusID
    ).order_by('date', 'id')

    ledger = compute_customer_ledger(entries_qs, start_date, end_date)

    serialized = [
        {
            "date": e.date.strftime('%Y-%m-%d') if hasattr(e.date, 'strftime') else str(e.date),
            "token_id": e.token_id,
            "description": e.description,
            "payment_method": e.payment_method,
            "type": e.type,
            "amount": str(e.amount),
            "balance": str(e.running_balance),
        }
        for e in ledger['entries']
    ]

    return JsonResponse({
        "entries": serialized,
        "opening_balance": str(ledger['opening_balance']),
        "total_debit": str(ledger['total_debit']),
        "total_credit": str(ledger['total_credit']),
        "closing_balance": str(ledger['closing_balance']),
    })

def sales_ladger_filter_by_date(request):
    db = request.user.company_id.db_name

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    customer = request.GET.get('customer')
    item = request.GET.get('item')
    invoice_id = request.GET.get('invoice_id')   

    filter_conditions = Q()

    if start_date_str and end_date_str:
        filter_conditions &= Q(invoice_date__range=(convertDate(start_date_str, end_date_str)))

    if item:
        filter_conditions &= Q(item_name=item)

    if customer:
        filter_conditions &= Q(cusID=customer)

    if invoice_id:                                  
        filter_conditions &= Q(invoiceID__icontains=invoice_id)

    data = []
    amount_total = 0   
    if filter_conditions:
        filtered_data = customer_invoice.objects.using(db).filter(filter_conditions).values()
        for item in filtered_data:
            if item['invoiceID'] not in [d['invoiceID'] for d in data]:
                data.append(item)

        amount_total = customer_invoice.objects.using(db).filter(filter_conditions).values("invoiceID").distinct().aggregate(total_amount=Sum("amount_expected"))['total_amount'] or 0

    serializer_data = list(data)
    data = {
        'serializer_data': serializer_data,
        'amount_total': amount_total,
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



