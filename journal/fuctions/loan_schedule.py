import calendar
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.db import connections

from journal.models import loan_installment


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


def ensure_installment_table(db):
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
                amount_paid NUMERIC(12, 2) NOT NULL DEFAULT 0
            )
        """)


def save_installments(db, loan, rows):
    ensure_installment_table(db)
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
        )


def installment_status(expected, paid, due_date, today=None):
    today = today or date.today()
    expected = _money(expected)
    paid = _money(paid)
    if paid >= expected and expected > ZERO:
        return 'paid'
    if due_date and due_date < today:
        return 'defaulted'
    if paid > ZERO:
        return 'partial'
    if due_date and due_date == today:
        return 'due'
    return 'upcoming'


def get_or_create_schedule(db, loan):
    ensure_installment_table(db)
    existing = list(
        loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
    )
    totals = compute_loan_totals(loan.amount_borrowed, loan.interest, loan.duration)

    if not existing:
        _, rows = build_schedule(
            loan.amount_borrowed,
            loan.date,
            loan.duration,
            loan.interest,
        )
        save_installments(db, loan, rows)
        existing = list(
            loan_installment.objects.using(db).filter(loan_id=loan.id).order_by('month_number')
        )

    today = date.today()
    paid_total = ZERO
    cards = []
    defaulted = []
    extended_rate = _money(loan.extended_interest)
    extended_total = ZERO

    for row in existing:
        expected = _money(row.expected_amount)
        paid = _money(row.amount_paid)
        paid_total += paid
        status = installment_status(expected, paid, row.due_date, today)
        unpaid = max(ZERO, expected - paid)
        card = {
            'month_number': row.month_number,
            'due_date': row.due_date,
            'principal_portion': _money(row.principal_portion),
            'interest_portion': _money(row.interest_portion),
            'expected_amount': expected,
            'amount_paid': paid,
            'unpaid': unpaid,
            'status': status,
        }
        cards.append(card)

        if status == 'defaulted' and extended_rate > ZERO:
            charge = (unpaid * extended_rate / Decimal('100')).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            defaulted.append({
                'month_number': row.month_number,
                'due_date': row.due_date,
                'unpaid': unpaid,
                'rate': extended_rate,
                'charge': charge,
            })
            extended_total += charge

    return {
        'totals': totals,
        'cards': cards,
        'paid_total': paid_total,
        'balance_left': max(ZERO, totals['total_amount'] - paid_total),
        'defaulted': defaulted,
        'extended_rate': extended_rate,
        'extended_total': extended_total,
    }
