import calendar
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.db import connections

from journal.models import loan_account, loan_installment, loan_repayment


TWOPLACES = Decimal('0.01')
ZERO = Decimal('0.00')


def _money(value):
    if value is None:
        return ZERO
    try:
        return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return ZERO


def _parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not value:
        return date.today()
    text = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return date.today()


def _months(duration):
    try:
        months = int(duration)
    except (TypeError, ValueError):
        months = 1
    return max(1, months)


def add_months(start, months):
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def split_amount(total, parts):
    total = _money(total)
    n = max(1, int(parts))
    base = (total / n).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    amounts = [base] * n
    amounts[-1] = total - (base * (n - 1))
    return amounts


def compute_loan_totals(principal, interest_rate=None, duration=None):
    principal = _money(principal)
    months = _months(duration)
    rate = _money(interest_rate)
    interest_amount = (principal * rate / Decimal('100')).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    total_amount = principal + interest_amount
    return {
        'principal': principal,
        'months': months,
        'interest_rate': rate,
        'interest_amount': interest_amount,
        'total_amount': total_amount,
    }


def build_schedule(principal, start_date, duration=None, interest_rate=None):
    totals = compute_loan_totals(principal, interest_rate, duration)
    start = _parse_date(start_date)
    principal_parts = split_amount(totals['principal'], totals['months'])
    interest_parts = split_amount(totals['interest_amount'], totals['months'])

    rows = []
    for index in range(totals['months']):
        principal_portion = principal_parts[index]
        interest_portion = interest_parts[index]
        rows.append({
            'month_number': index + 1,
            'due_date': add_months(start, index + 1),
            'principal_portion': principal_portion,
            'interest_portion': interest_portion,
            'expected_amount': principal_portion + interest_portion,
            'amount_paid': ZERO,
        })
    return totals, rows


def ensure_loan_tables(db):
    with connections[db].cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_installment (
                id BIGSERIAL PRIMARY KEY,
                loan_id INTEGER NOT NULL,
                transaction_id VARCHAR(200) NOT NULL,
                month_number SMALLINT NOT NULL,
                due_date DATE NOT NULL,
                principal_portion NUMERIC(12, 2) NOT NULL,
                interest_portion NUMERIC(12, 2) NOT NULL DEFAULT 0,
                expected_amount NUMERIC(12, 2) NOT NULL,
                amount_paid NUMERIC(12, 2) NOT NULL DEFAULT 0,
                extended_interest_amount NUMERIC(12, 2) NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("""
            ALTER TABLE loan_installment
            ADD COLUMN IF NOT EXISTS extended_interest_amount NUMERIC(12, 2) NOT NULL DEFAULT 0
        """)
        cursor.execute("""
            ALTER TABLE loan_account
            ADD COLUMN IF NOT EXISTS interest_amount NUMERIC(12, 2)
        """)
        cursor.execute("""
            ALTER TABLE loan_account
            ADD COLUMN IF NOT EXISTS total_amount NUMERIC(12, 2)
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_repayment (
                id BIGSERIAL PRIMARY KEY,
                loan_id INTEGER NOT NULL,
                installment_id INTEGER NOT NULL,
                invoice_id VARCHAR(200) NOT NULL DEFAULT '',
                amount NUMERIC(12, 2) NOT NULL,
                date DATE NOT NULL,
                source VARCHAR(60) NOT NULL DEFAULT 'aged_receivable',
                payment_method VARCHAR(80) NOT NULL DEFAULT '',
                "Userlogin" VARCHAR(60) NOT NULL DEFAULT '',
                note VARCHAR(250) NOT NULL DEFAULT ''
            )
        """)


def ensure_installment_table(db):
    ensure_loan_tables(db)


def save_installments(db, loan, rows):
    ensure_loan_tables(db)
    loan_installment.objects.using(db).filter(loan_id=loan.id).delete()
    for row in rows:
        loan_installment.objects.using(db).create(
            loan_id=loan.id,
            transaction_id=str(loan.transaction_id or ''),
            month_number=row['month_number'],
            due_date=row['due_date'],
            principal_portion=row['principal_portion'],
            interest_portion=row['interest_portion'],
            expected_amount=row['expected_amount'],
            amount_paid=row.get('amount_paid') or ZERO,
            extended_interest_amount=row.get('extended_interest_amount') or ZERO,
        )


def installment_amount_due(installment):
    return _money(installment.expected_amount) + _money(getattr(installment, 'extended_interest_amount', 0))


def installment_status(amount_due, paid, due_date, today=None):
    today = today or date.today()
    amount_due = _money(amount_due)
    paid = _money(paid)
    if amount_due > ZERO and paid >= amount_due:
        return 'paid'
    if due_date and due_date < today:
        return 'defaulted'
    if paid > ZERO:
        return 'partial'
    if due_date and due_date == today:
        return 'due'
    return 'upcoming'


def refresh_loan_balance(db, loan, installments=None):
    if installments is None:
        installments = list(
            loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
        )
    total_due = ZERO
    paid_total = ZERO
    for inst in installments:
        total_due += installment_amount_due(inst)
        paid_total += _money(inst.amount_paid)
    balance = max(ZERO, total_due - paid_total)
    loan.balance_left = balance
    loan.status = 'paid' if balance == ZERO and total_due > ZERO else 'unpaid'
    loan.save(using=db)
    return paid_total, balance


def apply_saved_defaults(db, loan, installments=None):
    """Persist extended interest once a month is overdue and unpaid."""
    ensure_loan_tables(db)
    rate = _money(loan.extended_interest)
    if rate <= ZERO:
        return ZERO

    if installments is None:
        installments = list(
            loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
        )

    today = date.today()
    added = ZERO
    for inst in installments:
        already = _money(getattr(inst, 'extended_interest_amount', 0))
        if already > ZERO:
            continue
        unpaid = max(ZERO, _money(inst.expected_amount) - _money(inst.amount_paid))
        if inst.due_date and inst.due_date < today and unpaid > ZERO:
            charge = (unpaid * rate / Decimal('100')).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            inst.extended_interest_amount = charge
            inst.save(using=db)
            added += charge

    if added > ZERO:
        refresh_loan_balance(db, loan, installments)
    return added


def _loan_totals(loan):
    totals = compute_loan_totals(loan.amount_borrowed, loan.interest, loan.duration)
    stored_interest = getattr(loan, 'interest_amount', None)
    stored_total = getattr(loan, 'total_amount', None)
    if stored_interest is not None:
        totals['interest_amount'] = _money(stored_interest)
    if stored_total is not None:
        totals['total_amount'] = _money(stored_total)
    return totals


def get_or_create_schedule(db, loan):
    ensure_loan_tables(db)
    existing = list(
        loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
    )
    totals = _loan_totals(loan)

    if not existing:
        _, rows = build_schedule(
            loan.amount_borrowed,
            loan.date,
            loan.duration,
            loan.interest,
        )
        save_installments(db, loan, rows)
        if getattr(loan, 'interest_amount', None) is None:
            loan.interest_amount = totals['interest_amount']
            loan.total_amount = totals['total_amount']
            loan.save(using=db)
        existing = list(
            loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
        )

    apply_saved_defaults(db, loan, existing)
    existing = list(
        loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
    )
    loan.refresh_from_db()

    repayments = list(
        loan_repayment.objects.using(db).filter(loan_id=loan.id).order_by('date', 'id')
    )
    by_installment = {}
    for payment in repayments:
        by_installment.setdefault(payment.installment_id, []).append(payment)

    today = date.today()
    paid_total = ZERO
    cards = []
    defaulted = []
    extended_rate = _money(loan.extended_interest)
    extended_total = ZERO

    for row in existing:
        expected = _money(row.expected_amount)
        extended = _money(getattr(row, 'extended_interest_amount', 0))
        amount_due = expected + extended
        paid = _money(row.amount_paid)
        paid_total += paid
        unpaid = max(ZERO, amount_due - paid)
        status = installment_status(amount_due, paid, row.due_date, today)
        card = {
            'id': row.id,
            'month_number': row.month_number,
            'due_date': row.due_date,
            'principal_portion': _money(row.principal_portion),
            'interest_portion': _money(row.interest_portion),
            'expected_amount': expected,
            'extended_interest': extended,
            'amount_due': amount_due,
            'amount_paid': paid,
            'unpaid': unpaid,
            'status': status,
            'payments': by_installment.get(row.id, []),
        }
        cards.append(card)

        if extended > ZERO:
            defaulted.append({
                'month_number': row.month_number,
                'due_date': row.due_date,
                'unpaid': max(ZERO, expected - paid),
                'rate': extended_rate,
                'charge': extended,
            })
            extended_total += extended

    return {
        'totals': totals,
        'cards': cards,
        'paid_total': paid_total,
        'balance_left': max(ZERO, sum(card['amount_due'] for card in cards) - paid_total),
        'defaulted': defaulted,
        'extended_rate': extended_rate,
        'extended_total': extended_total,
    }


def find_loan_for_invoice(db, invoice_id, customer_id=None):
    if not invoice_id:
        return None
    qs = loan_account.objects.using(db).filter(reference=invoice_id)
    if customer_id:
        match = qs.filter(debtor_id=customer_id).order_by('-id').first()
        if match:
            return match
    return qs.order_by('-id').first()


def allocate_loan_repayment(
    db,
    invoice_id,
    amount,
    payment_date=None,
    source='aged_receivable',
    payment_method='',
    userlogin='',
    customer_id=None,
):
    """Apply an Aged Receivable payment across unpaid loan months, oldest first."""
    remaining = _money(amount)
    if remaining <= ZERO:
        return []

    ensure_loan_tables(db)
    loan = find_loan_for_invoice(db, invoice_id, customer_id)
    if not loan:
        return []

    get_or_create_schedule(db, loan)
    installments = list(
        loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
    )
    apply_saved_defaults(db, loan, installments)
    installments = list(
        loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
    )

    pay_date = _parse_date(payment_date)
    allocations = []

    for inst in installments:
        if remaining <= ZERO:
            break
        needed = installment_amount_due(inst) - _money(inst.amount_paid)
        if needed <= ZERO:
            continue
        applied = min(needed, remaining)
        inst.amount_paid = _money(inst.amount_paid) + applied
        inst.save(using=db)
        repayment = loan_repayment.objects.using(db).create(
            loan_id=loan.id,
            installment_id=inst.id,
            invoice_id=str(invoice_id or ''),
            amount=applied,
            date=pay_date,
            source=source,
            payment_method=payment_method or '',
            Userlogin=userlogin or '',
            note='Aged receivable payment',
        )
        allocations.append(repayment)
        remaining -= applied

    refresh_loan_balance(db, loan, installments)
    return allocations

