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

def create_new_loan(request, db):
    loan_form = LoanAccountForm(request.POST)
    loan_log_form = LoanAccountLogForm(request.POST)

    date = request.POST['date']
    employee_id = request.POST.get('employee_id')
    customer_id = request.POST.get('customer_id')
    vendor_id = request.POST.get('vendor_id')
    account = request.POST.get('account_debited')
    description = request.POST['description']
    amount_borrowed = request.POST['amount_borrowed']
    amount_paid = request.POST['amount_paid']


    debtor_id = None
    debtor_name = None

    if account is None:
        messages.error(request, "Please select account")
    else:
        account_debited = chart_of_account.objects.using(db).get(account_id=account)
        if employee_id:
            debtor_id = employee_id
            debtor_name = employee.objects.using(db).get(staff_ID=employee_id).fullname
        elif customer_id:
            debtor_id = customer_id
            debtor_name = customer_table.objects.using(db).get(customer_code=customer_id).name
        elif vendor_id:
            debtor_id = vendor_id
            debtor_name = vendor_table.objects.using(db).get(custID=vendor_id).name
        else:
            messages.error(request, "Select Employee, Customer or Vendor")
            
        if amount_borrowed and amount_paid:
            balance_left = int(amount_borrowed) - int(amount_paid)
        else:
            balance_left = ""
       


        # Generate a new transaction ID
        transaction_id = uuid.uuid4()

        form_data = {"date":date,"debtor_name":debtor_name, "debtor_id": debtor_id, "description": description, "amount_borrowed": amount_borrowed, "amount_paid": amount_paid, "balance_left": balance_left, "account_debited":account_debited.account_id}
        
        loan_form = LoanAccountForm(form_data)
        loan_log_form = LoanAccountLogForm(form_data)

        if loan_form.is_valid() and loan_log_form.is_valid():
                
            if employee_id: 
                #get staf last account balance 
                if staff_account.objects.using(db).filter(staff_id=debtor_id).exists():
                    initial_bal = staff_account.objects.using(db).filter(staff_id=debtor_id).last().balance
                else: 
                    initial_bal = decimal.Decimal(0.00)
                
                if initial_bal > 0:
                        balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount_borrowed)
                else:
                    balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount_borrowed)

                # insert into staff account   
                staff = staff_account(
                    date = date, staff_id = debtor_id,
                    staff_name = debtor_name, amount =amount_borrowed, 
                    initial_amount = initial_bal,
                    balance = balance,
                    account_posted = account_debited.account_id,
                    description = description, 
                    payment_method = "Cash",invoice_status = "Unused", transaction_id=transaction_id,
                    Userlogin = request.user.username)
                staff.save(using=db)
            elif customer_id:
                #debit customer recievable balance 
                cus = customer_table.objects.using(db).get(customer_code=customer_id)
                DebitReceivable(request, db, cus, date, description, "Cash", account, amount_borrowed)  
            elif vendor_id:
                #debit vendor  payable balance 
                ven = vendor_table.objects.using(db).get(custID=vendor_id)
                DebitPayable(request, db, ven, date, description, "Cash", account, amount_borrowed)
               
                
                
            loan_instance = loan_form.save(commit=False)
            loan_instance.transaction_id = transaction_id
            loan_instance.save(using=db)

            loan_log_instance = loan_log_form.save(commit=False)
            loan_log_instance.transaction_id = transaction_id
            loan_log_instance.save(using=db)

            #account debited 
            account_debited.actual_balance += decimal.Decimal(amount_borrowed)
            # account_debited.save()
            CreateLog(db, account_debited, amount_borrowed)

            
            #create account log
            acc_log = account_log(
                transaction_source  = "Loan",
                amount              = amount_borrowed,
                date                = date,
                account             = account_debited.account_id,
                account_type        = account_debited.account_type,
                Userlogin = request.user.username
            )
            # acc_log.save(using=db)
            messages.success(request, "Payment Received")
        else:
            
            return loan_form


