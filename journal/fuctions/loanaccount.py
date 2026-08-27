from journal.forms import LoanAccountForm, LoanAccountLogForm
from django.contrib import messages
from customer.models import customer_table, receivable, payable
from customer.forms import *
from vendor.models import vendor_table
from account.models import *
from employee.models import employee, staff_account
from employee.forms import employee
from account.models import chart_of_account
import uuid, decimal
from customer.functions.generalFunction import DebitPayable, DebitReceivable, CreateLog
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import decimal
import uuid
from journal.fuctions.loan_schedule import (
    build_schedule,
    save_installments,
    _money,
    ensure_loan_tables,
)
from journal.models import loan_installment, loan_repayment


def create_new_loan(request, db):
    try:
        #Safely get POST data
        date = request.POST.get('date')
        employee_id = request.POST.get('employee_id')
        customer_id = request.POST.get('customer_id')
        vendor_id = request.POST.get('vendor_id')
        description = request.POST.get('description')
        amount_borrowed = request.POST.get('amount_borrowed')

        # New optional fields (Spacesoft-only UI, but harmless for everyone else)
        duration = request.POST.get('duration') or None
        interest = request.POST.get('interest') or None
        extended_interest = request.POST.get('extended_interest') or None
        reference = request.POST.get('reference') or ""
        
        apply_interest = request.POST.get('apply_interest') == 'on'
        apply_extended_interest = request.POST.get('apply_extended_interest') == 'on'


        # Basic validation
        if not all([date, description, amount_borrowed]):
            messages.error(request, "All required fields must be filled")
            return None

        try:
            amount_borrowed = decimal.Decimal(amount_borrowed)
        except:
            messages.error(request, "Invalid amount")
            return None

        if apply_interest and not interest:
            messages.error(request, "Enter an interest rate, or uncheck Apply Interest")
            return None

        if apply_extended_interest and not extended_interest:
            messages.error(request, "Enter an extended interest rate, or uncheck Apply Extended Interest")
            return None
        
        if interest and not apply_interest:
            interest = None

        if extended_interest and not apply_extended_interest:
            extended_interest = None
            
    
        # Validate interest fields if provided
        for label, value in (("Interest", interest), ("Extended interest", extended_interest)):
            if value is not None:
                try:
                    decimal.Decimal(value)
                except:
                    messages.error(request, f"{label} must be a valid number")
                    return None

        #Get account safely
        try:
            account_debited = chart_of_account.objects.using(db).get(account_id="1100-LoanReceivable")
        except chart_of_account.DoesNotExist:
            messages.error(request, "Selected account does not exist")
            return None

        debtor_id = None
        debtor_name = None

        # Determine debtor
        try:
            if employee_id:
                emp = employee.objects.using(db).get(staff_ID=employee_id)
                debtor_id = employee_id
                debtor_name = emp.fullname

            elif customer_id:
                cus = customer_table.objects.using(db).get(customer_code=customer_id)
                debtor_id = customer_id
                debtor_name = cus.name

            elif vendor_id:
                ven = vendor_table.objects.using(db).get(custID=vendor_id)
                debtor_id = vendor_id
                debtor_name = ven.name

            else:
                messages.error(request, "Select Employee, Customer or Vendor")
                return None

        except ObjectDoesNotExist:
            messages.error(request, "Selected debtor does not exist")
            return None

        totals, schedule_rows = build_schedule(
            amount_borrowed, date, duration, interest
        )
        if not duration:
            duration = str(totals['months'])
        balance_left = totals['total_amount']
        transaction_id = uuid.uuid4()

        form_data = {
            "date": date,
            "debtor_name": debtor_name,
            "debtor_id": debtor_id,
            "description": description,
            "amount_borrowed": amount_borrowed,
            "balance_left": balance_left,
            "account_debited": account_debited.account_id,
            "duration": duration,
            "interest": interest,
            "extended_interest": extended_interest,
            "reference": reference,
        }

        loan_form = LoanAccountForm(form_data)
        loan_log_form = LoanAccountLogForm(form_data)

        if not (loan_form.is_valid() and loan_log_form.is_valid()):
            print("Loan Form Errors:", loan_form.errors)
            print("Loan Log Form Errors:", loan_log_form.errors)
            messages.error(request, f"{loan_form.errors} {loan_log_form.errors}")
            return loan_form

        #ATOMIC TRANSACTION (VERY IMPORTANT)
        with transaction.atomic():
            account = account_debited
            amount_owed = totals['total_amount']
            if employee_id:
                last_record = staff_account.objects.using(db).filter(staff_id=debtor_id).last()
                initial_bal = last_record.balance if last_record else decimal.Decimal("0.00")

                balance = initial_bal + amount_owed

                staff_account.objects.using(db).create(
                    date=date,
                    staff_id=debtor_id,
                    staff_name=debtor_name,
                    amount=amount_owed,
                    initial_amount=initial_bal,
                    balance=balance,
                    account_posted=account_debited.account_id,
                    description=description,
                    payment_method="Cash",
                    invoice_status="Unused",
                    transaction_id=transaction_id,
                    Userlogin=request.user.username
                )

            elif customer_id:
                DebitReceivable(request, db, cus, date, description, "Cash", account, amount_owed)

            elif vendor_id:
                DebitPayable(request, db, ven, date, description, "Cash", account, amount_owed)

            #Save loan
            loan_instance = loan_form.save(commit=False)
            loan_instance.transaction_id = transaction_id
            loan_instance.interest_amount = totals['interest_amount']
            loan_instance.total_amount = totals['total_amount']
            loan_instance.balance_left = totals['total_amount']
            loan_instance.save(using=db)
            save_installments(db, loan_instance, schedule_rows)

            #Save log
            loan_log_instance = loan_log_form.save(commit=False)
            loan_log_instance.transaction_id = transaction_id
            loan_log_instance.save(using=db)

            #Update account balance
            account_debited.actual_balance += amount_owed
            CreateLog(db, account_debited, amount_owed)

            #Log entry
            account_log.objects.using(db).create(
                transaction_source="Loan",
                amount=amount_owed,
                date=date,
                account=account_debited.account_id,
                account_type=account_debited.account_type,
                Userlogin=request.user.username
            )

        messages.success(request, "Loan created successfully")
        return True

    except Exception as e:
        #Catch ANY unexpected error
        print("ERROR:", str(e))  # for debugging
        messages.error(request, "Something went wrong. Please try again.")
        return None


def loan_has_payments(db, loan_id):
    ensure_loan_tables(db)
    if loan_repayment.objects.using(db).filter(loan_id=loan_id).exists():
        return True
    return loan_installment.objects.using(db).filter(loan_id=loan_id, amount_paid__gt=0).exists()


def detect_borrower_type(db, debtor_id):
    from employee.models import employee as Employee
    if not debtor_id:
        return 'employee'
    if Employee.objects.using(db).filter(staff_ID=debtor_id).exists():
        return 'employee'
    if customer_table.objects.using(db).filter(customer_code=debtor_id).exists():
        return 'customer'
    if vendor_table.objects.using(db).filter(custID=debtor_id).exists():
        return 'vendor'
    return 'employee'


def update_existing_loan(request, db, loan):
    from employee.models import employee as Employee

    date = request.POST.get('date')
    employee_id = request.POST.get('employee_id')
    customer_id = request.POST.get('customer_id')
    vendor_id = request.POST.get('vendor_id')
    description = request.POST.get('description')
    reference = request.POST.get('reference') or ""
    apply_extended_interest = request.POST.get('apply_extended_interest') == 'on'
    extended_interest = request.POST.get('extended_interest') or None
    if extended_interest and not apply_extended_interest:
        extended_interest = None
    if apply_extended_interest and not extended_interest:
        messages.error(request, "Enter an extended interest rate, or uncheck Apply Extended Interest")
        return None

    if not all([date, description]):
        messages.error(request, "Date and description are required")
        return None

    if extended_interest is not None:
        try:
            decimal.Decimal(extended_interest)
        except Exception:
            messages.error(request, "Extended interest must be a valid number")
            return None

    has_payments = loan_has_payments(db, loan.id)

    if has_payments:
        amount_borrowed = _money(loan.amount_borrowed)
        duration = loan.duration
        interest = loan.interest
        reference = loan.reference or ""
        debtor_id = loan.debtor_id
        debtor_name = loan.debtor_name
    else:
        amount_borrowed = request.POST.get('amount_borrowed')
        duration = request.POST.get('duration') or None
        interest = request.POST.get('interest') or None
        apply_interest = request.POST.get('apply_interest') == 'on'
        if apply_interest and not interest:
            messages.error(request, "Enter an interest rate, or uncheck Apply Interest")
            return None
        if interest and not apply_interest:
            interest = None
        try:
            amount_borrowed = decimal.Decimal(amount_borrowed)
        except Exception:
            messages.error(request, "Invalid amount")
            return None
        if interest is not None:
            try:
                decimal.Decimal(interest)
            except Exception:
                messages.error(request, "Interest must be a valid number")
                return None

    if not has_payments:
        try:
            if employee_id:
                emp = Employee.objects.using(db).get(staff_ID=employee_id)
                debtor_id = employee_id
                debtor_name = emp.fullname
            elif customer_id:
                cus = customer_table.objects.using(db).get(customer_code=customer_id)
                debtor_id = customer_id
                debtor_name = cus.name
            elif vendor_id:
                ven = vendor_table.objects.using(db).get(custID=vendor_id)
                debtor_id = vendor_id
                debtor_name = ven.name
            else:
                debtor_id = loan.debtor_id
                debtor_name = loan.debtor_name
        except ObjectDoesNotExist:
            messages.error(request, "Selected debtor does not exist")
            return None

    totals, schedule_rows = build_schedule(amount_borrowed, date, duration, interest)
    if not duration:
        duration = str(totals['months'])

    old_total = _money(loan.total_amount) if loan.total_amount is not None else _money(loan.amount_borrowed)

    try:
        account_debited = chart_of_account.objects.using(db).get(account_id=loan.account_debited or "1100-LoanReceivable")
    except chart_of_account.DoesNotExist:
        account_debited = None

    with transaction.atomic():
        loan.date = date
        loan.description = description
        loan.debtor_id = debtor_id
        loan.debtor_name = debtor_name
        loan.reference = reference
        loan.extended_interest = extended_interest
        loan.duration = duration
        loan.interest = interest
        loan.amount_borrowed = amount_borrowed
        loan.interest_amount = totals['interest_amount']
        loan.total_amount = totals['total_amount']

        if not has_payments:
            loan.balance_left = totals['total_amount']
            loan.save(using=db)
            save_installments(db, loan, schedule_rows)
            diff = totals['total_amount'] - old_total
            if account_debited is not None and diff != 0:
                account_debited.actual_balance += diff
                account_debited.save(using=db)
                CreateLog(db, account_debited, diff)
        else:
            loan.save(using=db)

    messages.success(request, "Loan updated successfully")
    return True

