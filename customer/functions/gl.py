"""Double-entry GL posting used by Trial Balance.

Chart actual_balance is stored in each account's normal direction:
positive Assets/Expenses = debit, positive Liability/Equity/Income = credit.
A debit to a credit-normal account (or a credit to a debit-normal account)
subtracts, so Trial Balance can split the signed amount into columns.
"""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from django.apps import apps
from django.utils import timezone

from account.models import chart_of_account


ZERO = Decimal('0.00')
CENT = Decimal('0.01')

AR_ID = '1002-Receivable'
SALES_ID = '4001-Sales'
CASH_ID = '1010-000000'
VAT_ID = '6002-Vat'
RETURN_IN_ID = '2001-ReturnInward'
RETURN_OUT_ID = '1001-ReturnOutward'
PURCHASE_AP_ID = '2067-Purchase'
PURCHASE_COGS_ID = '2010-Purchased'
PAYABLE_ID = '2003-Payable'
LOAN_REC_ID = '1100-LoanReceivable'
OTHER_INCOME_ID = '4001-income'

SERIES_MODEL = {
    'assets': 'Assets_account',
    'asset': 'Assets_account',
    'expenses': 'Expenses_account',
    'expense': 'Expenses_account',
    'income': 'Income_account',
    'revenue': 'Income_account',
    'liability': 'Liability_account',
    'liabilities': 'Liability_account',
    'liablity': 'Liability_account',
    'equity': 'Equity_account',
}

SALES_LIKE_IDS = {SALES_ID, '4001-income'}
AR_LIKE_IDS = {AR_ID}


def money(value):
    try:
        return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
    except Exception:
        return ZERO


def as_date(value):
    if value is None:
        return timezone.now().date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00')).date()
    except Exception:
        return timezone.now().date()


def series_is_debit_normal(series_name):
    s = (series_name or '').strip().lower()
    if s in ('assets', 'asset', 'expenses', 'expense'):
        return True
    if s in ('liability', 'liabilities', 'liablity', 'equity', 'income', 'revenue'):
        return False
    if 'expense' in s or 'asset' in s:
        return True
    if any(token in s for token in ('liab', 'equity', 'income', 'revenue')):
        return False
    return True


def series_model_name(series_name):
    s = (series_name or '').strip().lower()
    if s in SERIES_MODEL:
        return SERIES_MODEL[s]
    titled = (series_name or '').strip().title().replace(' ', '') + '_account'
    return titled


def get_chart(db, account_id):
    if not account_id:
        return None
    try:
        return chart_of_account.objects.using(db).get(account_id=str(account_id).strip())
    except chart_of_account.DoesNotExist:
        return None


def get_chart_any(db, *account_ids):
    for account_id in account_ids:
        acc = get_chart(db, account_id)
        if acc is not None:
            return acc
    return None


def is_bank_or_cash(account):
    if account is None:
        return False
    if account.account_id in SALES_LIKE_IDS or account.account_id in AR_LIKE_IDS:
        return False
    series = (account.series_name or '').strip().lower()
    typ = (account.account_type or '').lower()
    name = (account.account_bankname or '').lower()
    if 'receivable' in typ or 'receivable' in name or 'debtor' in name:
        return False
    if 'cash' in typ or 'bank' in typ:
        return True
    if series in ('assets', 'asset') and 'payable' not in typ:
        if 'loan' in name:
            return False
        return True
    return False


def cash_chart(db, account_id=None, payment_method=None):
    acc = get_chart(db, account_id)
    if is_bank_or_cash(acc):
        return acc
    fallback = get_chart_any(db, CASH_ID, '1010-Cash', '1011-UBA')
    if fallback is not None:
        return fallback
    return acc


def post_series_log(db, account, amount, txn_date=None, user=None):
    """Write one series-table row. Does not change actual_balance."""
    amt = money(amount)
    if account is None or amt == ZERO:
        return
    model_name = series_model_name(account.series_name)
    try:
        AccountModel = apps.get_model(app_label='account', model_name=model_name)
    except LookupError:
        return
    AccountModel.objects.using(db).create(
        account_id=account.account_id,
        series_name=account.series_name,
        account_bankname=account.account_bankname,
        account_type=account.account_type,
        amount=amt,
        date=as_date(txn_date),
        Userlogin=user or '',
    )


def apply_normal(db, account, signed_amount, txn_date=None, user=None):
    """Add signed_amount in the account's normal direction and log it."""
    amt = money(signed_amount)
    if account is None or amt == ZERO:
        return
    fresh = chart_of_account.objects.using(db).get(pk=account.pk)
    fresh.actual_balance = money(fresh.actual_balance) + amt
    fresh.save(using=db)
    post_series_log(db, fresh, amt, txn_date=txn_date, user=user)


def debit_gl(db, account, amount, txn_date=None, user=None):
    amt = money(amount)
    if amt == ZERO or account is None:
        return
    if series_is_debit_normal(account.series_name):
        apply_normal(db, account, amt, txn_date=txn_date, user=user)
    else:
        apply_normal(db, account, -amt, txn_date=txn_date, user=user)


def credit_gl(db, account, amount, txn_date=None, user=None):
    amt = money(amount)
    if amt == ZERO or account is None:
        return
    if series_is_debit_normal(account.series_name):
        apply_normal(db, account, -amt, txn_date=txn_date, user=user)
    else:
        apply_normal(db, account, amt, txn_date=txn_date, user=user)


def post_double_entry(db, debit_account, credit_account, amount, txn_date=None, user=None):
    amt = money(amount)
    if amt == ZERO:
        return
    if debit_account is None or credit_account is None:
        return
    if debit_account.account_id == credit_account.account_id:
        return
    debit_gl(db, debit_account, amt, txn_date=txn_date, user=user)
    credit_gl(db, credit_account, amt, txn_date=txn_date, user=user)


def included_vat(total, vat):
    """VAT already inside the invoice total (typical 7.5/107.5). Skip junk ratios."""
    total = money(total)
    vat = money(vat)
    if vat <= ZERO or total <= ZERO or vat >= total:
        return ZERO
    if (vat / total) > Decimal('0.20'):
        return ZERO
    return vat


def post_sale(db, total, paid=0, vat=0, payment_account_id=None, payment_method=None,
              extra_receipts=None, txn_date=None, user=None):
    """Dr AR (and cash for collections), Cr Sales / VAT."""
    total = money(total)
    paid = money(paid)
    if total <= ZERO:
        return
    ar = get_chart_any(db, AR_ID)
    sales = get_chart_any(db, SALES_ID)
    if ar is None or sales is None:
        return
    vat_amt = included_vat(total, vat)
    net = total - vat_amt
    post_double_entry(db, ar, sales, net, txn_date=txn_date, user=user)
    if vat_amt:
        vat_acc = get_chart_any(db, VAT_ID, '2000-Tax')
        post_double_entry(db, ar, vat_acc, vat_amt, txn_date=txn_date, user=user)
    receipts = list(extra_receipts or [])
    if paid > ZERO:
        receipts.insert(0, (payment_account_id, paid, payment_method))
    for account_id, amount, method in receipts:
        amount = money(amount)
        if amount <= ZERO:
            continue
        bank = cash_chart(db, account_id, method)
        post_double_entry(db, bank, ar, amount, txn_date=txn_date, user=user)


def post_sale_return(db, total, paid=0, vat=0, payment_account_id=None, payment_method=None,
                     txn_date=None, user=None):
    """Dr Return Inward / VAT, Cr AR; refund cash that was collected."""
    total = money(total)
    paid = money(paid)
    if total <= ZERO:
        return
    ar = get_chart_any(db, AR_ID)
    ret = get_chart_any(db, RETURN_IN_ID, SALES_ID)
    if ar is None or ret is None:
        return
    vat_amt = included_vat(total, vat)
    net = total - vat_amt
    post_double_entry(db, ret, ar, net, txn_date=txn_date, user=user)
    if vat_amt:
        vat_acc = get_chart_any(db, VAT_ID, '2000-Tax')
        post_double_entry(db, vat_acc, ar, vat_amt, txn_date=txn_date, user=user)
    if paid > ZERO:
        bank = cash_chart(db, payment_account_id, payment_method)
        post_double_entry(db, ar, bank, paid, txn_date=txn_date, user=user)


def post_receipt(db, amount, payment_account_id=None, payment_method=None,
                 party='customer', txn_date=None, user=None):
    """Customer receipt: Dr cash, Cr AR. Vendor receipt: Dr cash, Cr AP."""
    amount = money(amount)
    if amount <= ZERO:
        return
    bank = cash_chart(db, payment_account_id, payment_method)
    if party == 'vendor':
        contra = get_chart_any(db, PAYABLE_ID, PURCHASE_AP_ID)
    else:
        contra = get_chart_any(db, AR_ID)
    post_double_entry(db, bank, contra, amount, txn_date=txn_date, user=user)


def post_purchase(db, total, paid=0, payment_account_id=None, payment_method=None,
                  txn_date=None, user=None):
    """Dr purchases, Cr AP; settle AP with cash when paid."""
    total = money(total)
    paid = money(paid)
    if total <= ZERO:
        return
    cogs = get_chart_any(db, PURCHASE_COGS_ID, '2065-PURCHASE', '2002-Purchase')
    ap = get_chart_any(db, PURCHASE_AP_ID, PAYABLE_ID)
    if cogs is None or ap is None:
        return
    if cogs.account_id == ap.account_id:
        bank = cash_chart(db, payment_account_id, payment_method)
        post_double_entry(db, cogs, bank if paid else ap, total, txn_date=txn_date, user=user)
        return
    post_double_entry(db, cogs, ap, total, txn_date=txn_date, user=user)
    if paid > ZERO:
        bank = cash_chart(db, payment_account_id, payment_method)
        post_double_entry(db, ap, bank, paid, txn_date=txn_date, user=user)


def post_loan_disbursement(db, loan_account, amount, txn_date=None, user=None):
    amount = money(amount)
    if amount <= ZERO or loan_account is None:
        return
    cash = cash_chart(db)
    post_double_entry(db, loan_account, cash, amount, txn_date=txn_date, user=user)


def post_loan_repayment(db, loan_account, amount, txn_date=None, user=None):
    """Invoice payment already Dr cash Cr AR; move that onto the loan."""
    amount = money(amount)
    if amount <= ZERO or loan_account is None:
        return
    ar = get_chart_any(db, AR_ID)
    post_double_entry(db, ar, loan_account, amount, txn_date=txn_date, user=user)


def post_loan_interest(db, loan_account, amount, txn_date=None, user=None):
    amount = money(amount)
    if amount <= ZERO or loan_account is None:
        return
    income = get_chart_any(db, OTHER_INCOME_ID, SALES_ID)
    post_double_entry(db, loan_account, income, amount, txn_date=txn_date, user=user)


def post_transfer(db, from_account, to_account, amount, txn_date=None, user=None):
    post_double_entry(db, to_account, from_account, amount, txn_date=txn_date, user=user)


def table_columns(db, table):
    from django.db import connections
    with connections[db].cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            [table],
        )
        return {row[0] for row in cursor.fetchall()}


class _Row:
    def __init__(self, data):
        self.__dict__.update(data)

    def __getattr__(self, name):
        return None


def _values_existing(db, model, table, fields):
    cols = table_columns(db, table)
    use = [f for f in fields if f in cols]
    if not use:
        return []
    return [_Row(row) for row in model.objects.using(db).values(*use)]


def _unique_invoices(rows, id_field='invoiceID'):
    seen = {}
    for row in rows:
        key = getattr(row, id_field, None) or ''
        if key in seen:
            continue
        seen[key] = row
    return list(seen.values())


def _invoice_returned(invoice):
    iid = str(getattr(invoice, 'invoiceID', '') or '').lower()
    status = str(getattr(invoice, 'cancellation_status', '') or '')
    state = str(getattr(invoice, 'invoice_state', '') or '').lower()
    return (
        'returned' in iid
        or status == '1'
        or state in ('cancelled', 'canceled', 'returned')
    )


def _vat_for_invoice(vat_map, invoice_id):
    invoice_id = str(invoice_id or '')
    base = invoice_id.replace('_returned', '')
    for key in (invoice_id, base, base + '_returned'):
        amt = vat_map.get(key)
        if amt:
            return money(amt)
    return ZERO


def reset_chart_and_series(db):
    from account.models import (
        Assets_account, Expenses_account, Liability_account,
        Equity_account, Income_account,
    )
    Assets_account.objects.using(db).all().delete()
    Expenses_account.objects.using(db).all().delete()
    Liability_account.objects.using(db).all().delete()
    Equity_account.objects.using(db).all().delete()
    Income_account.objects.using(db).all().delete()
    updated = 0
    for acc in chart_of_account.objects.using(db).all():
        if money(acc.actual_balance) != ZERO:
            acc.actual_balance = ZERO
            acc.save(using=db)
            updated += 1
    return updated


def repair_trial_balance_gl(db, dry_run=False):
    """Rebuild series logs and chart balances from invoices, purchases, loans."""
    from customer.models import customer_invoice, Vat, receivable
    from vendor.models import Vendor_invoice
    from journal.models import loan_account

    vat_map = {}
    try:
        for row in Vat.objects.using(db).all():
            vat_map[str(row.source)] = vat_map.get(str(row.source), ZERO) + money(row.amount)
    except Exception:
        vat_map = {}

    sales_invoices = _unique_invoices(_values_existing(
        db, customer_invoice, 'customer_invoice',
        [
            'id', 'invoiceID', 'amount_expected', 'amount_paid',
            'cancellation_status', 'invoice_state', 'invoice_date',
            'payment_account', 'payment_method',
        ],
    ))
    purchase_invoices = _unique_invoices(_values_existing(
        db, Vendor_invoice, 'vendor_invoice',
        [
            'id', 'invoiceID', 'amount_expected', 'amount_paid',
            'cancellation', 'invoice_date',
        ],
    ))

    preview = {
        'sales': 0,
        'returns': 0,
        'receipts': 0,
        'purchases': 0,
        'loans': 0,
        'unallocated': 0,
        'sale_total': ZERO,
        'return_total': ZERO,
        'paid_total': ZERO,
        'purchase_total': ZERO,
        'loan_total': ZERO,
        'unallocated_total': ZERO,
    }

    sale_posts = []
    for inv in sales_invoices:
        total = money(inv.amount_expected)
        paid = money(inv.amount_paid)
        vat = _vat_for_invoice(vat_map, inv.invoiceID)
        txn_date = as_date(inv.invoice_date)
        method = inv.payment_method
        pay_acc = inv.payment_account
        if _invoice_returned(inv):
            preview['returns'] += 1
            preview['return_total'] += total
            # Original sale plus reversing return so AR nets to zero.
            sale_posts.append(('sale', total, paid, vat, pay_acc, method, txn_date))
            sale_posts.append(('return', total, paid, vat, pay_acc, method, txn_date))
        else:
            preview['sales'] += 1
            preview['sale_total'] += total
            preview['paid_total'] += paid
            sale_posts.append(('sale', total, paid, vat, pay_acc, method, txn_date))

    unallocated = []
    try:
        for row in receivable.objects.using(db).filter(type='Credit').order_by('id'):
            token = str(row.token_id or '').strip()
            if token:
                continue
            amt = money(row.amount)
            if amt <= ZERO:
                continue
            preview['unallocated'] += 1
            preview['unallocated_total'] += amt
            unallocated.append((amt, row.account_posted, row.payment_method, as_date(row.date)))
    except Exception:
        unallocated = []

    purchase_posts = []
    for inv in purchase_invoices:
        total = money(inv.amount_expected)
        paid = money(inv.amount_paid)
        if total <= ZERO:
            continue
        preview['purchases'] += 1
        preview['purchase_total'] += total
        # Payable has debit-only rows for the billed purchases: treat as unpaid
        # when there is no matching cash account movement. Use invoice paid
        # only when it is strictly less than expected (part payment).
        settle = paid if ZERO < paid < total else ZERO
        purchase_posts.append((total, settle, as_date(inv.invoice_date)))

    loan_posts = []
    try:
        for loan in loan_account.objects.using(db).all():
            left = money(loan.balance_left)
            if left == ZERO:
                continue
            acc = get_chart(db, loan.account_debited) or get_chart(db, LOAN_REC_ID)
            preview['loans'] += 1
            preview['loan_total'] += left
            loan_posts.append((acc, left, as_date(loan.date)))
    except Exception:
        pass

    if dry_run:
        return preview

    reset_chart_and_series(db)

    for kind, total, paid, vat, pay_acc, method, txn_date in sale_posts:
        if kind == 'sale':
            post_sale(
                db, total=total, paid=paid, vat=vat,
                payment_account_id=pay_acc, payment_method=method,
                txn_date=txn_date,
            )
        else:
            post_sale_return(
                db, total=total, paid=paid, vat=vat,
                payment_account_id=pay_acc, payment_method=method,
                txn_date=txn_date,
            )

    for amt, account_posted, method, txn_date in unallocated:
        post_receipt(
            db, amt, payment_account_id=account_posted,
            payment_method=method, party='customer', txn_date=txn_date,
        )

    for total, paid, txn_date in purchase_posts:
        post_purchase(db, total=total, paid=paid, txn_date=txn_date)

    for acc, left, txn_date in loan_posts:
        post_loan_disbursement(db, acc, left, txn_date=txn_date)

    return preview
