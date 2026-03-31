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

def create_new_loan(request, db):
    try:
        #Safely get POST data
        date = request.POST.get('date')
        employee_id = request.POST.get('employee_id')
        customer_id = request.POST.get('customer_id')
        vendor_id = request.POST.get('vendor_id')
        account = request.POST.get('account_debited')
        description = request.POST.get('description')
        amount_borrowed = request.POST.get('amount_borrowed')

        # Basic validation
        if not all([date, account, description, amount_borrowed]):
            messages.error(request, "All required fields must be filled")
            return None

        try:
            amount_borrowed = decimal.Decimal(amount_borrowed)
        except:
            messages.error(request, "Invalid amount")
            return None

        #Get account safely
        try:
            account_debited = chart_of_account.objects.using(db).get(account_id=account)
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

        balance_left = amount_borrowed
        transaction_id = uuid.uuid4()

        form_data = {
            "date": date,
            "debtor_name": debtor_name,
            "debtor_id": debtor_id,
            "description": description,
            "amount_borrowed": amount_borrowed,
            "balance_left": balance_left,
            "account_debited": account_debited.account_id
        }

        loan_form = LoanAccountForm(form_data)
        loan_log_form = LoanAccountLogForm(form_data)

        if not (loan_form.is_valid() and loan_log_form.is_valid()):
            messages.error(request, "Invalid form data")
            return loan_form

        #ATOMIC TRANSACTION (VERY IMPORTANT)
        with transaction.atomic():

            if employee_id:
                last_record = staff_account.objects.using(db).filter(staff_id=debtor_id).last()
                initial_bal = last_record.balance if last_record else decimal.Decimal("0.00")

                balance = initial_bal + amount_borrowed

                staff_account.objects.using(db).create(
                    date=date,
                    staff_id=debtor_id,
                    staff_name=debtor_name,
                    amount=amount_borrowed,
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
                DebitReceivable(request, db, cus, date, description, "Cash", account, amount_borrowed)

            elif vendor_id:
                DebitPayable(request, db, ven, date, description, "Cash", account, amount_borrowed)

            #Save loan
            loan_instance = loan_form.save(commit=False)
            loan_instance.transaction_id = transaction_id
            loan_instance.save(using=db)

            #Save log
            loan_log_instance = loan_log_form.save(commit=False)
            loan_log_instance.transaction_id = transaction_id
            loan_log_instance.save(using=db)

            #Update account balance
            account_debited.actual_balance += amount_borrowed
            CreateLog(db, account_debited, amount_borrowed)

            #Log entry
            account_log.objects.using(db).create(
                transaction_source="Loan",
                amount=amount_borrowed,
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


