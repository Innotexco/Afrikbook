from customer.models import *  
import decimal, uuid
from decimal import Decimal
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog, CreateStockIn, CreateStockInLog
from django.db.models import Q
from django.db import transaction


def exclude_returned_or_cancelled_invoices(qs):
    """Drop return-inward and cancelled invoices from AR / sales lists."""
    return qs.exclude(
        Q(invoiceID__icontains='returned')
        | Q(cancellation_status='1')
        | Q(invoice_state__iexact='Cancelled')
        | Q(invoice_state__iexact='Returned')
    )



# def CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total):

#     # Generate a new transaction ID
#     transaction_id = uuid.uuid4()

#     if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
#         initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
#     else: 
#         initial_bal = decimal.Decimal(0.00)
    
#     if initial_bal > 0:
#         balance = decimal.Decimal(initial_bal) - decimal.Decimal(total)
#     else:
#         balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

#     create_receivable = receivable(
#         date=refund_date,
#         description= Gdescription,
#         type = "Credit",
#         amount = total, 
#         payment_method =p_method,
#         invoice_status ="Unused",
#         customer_id = cus.customer_code,
#         customer_name = cus.name,
#         initial_amount = initial_bal,
#         balance = balance,
#         account_posted = account, # default account
#         transaction_id = transaction_id,
#         Userlogin = request.user.username)
#     create_receivable.save(using=db)


# def DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total):

#     # Generate a new transaction ID
#     transaction_id = uuid.uuid4()

#     if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
#         initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
#     else: 
#         initial_bal = decimal.Decimal(0.00)
    
#     if initial_bal > 0:
#         balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)
#     else:
#         balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

#     create_receivable = receivable(
#         date=refund_date,
#         description= Gdescription,
#         type = "Debit",
#         amount = total, 
#         payment_method = p_method,
#         invoice_status ="Unused",
#         customer_id = cus.customer_code,
#         customer_name = cus.name,
#         initial_amount = initial_bal,
#         balance = balance,
#         account_posted = account, # default account
#         transaction_id = transaction_id,
#         Userlogin = request.user.username)
#     create_receivable.save(using=db)



def CreditPayable(request, db, ven, refund_date, Gdescription, p_method, account, total):

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    if payable.objects.using(db).filter(vendor_id=ven.custID).exists():
        initial_bal = payable.objects.using(db).filter(vendor_id=ven.custID).last().balance
    else: 
        initial_bal = decimal.Decimal(0.00)
    
    if initial_bal > 0:
        balance = decimal.Decimal(initial_bal) - decimal.Decimal(total)
    else:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

    create_payable = payable(
        date=refund_date,
        description= Gdescription,
        type = "Credit",
        amount = total, 
        payment_method =p_method,
        vendor_id = ven.custID,
        vendor_name = ven.name,
        initial_amount = initial_bal,
        balance = balance,
        account_posted = account, # default account
        transaction_id = transaction_id,
        Userlogin = request.user.username)
    create_payable.save(using=db)


def DebitPayable(request, db, ven, refund_date, Gdescription, p_method, account,  total):

    # Generate a new transaction ID
    transaction_id = uuid.uuid4()

    if payable.objects.using(db).filter(vendor_id=ven.custID).exists():
        initial_bal = payable.objects.using(db).filter(vendor_id=ven.custID).last().balance
    else: 
        initial_bal = decimal.Decimal(0.00)
    
    if initial_bal > 0:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)
    else:
        balance = decimal.Decimal(initial_bal) + decimal.Decimal(total)

    create_payable = payable(
        date=refund_date,
        description= Gdescription,
        type = "Debit",
        amount = total, 
        payment_method = p_method,
        vendor_id = ven.custID,
        vendor_name = ven.name,
        initial_amount = initial_bal,
        balance = balance,
        account_posted = account, # default account
        transaction_id = transaction_id,
        Userlogin = request.user.username)
    create_payable.save(using=db)
    
    

def _last_receivable_balance(db, customer_code):
    prior = (
        receivable.objects.using(db)
        .filter(customer_id=customer_code)
        .order_by('date', 'id')
        .last()
    )
    if prior is None:
        return Decimal('0.00')
    return Decimal(str(prior.balance or 0))


def DebitReceivable(request, db, cus, refund_date, Gdescription, p_method, account, total, invoiceID=None):
    transaction_id = uuid.uuid4()

    initial_bal = _last_receivable_balance(db, cus.customer_code)
    balance = initial_bal + Decimal(str(total))

    create_receivable = receivable(
        date           = refund_date,
        description    = Gdescription,
        type           = "Debit",
        amount         = total,
        payment_method = p_method,
        invoice_status = "Unused",
        customer_id    = cus.customer_code,
        customer_name  = cus.name,
        initial_amount = initial_bal,
        balance        = balance,
        account_posted = account,
        transaction_id = transaction_id,
        token_id       = invoiceID or "",
        Userlogin      = request.user.username,
    )
    create_receivable.save(using=db)


def CreditReceivable(request, db, cus, refund_date, Gdescription, p_method, account, amount_paid_now, invoiceID, invoice_total, current_paid_before):
    transaction_id = uuid.uuid4()

    initial_bal = _last_receivable_balance(db, cus.customer_code)
    balance = initial_bal - Decimal(str(amount_paid_now))

    create_receivable = receivable(
        date           = refund_date,
        description    = Gdescription,
        type           = "Credit",
        amount         = amount_paid_now,
        payment_method = p_method,
        invoice_status = "Unused",
        customer_id    = cus.customer_code,
        customer_name  = cus.name,
        initial_amount = initial_bal,
        balance        = balance,
        account_posted = account,
        transaction_id = transaction_id,
        token_id       = invoiceID,
        Userlogin      = request.user.username,
    )
    create_receivable.save(using=db)


PAYMENT_DEBIT_PREFIXES = ("Payment Received", "Discount Allowed")


def spurious_payment_debit_qs(db):
    """Debits posted at payment/discount time — they must not live on the AR ledger."""
    lookup = Q()
    for prefix in PAYMENT_DEBIT_PREFIXES:
        lookup |= Q(description__startswith=prefix)
    return receivable.objects.using(db).filter(type="Debit").filter(lookup)


def recompute_receivable_running_balances(db, customer_ids=None):
    """Rewrite each remaining row's initial_amount/balance from a Debit+/Credit- walk."""
    if customer_ids is None:
        customer_ids = (
            receivable.objects.using(db)
            .values_list('customer_id', flat=True)
            .distinct()
        )

    updated = 0
    for customer_id in customer_ids:
        rows = list(
            receivable.objects.using(db)
            .filter(customer_id=customer_id)
            .order_by('date', 'id')
        )
        running = Decimal('0.00')
        for row in rows:
            amount = Decimal(str(row.amount or 0))
            initial = running
            if row.type == "Debit":
                running += amount
            else:
                running -= amount
            if row.initial_amount != initial or row.balance != running:
                row.initial_amount = initial
                row.balance = running
                row.save(using=db, update_fields=['initial_amount', 'balance'])
                updated += 1
    return updated


def repair_spurious_payment_debits(db, dry_run=False):
    """One-time repair: drop payment-echo Debits, then recompute every customer's running balance.

    Matching is description-based only (Payment Received / Discount Allowed Debits).
    Credits are kept. Does not run from a GET view.
    """
    junk = spurious_payment_debit_qs(db).order_by('date', 'id')
    preview = list(junk.values(
        'id', 'date', 'customer_id', 'customer_name', 'token_id',
        'description', 'amount', 'balance',
    ))
    delete_count = len(preview)

    if dry_run:
        return {
            'deleted': 0,
            'would_delete': delete_count,
            'recomputed': 0,
            'rows': preview,
        }

    with transaction.atomic(using=db):
        if delete_count:
            junk.delete()
        recomputed = recompute_receivable_running_balances(db)

    return {
        'deleted': delete_count,
        'would_delete': delete_count,
        'recomputed': recomputed,
        'rows': preview,
    }


def _d(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'))


def _sum_amounts(rows):
    total = Decimal('0.00')
    for row in rows:
        total += _d(row.amount)
    return total


def _is_later_credit(row):
    desc = row.description or ''
    return row.type == 'Credit' and desc.startswith(PAYMENT_DEBIT_PREFIXES)


def _invoice_date(value):
    if value is None:
        return None
    if hasattr(value, 'date'):
        return value.date()
    return value


def _reduce_rows_to(rows, target, db, dry_run):
    """Cut newest rows first so their amounts sum to target. Returns (rows, actions)."""
    actions = []
    current = _sum_amounts(rows)
    excess = current - target
    if excess <= 0:
        return rows, actions

    kept = list(rows)
    for row in sorted(rows, key=lambda r: r.id, reverse=True):
        if excess <= 0:
            break
        amount = _d(row.amount)
        if amount <= excess:
            actions.append({
                'op': 'delete',
                'id': row.id,
                'type': row.type,
                'amount': str(amount),
                'description': row.description or '',
            })
            if not dry_run:
                row.delete(using=db)
            kept = [r for r in kept if r.id != row.id]
            excess -= amount
        else:
            new_amount = amount - excess
            actions.append({
                'op': 'update',
                'id': row.id,
                'type': row.type,
                'from': str(amount),
                'to': str(new_amount),
                'description': row.description or '',
            })
            if not dry_run:
                row.amount = new_amount
                row.save(using=db, update_fields=['amount'])
            row.amount = new_amount
            excess = Decimal('0.00')
    return kept, actions


def _raise_rows_to(rows, target, db, dry_run, create_defaults):
    """Increase the oldest row, or create one, so amounts sum to target. Returns (rows, actions)."""
    actions = []
    current = _sum_amounts(rows)
    if current >= target:
        return rows, actions

    delta = target - current
    if rows:
        row = sorted(rows, key=lambda r: r.id)[0]
        new_amount = _d(row.amount) + delta
        actions.append({
            'op': 'update',
            'id': row.id,
            'type': row.type,
            'from': str(_d(row.amount)),
            'to': str(new_amount),
            'description': row.description or '',
        })
        if not dry_run:
            row.amount = new_amount
            row.save(using=db, update_fields=['amount'])
        row.amount = new_amount
    else:
        payload = dict(create_defaults)
        payload['amount'] = delta
        actions.append({
            'op': 'create',
            'type': payload.get('type'),
            'amount': str(delta),
            'description': payload.get('description') or '',
            'token_id': payload.get('token_id'),
        })
        if not dry_run:
            created = receivable(**payload)
            created.save(using=db)
            rows = [created]
    return rows, actions


def _set_rows_total(rows, target, db, dry_run, create_defaults):
    if target < 0:
        target = Decimal('0.00')
    current = _sum_amounts(rows)
    actions = []
    if current > target:
        rows, actions = _reduce_rows_to(rows, target, db, dry_run)
    elif current < target:
        rows, actions = _raise_rows_to(rows, target, db, dry_run, create_defaults)
    return rows, actions


def invoice_ar_net(db, token_ids):
    """Debits minus credits for the given receivable token_ids."""
    tokens = [t for t in token_ids if t]
    if not tokens:
        return Decimal('0.00')
    net = Decimal('0.00')
    for row in receivable.objects.using(db).filter(token_id__in=tokens):
        amount = _d(row.amount)
        if (row.type or '').lower() == 'debit':
            net += amount
        else:
            net -= amount
    return net


def reverse_invoice_ar(request, db, cus, entry_date, description, p_method, account, token_ids, posting_token_id):
    """Post one AR Debit or Credit so the listed invoice tokens net to zero.

    Used on return inward: a returned invoice must not change customer AR,
    matching Customer Ledger which excludes cancelled/returned invoices.
    """
    net = invoice_ar_net(db, token_ids)
    if net > 0:
        CreditReceivable(
            request, db, cus, entry_date, description, p_method, account,
            net, posting_token_id, net, Decimal('0.00'),
        )
    elif net < 0:
        DebitReceivable(
            request, db, cus, entry_date, description, p_method, account,
            -net, invoiceID=posting_token_id,
        )
    return net


def _returned_invoice_tokens(invoice_id):
    invoice_id = str(invoice_id or '')
    orig = invoice_id[:-9] if invoice_id.endswith('_returned') else invoice_id
    returned = orig + '_returned' if orig else invoice_id
    tokens = []
    for token in (orig, returned, invoice_id):
        if token and token not in tokens:
            tokens.append(token)
    return orig, returned, tokens


def repair_returned_invoice_receivables(db, dry_run=False):
    """Zero AR for cancelled/returned invoices so they drop out of customer AR.

    Customer Ledger lists only open invoices. Receivables was still carrying
    leftover sale debits (unpaid returns) or extra return credits (paid returns).
    """
    returned_invoices = (
        customer_invoice.objects.using(db)
        .filter(
            Q(invoiceID__icontains='returned')
            | Q(cancellation_status='1')
            | Q(invoice_state__iexact='Cancelled')
            | Q(invoice_state__iexact='Returned')
        )
        .order_by('invoiceID', 'id')
        .values(
            'id', 'invoiceID', 'cusID', 'customer_name', 'invoice_date',
            'Gdescription', 'payment_method',
        )
    )

    grouped = {}
    for line in returned_invoices:
        orig, returned, _tokens = _returned_invoice_tokens(line['invoiceID'])
        grouped.setdefault(orig or line['invoiceID'], []).append(line)

    reports = []
    affected_customers = set()

    def _apply():
        for orig_id, lines in grouped.items():
            first = lines[0]
            orig, returned, tokens = _returned_invoice_tokens(first['invoiceID'])
            net_before = invoice_ar_net(db, tokens)
            if net_before == 0:
                continue

            customer_code = first.get('cusID') or ''
            customer_name = first.get('customer_name') or ''
            if not customer_code:
                ar_row = receivable.objects.using(db).filter(token_id__in=tokens).order_by('id').first()
                if ar_row:
                    customer_code = ar_row.customer_id
                    customer_name = customer_name or ar_row.customer_name

            posting_token = returned or orig_id
            description = f"Return Inward - Invoice {orig or orig_id}"
            entry_date = _invoice_date(first.get('invoice_date'))
            payment_method = first.get('payment_method') or 'Cash'
            ar_row = receivable.objects.using(db).filter(token_id__in=tokens).order_by('id').first()
            account_posted = (ar_row.account_posted if ar_row and ar_row.account_posted else '') or '4001-Sales'

            if net_before > 0:
                typ, amount = 'Credit', net_before
            else:
                typ, amount = 'Debit', -net_before

            actions = [{
                'op': 'create',
                'type': typ,
                'amount': str(amount),
                'token_id': posting_token,
                'description': description,
            }]
            if not dry_run:
                if orig and orig != posting_token:
                    receivable.objects.using(db).filter(token_id=orig).update(token_id=posting_token)
                receivable.objects.using(db).create(
                    date=entry_date,
                    description=description,
                    type=typ,
                    amount=amount,
                    payment_method=payment_method,
                    invoice_status='Unused',
                    customer_id=customer_code,
                    customer_name=customer_name or '',
                    initial_amount=Decimal('0.00'),
                    balance=Decimal('0.00'),
                    account_posted=account_posted,
                    transaction_id=str(uuid.uuid4()),
                    token_id=posting_token,
                    Userlogin='repair',
                )

            if customer_code:
                affected_customers.add(customer_code)

            reports.append({
                'invoiceID': orig or orig_id,
                'customer_id': customer_code,
                'customer_name': customer_name,
                'net_before': str(net_before),
                'net_after': '0.00',
                'actions': actions,
            })

        recomputed = 0
        if not dry_run and affected_customers:
            recomputed = recompute_receivable_running_balances(db, affected_customers)
        return recomputed

    if dry_run:
        recomputed = _apply()
    else:
        with transaction.atomic(using=db):
            recomputed = _apply()

    return {
        'changed': len(reports),
        'recomputed': recomputed,
        'invoices': reports,
    }


def repair_receivable_invoice_alignment(db, dry_run=False):
    """Make AR debit/credit totals match invoice.amount_expected / amount_paid.

    Trusts the invoice as the collection record:
      sale debit  = amount_expected
      all credits = amount_paid
    Later "Payment Received" / "Discount Allowed" credits are kept; the original
    sale credit is rewritten so the pieces add up. Extra sale debits are trimmed.
    """
    # .values() avoids columns some older tenant DBs do not have yet (e.g. payment_account).
    invoices = (
        customer_invoice.objects.using(db)
        .exclude(invoiceID__icontains='returned')
        .exclude(cancellation_status='1')
        .exclude(invoice_state='Cancelled')
        .order_by('invoiceID', 'id')
        .values(
            'id', 'invoiceID', 'cusID', 'customer_name', 'amount_paid',
            'amount_expected', 'invoice_date', 'Gdescription', 'payment_method',
        )
    )

    grouped = {}
    for line in invoices:
        grouped.setdefault(line['invoiceID'], []).append(line)

    reports = []
    affected_customers = set()

    def _apply():
        for invoice_id, lines in grouped.items():
            expected = _d(lines[0]['amount_expected'])
            paid = max(_d(line['amount_paid']) for line in lines)
            first = lines[0]

            ar_rows = list(
                receivable.objects.using(db)
                .filter(token_id=invoice_id)
                .order_by('id')
            )
            debits = [r for r in ar_rows if r.type == 'Debit']
            later_credits = [r for r in ar_rows if _is_later_credit(r)]
            sale_credits = [
                r for r in ar_rows
                if r.type == 'Credit' and not _is_later_credit(r)
            ]

            later_sum = _sum_amounts(later_credits)
            debit_before = _sum_amounts(debits)
            credit_before = later_sum + _sum_amounts(sale_credits)

            target_later = later_sum if later_sum <= paid else paid
            target_sale_credit = paid - target_later

            customer_code = first.get('cusID') or (ar_rows[0].customer_id if ar_rows else '')
            customer_name = first.get('customer_name') or (ar_rows[0].customer_name if ar_rows else '')
            payment_method = first.get('payment_method') or 'Cash'
            account_posted = (
                (ar_rows[0].account_posted if ar_rows and ar_rows[0].account_posted else '')
                or '4001-Sales'
            )
            inv_date = _invoice_date(first.get('invoice_date'))
            description = first.get('Gdescription') or ''

            create_debit = dict(
                date=inv_date,
                description=description,
                type='Debit',
                payment_method=payment_method,
                invoice_status='Unused',
                customer_id=customer_code,
                customer_name=customer_name or '',
                initial_amount=Decimal('0.00'),
                balance=Decimal('0.00'),
                account_posted=account_posted,
                transaction_id=str(uuid.uuid4()),
                token_id=invoice_id,
                Userlogin='repair',
            )
            create_credit = dict(create_debit)
            create_credit['type'] = 'Credit'
            create_credit['transaction_id'] = str(uuid.uuid4())

            actions = []
            later_credits, later_actions = _set_rows_total(
                later_credits, target_later, db, dry_run, create_credit
            )
            actions.extend(later_actions)
            sale_credits, sale_actions = _set_rows_total(
                sale_credits, target_sale_credit, db, dry_run, create_credit
            )
            actions.extend(sale_actions)
            debits, debit_actions = _set_rows_total(
                debits, expected, db, dry_run, create_debit
            )
            actions.extend(debit_actions)

            lines_need_sync = any(_d(line['amount_paid']) != paid for line in lines)
            if lines_need_sync:
                actions.append({
                    'op': 'sync_lines',
                    'invoiceID': invoice_id,
                    'to': str(paid),
                    'line_count': len(lines),
                })
                if not dry_run:
                    customer_invoice.objects.using(db).filter(invoiceID=invoice_id).update(amount_paid=paid)

            debit_after = expected
            credit_after = paid
            changed = bool(actions) or debit_before != debit_after or credit_before != credit_after
            if not changed:
                continue

            if customer_code:
                affected_customers.add(customer_code)

            reports.append({
                'invoiceID': invoice_id,
                'customer_id': customer_code,
                'customer_name': customer_name,
                'expected': str(expected),
                'paid': str(paid),
                'ar_debit_before': str(debit_before),
                'ar_credit_before': str(credit_before),
                'ar_debit_after': str(debit_after),
                'ar_credit_after': str(credit_after),
                'actions': actions,
            })

        recomputed = 0
        if not dry_run:
            recomputed = recompute_receivable_running_balances(db, affected_customers or None)
        return recomputed

    if dry_run:
        recomputed = _apply()
    else:
        with transaction.atomic(using=db):
            recomputed = _apply()

    return {
        'changed': len(reports),
        'recomputed': recomputed,
        'invoices': reports,
    }


def ReduceOutletStockinItemQuantity(db, outlet, itemcode, qty):
   
    stock = CreateOutletStockIn.objects.using(db).filter(outlet=outlet, item_code=itemcode).first()
    
    if stock is None:
        try:
            stock = CreateOutletStockIn.objects.using(db).get(item_code=itemcode).first()
            new_qty = decimal.Decimal(stock.quantity) -  decimal.Decimal(qty)
            stock.quantity = new_qty
            stock.save()
        except CreateOutletStockIn.DoesNotExist:
               pass
    else:
        new_qty = decimal.Decimal(stock.quantity) -  decimal.Decimal(qty)
        stock.quantity = new_qty
        stock.save()

    # StockinStatus(db, itemcode, qty)
    # CreatOutletStockinLog(stock, new_qty)


def CreateOutletStockinLog(db, datetx, invoice_no, order_no, supplier, warehouse, outlet, description, item, item_decription, item_qty, token_id, Userlogin, item_code, selling_price, wholesale_price):
    # Generate refrence number
    ref_no = "REF"+generate_order_id()
    
    CreateOutletStockInLog.objects.using(db).create(
                    datetx = datetx,
                    invoice_no = invoice_no,	
                    order_no = order_no,	
                    supplier = supplier,
                    warehouse = warehouse,
                    outlet = outlet,	
                    description = description,	
                    item = item,	
                    item_decription =item_decription,
                    quantity = item_qty,
                    token_id = token_id,	
                    Userlogin = Userlogin,	
                    item_code = item_code,	
                    ref_no = ref_no,	
                    selling_price = selling_price,
                    wholesale_price = wholesale_price,
                )
    

def StockinStatus(db,  itemcode, qty):
    items = CreateStockInLog.objects.using(db).filter(item_code=itemcode).order_by('id').exclude(status="Sold")[:qty]
    # CreateStockInLog.objects.using(db).filter(invoice_no=invoice_no, item_code=item_code).update(notification_status=status)

    items.update(status="Sold")



def IncreaseOutletStockinItemQuantity(db, outlet, itemcode, qty):
    stock = CreateOutletStockIn.objects.using(db).get(outlet=outlet, item_code=itemcode)
    new_qty = decimal.Decimal(stock.quantity) +  decimal.Decimal(qty)
    stock.quantity = new_qty
    stock.save()


def ReduceStockinItemQuantity(db, outlet, itemcode, qty):
    lookups = Q(outlet=outlet) | Q(warehouse=outlet)
    stock = CreateStockIn.objects.using(db).filter(lookups, item_code=itemcode).first()
    if stock is None:
        raise CreateStockIn.DoesNotExist(
            f"No CreateStockIn row found for warehouse/outlet={outlet}, item_code={itemcode}"
        )
    new_qty = decimal.Decimal(stock.quantity) - decimal.Decimal(str(qty))
    stock.quantity = new_qty
    stock.save(using=db)
    
from django.apps import apps
    
def CreateLog(db, account, total):
    model_name = account.series_name.title()+"_account"

     # Get the model dynamically
    AccountModel = apps.get_model(app_label='account', model_name=model_name)
    
 
    
    AccountModel.objects.using(db).create(
        account_id          = account.account_id,
        series_name         = account.series_name,
        account_bankname    = account.account_bankname,
        account_type        = account.account_type,
        amount              = total    
    )