from customer.models import *  
import decimal, uuid
from decimal import Decimal
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog, CreateStockIn, CreateStockInLog
from django.db.models import Q, F
from django.db import connections, transaction


def exclude_returned_or_cancelled_invoices(qs):
    """Drop return-inward and cancelled invoices from AR / sales lists."""
    return qs.exclude(
        Q(invoiceID__icontains='returned')
        | Q(cancellation_status='1')
        | Q(invoice_state__iexact='Cancelled')
        | Q(invoice_state__iexact='Returned')
    )


def returned_or_cancelled_invoice_tokens(db, customer_id=None):
    """Original and *_returned invoice IDs that Customer Ledger must hide."""
    inv_qs = customer_invoice.objects.using(db).filter(
        Q(invoiceID__icontains='returned')
        | Q(cancellation_status='1')
        | Q(invoice_state__iexact='Cancelled')
        | Q(invoice_state__iexact='Returned')
    )
    if customer_id:
        inv_qs = inv_qs.filter(cusID__iexact=customer_id)

    tokens = set()
    for invoice_id in inv_qs.values_list('invoiceID', flat=True):
        _orig, _returned, pair = _returned_invoice_tokens(invoice_id)
        tokens.update(pair)
    return tokens


def exclude_returned_or_cancelled_receivables(qs, db, customer_id=None):
    """Drop AR rows that belong to returned or cancelled invoices.

    Customer Ledger lists open invoices only. The detail statement must omit
    the matching receivable history (retagged *_returned tokens, original
    tokens still sitting on a cancelled invoice, and Return Inward reversing
    rows) so those invoices do not appear or change opening/closing.
    """
    filtered = qs.exclude(token_id__icontains='returned').exclude(
        description__icontains='Return Inward'
    )
    tokens = returned_or_cancelled_invoice_tokens(db, customer_id)
    if tokens:
        filtered = filtered.exclude(token_id__in=list(tokens))
    return filtered


def customer_ledger_entries_qs(db, customer_id):
    """Receivable rows for one customer, excluding returned/cancelled invoices."""
    qs = receivable.objects.using(db).filter(customer_id__iexact=customer_id)
    return exclude_returned_or_cancelled_receivables(
        qs, db, customer_id
    ).order_by('date', 'id')



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
AGED_PAYMENT_PREFIXES = PAYMENT_DEBIT_PREFIXES
CANCELLED_PAYMENT_MARK = " [cancelled]"


def spurious_payment_debit_qs(db):
    """Debits posted at payment/discount time — they must not live on the AR ledger."""
    lookup = Q()
    for prefix in PAYMENT_DEBIT_PREFIXES:
        lookup |= Q(description__startswith=prefix)
    return receivable.objects.using(db).filter(type="Debit").filter(lookup)


def _aged_payment_prefix_q():
    lookup = Q()
    for prefix in AGED_PAYMENT_PREFIXES:
        lookup |= Q(description__istartswith=prefix)
    return lookup


def received_payment_credit_q():
    """Credit rows posted as Payment Received or Discount Allowed (Pay Now receipts)."""
    return Q(type__iexact="Credit") & _aged_payment_prefix_q()


def aged_receivable_payment_qs(db, invoice_id=None, customer_id=None):
    """Credits posted by Aged Receivables Pay Now (payment or discount)."""
    qs = (
        receivable.objects.using(db)
        .filter(type__iexact="Credit")
        .filter(_aged_payment_prefix_q())
        .exclude(description__icontains="[cancelled]")
    )
    if invoice_id:
        qs = qs.filter(token_id=invoice_id)
    if customer_id:
        qs = qs.filter(customer_id__iexact=customer_id)
    return qs.order_by("date", "id")


def serialize_aged_payments(db, invoice_id, customer_id=None):
    rows = []
    for row in aged_receivable_payment_qs(db, invoice_id, customer_id):
        desc = row.description or ""
        kind = "Discount" if desc.lower().startswith("discount allowed") else "Payment"
        rows.append({
            "id": row.id,
            "date": row.date.strftime("%Y-%m-%d") if hasattr(row.date, "strftime") else str(row.date or ""),
            "description": desc,
            "kind": kind,
            "payment_method": row.payment_method or "",
            "account_posted": row.account_posted or "",
            "amount": str(row.amount or 0),
        })
    return rows


def receivable_credit_is_cancellable(row):
    """True for uncancelled Payment Received / Discount Allowed credits tied to an invoice."""
    if (getattr(row, "type", "") or "").lower() != "credit":
        return False
    desc = row.description or ""
    if "[cancelled]" in desc.lower():
        return False
    if not desc.lower().startswith(tuple(p.lower() for p in AGED_PAYMENT_PREFIXES)):
        return False
    return bool((getattr(row, "token_id", None) or "").strip())


def aged_open_or_cancellable_invoice_qs(db):
    """Invoices with remaining balance. Balanced invoices leave Aged Receivables."""
    return exclude_returned_or_cancelled_invoices(
        customer_invoice.objects.using(db).filter(amount_paid__lt=F("amount_expected"))
    )


def _chart_for_account_posted(db, account_posted):
    from customer.functions.gl import get_chart
    from account.models import chart_of_account

    text = (account_posted or "").strip()
    if not text:
        return None
    acc = get_chart(db, text)
    if acc is not None:
        return acc
    if text.isdigit():
        return chart_of_account.objects.using(db).filter(id=int(text)).first()
    return chart_of_account.objects.using(db).filter(account_id=text).first()


def _mark_aged_payment_cancelled(db, row):
    desc = row.description or ""
    if "[cancelled]" in desc.lower():
        return
    mark = CANCELLED_PAYMENT_MARK
    max_len = 255
    if len(desc) + len(mark) > max_len:
        desc = desc[: max_len - len(mark)]
    row.description = desc + mark
    row.save(using=db)


def cancel_aged_receivable_payment(request, db, payment_id, customer_code, invoice_id):
    """Reverse one received-payment credit (Payment Received / Discount Allowed).

    Restores invoice amount_paid so the invoice can return to Aged Receivables,
    posts a Payment Cancelled AR Debit, reverses the original CreateLog series
    row, restores customer balance when needed, and unwinds loan allocations.
    """
    from datetime import date as date_cls
    from account.models import account_log, chart_of_account

    try:
        payment_id = int(payment_id)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Invalid payment."}

    customer_code = (customer_code or "").strip()
    invoice_id = (invoice_id or "").strip()
    if not customer_code or not invoice_id:
        return {"ok": False, "error": "Customer or invoice missing."}

    try:
        cus = customer_table.objects.using(db).get(customer_code=customer_code)
    except customer_table.DoesNotExist:
        return {"ok": False, "error": f"Customer '{customer_code}' not found."}

    today = date_cls.today()

    with transaction.atomic(using=db):
        row = (
            receivable.objects.using(db)
            .select_for_update()
            .filter(
                id=payment_id,
                customer_id__iexact=customer_code,
                token_id=invoice_id,
            )
            .first()
        )
        if row is None:
            return {"ok": False, "error": "Payment not found on this invoice."}
        if (row.type or "").lower() != "credit":
            return {"ok": False, "error": "Only received payments can be cancelled."}
        desc = row.description or ""
        if "[cancelled]" in desc.lower():
            return {"ok": False, "error": "This payment is already cancelled."}
        if not desc.lower().startswith(tuple(p.lower() for p in AGED_PAYMENT_PREFIXES)):
            return {"ok": False, "error": "This entry is not a received payment that can be cancelled."}

        amount = Decimal(str(row.amount or 0))
        if amount <= 0:
            return {"ok": False, "error": "Payment amount is zero."}

        cancel_desc = f"Payment Cancelled - Invoice {invoice_id} (#{row.id})"
        DebitReceivable(
            request, db, cus, today, cancel_desc,
            row.payment_method or "Cash",
            row.account_posted or "",
            amount,
            invoiceID=invoice_id,
        )
        _mark_aged_payment_cancelled(db, row)

        invs = list(
            customer_invoice.objects.using(db)
            .select_for_update()
            .filter(invoiceID=invoice_id, cusID=customer_code)
        )
        if invs:
            current_paid = Decimal(str(invs[0].amount_paid or 0))
            new_paid = current_paid - amount
            if new_paid < 0:
                new_paid = Decimal("0.00")
            for line in invs:
                line.amount_paid = new_paid
                line.save(using=db)

        if (row.payment_method or "").strip() == "Customer Balance":
            if hasattr(cus, "balance"):
                cus.balance = Decimal(str(cus.balance or 0)) + amount
            else:
                cus.Balance = Decimal(str(getattr(cus, "Balance", 0) or 0)) + amount
            cus.save(using=db)

        account = _chart_for_account_posted(db, row.account_posted)
        if account is not None:
            CreateLog(db, account, -amount, txn_date=today, user=request.user.username)
            account_log.objects.using(db).create(
                transaction_source="Payment Cancelled",
                amount=amount,
                date=today,
                account=account.account_id,
                account_type=account.account_type,
                Userlogin=request.user.username,
            )
        else:
            account_log.objects.using(db).create(
                transaction_source="Payment Cancelled",
                amount=amount,
                date=today,
                account=row.account_posted or "",
                account_type="",
                Userlogin=request.user.username,
            )

        try:
            from journal.fuctions.loan_schedule import reverse_aged_loan_repayment
            reverse_aged_loan_repayment(
                db,
                invoice_id=invoice_id,
                amount=amount,
                customer_id=customer_code,
                userlogin=getattr(request.user, "username", ""),
            )
        except Exception:
            import traceback
            traceback.print_exc()

        recompute_receivable_running_balances(db, [cus.customer_code])

        expected = Decimal(str(invs[0].amount_expected or 0)) if invs else Decimal("0.00")
        paid = Decimal(str(invs[0].amount_paid or 0)) if invs else Decimal("0.00")
        return {
            "ok": True,
            "amount": str(amount),
            "amount_paid": str(paid),
            "amount_expected": str(expected),
            "balance": str(expected - paid),
            "payments": serialize_aged_payments(db, invoice_id, customer_code),
        }


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


def _account_posted_is_loan_gl(account_posted):
    text = (account_posted or '').strip()
    if not text:
        return False
    compact = text.lower().replace(' ', '')
    if 'loanreceivable' in compact:
        return True
    return text == '1100' or text.startswith('1100-')


def _account_posted_is_chart_object(account_posted):
    return (account_posted or '').strip().lower().startswith('chart_of_account object')


def _loan_account_rows(db):
    """Read loan_account with whatever columns this tenant actually has."""
    with connections[db].cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            ['loan_account'],
        )
        cols = {row[0] for row in cursor.fetchall()}
    if not cols:
        return []
    want = [
        'id', 'date', 'debtor_id', 'debtor_name', 'description',
        'amount_borrowed', 'total_amount', 'account_debited',
    ]
    use = [name for name in want if name in cols]
    if not use:
        return []
    with connections[db].cursor() as cursor:
        cursor.execute('SELECT ' + ', '.join(use) + ' FROM loan_account')
        return [dict(zip(use, row)) for row in cursor.fetchall()]


def _loan_amounts(loan):
    amounts = set()
    for key in ('amount_borrowed', 'total_amount'):
        value = loan.get(key)
        if value is None or str(value).strip() == '':
            continue
        amounts.add(_d(value))
    return amounts


def _receivable_matches_loan(row, loans):
    amount = _d(row.amount)
    description = (row.description or '').strip()
    if not description:
        return False
    for loan in loans:
        if amount not in _loan_amounts(loan):
            continue
        if description == (loan.get('description') or '').strip():
            return True
    return False


def loan_posted_receivable_qs(db):
    """Debits create_new_loan wrote into the trade-receivable subsidiary."""
    loans = _loan_account_rows(db)
    keep_ids = []
    qs = receivable.objects.using(db).filter(type='Debit').order_by('date', 'id')
    for row in qs.only(
        'id', 'date', 'customer_id', 'customer_name', 'token_id',
        'description', 'amount', 'account_posted', 'balance',
    ):
        posted = row.account_posted or ''
        if _account_posted_is_loan_gl(posted):
            keep_ids.append(row.id)
        elif _account_posted_is_chart_object(posted) and _receivable_matches_loan(row, loans):
            keep_ids.append(row.id)
    if not keep_ids:
        return receivable.objects.using(db).none()
    return receivable.objects.using(db).filter(id__in=keep_ids).order_by('date', 'id')


def repair_loan_receivable_debits(db, dry_run=False):
    """Drop customer-loan Debits from receivable so AR is invoice outstanding only.

    Matching: Debit rows posted to 1100-LoanReceivable, or the historical
    str(chart_of_account) value when that row also matches a loan amount+description.
    Invoice sale Debits (4001-Sales) and later payment credits are kept.
    """
    junk = loan_posted_receivable_qs(db)
    preview = list(junk.values(
        'id', 'date', 'customer_id', 'customer_name', 'token_id',
        'description', 'amount', 'account_posted', 'balance',
    ))
    delete_count = len(preview)
    customer_ids = {
        row['customer_id'] for row in preview if row.get('customer_id')
    }

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
        recomputed = (
            recompute_receivable_running_balances(db, customer_ids)
            if customer_ids else 0
        )

    return {
        'deleted': delete_count,
        'would_delete': delete_count,
        'recomputed': recomputed,
        'rows': preview,
    }


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


def CreateLog(db, account, total, txn_date=None, user=None):
    """Write a series-table row. Prefer post_double_entry in customer.functions.gl."""
    from customer.functions.gl import post_series_log
    post_series_log(db, account, total, txn_date=txn_date, user=user)