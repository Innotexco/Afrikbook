from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from account.models import *
from .forms import *
from .functions.employee import *
from .functions.employeegurantor import *
from .functions.payroll import *
import decimal, uuid, datetime
from datetime import datetime, date
from django.db.models import Sum
from account.models import chart_of_account
from customer.functions.generalFunction import *
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name



# Create your views here.

# Employee
@login_required(login_url='/')
@urls_name(name="Employee")
def ViewEmployee(request):
    db = request.user.company_id.db_name
    Employee = employee.objects.using(db).all()
    context = {
        'employee': Employee
    }
    return render(request, "employee/ViewEmployee.html", context)

@login_required(login_url='/')
@urls_name(name="Employee")
def AddEmployee(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        email = request.POST['email']
        if employee.objects.using(db).filter(email=email).exists():
            messages.success(request, "Email already exists")
        else:
            add_employee(request, db)
   
    return render(request, "employee/NewEmployee.html")

@login_required(login_url='/')
@urls_name(name="Employee")
def UpdateEmployee(request, id):
    db = request.user.company_id.db_name
    Employee = employee.objects.using(db).get(id=id)
    Employee_account = employee_account_details.objects.using(db).get(employee_id=Employee.staff_ID)
    Employeeg = employee_guarantor.objects.using(db).get(employee_id=id)
    if request.method == "POST":
        update_employee(request, id, db)
        return redirect("employee:Employee")
        # update_employee_guarantor(request, id)
    context = {
        "employee": Employee,
        "account": Employee_account,
        "employeeg": Employeeg      
    }
    return render(request, "employee/UpdateEmployee.html", context)

@login_required(login_url='/')
@urls_name(name="Employee")
def DeleteEmployee(request, id):
    db = request.user.company_id.db_name
    employe = employee.objects.using(db).get(id=id)
    employe_account = employee_account_details.objects.using(db).get(employee_id=employe.staff_ID)
    employe_guarantor = employee_guarantor.objects.using(db).get(employee_id=id)

    employe.delete()
    employe_account()
    employe_guarantor.delete()
    messages.error(request, "Employee was deleted successfully")
    return redirect("employee:Employee") 

# Payroll
@login_required(login_url='/')
@urls_name(name="Payroll")
def ViewPayroll(request):
    db = request.user.company_id.db_name
    today_date = date.today()
    year = datetime.today().year
   
    years = range(year, year - 10, -1)
    Payroll = payroll.objects.using(db).filter(dateG=today_date)
    amount_total = payroll.objects.using(db).filter(dateG=today_date).values("staffID").distinct().aggregate(total_amount=Sum("net_pay"))['total_amount']
    context = {
        'Payroll': Payroll,
        'total':amount_total,
        'date':today_date,
        'years': years
    }
    return render(request, "employee/ViewPayroll.html", context)

@login_required(login_url='/')
@urls_name(name="Payroll")
def AddPayroll(request):
    db = request.user.company_id.db_name
    employe = employee.objects.using(db).all()
    year = datetime.today().year
    years = range(year, year - 10, -1)
    if request.method == "POST":
        add_payroll(request, db)
    context = {
        'employee':employe,
        'years':years
    }
    return render(request, "employee/NewPayroll.html", context)

def payroll_filter_by_date(request):
    db = request.user.company_id.db_name
    month = request.GET.get('month')
    year = request.GET.get('year')

    month_year = str(month+"_"+year)

    # Perform filtering based on month and year
    filtered_data = payroll.objects.using(db).filter(month_year=month_year).values().distinct()

    amount_total = payroll.objects.using(db).filter(month_year=month_year).values("staffID").distinct().aggregate(total_amount=Sum("net_pay"))['total_amount']
    
    serializer_data = list(filtered_data)

    data ={
        'amount_total':amount_total,
        'serializer_data':serializer_data
    }

    return JsonResponse(data, safe=False)

@login_required(login_url='/')
@urls_name(name="Salary Approval")
def ViewUnapprovePayroll(request):
    db = request.user.company_id.db_name
    accounts = chart_of_account.objects.using(db).all()
    payrolls = payroll.objects.using(db).values('month_year').distinct()
   
    unique_payroll = []
    for pay in payrolls:
        new_paryroll = payroll.objects.using(db).filter(month_year = pay['month_year'], status="upapprove")
        if new_paryroll.exists():
            unique_payroll.append(new_paryroll.first())
    for i in unique_payroll:
        i.total = payroll.objects.using(db).aggregate(total=Sum('bsaic_salary'))['total']

    if request.method == "POST":
        add_payroll(request)
    context = {
        'accounts':accounts,
        # 'payrolls':unique_payroll
    }
    return render(request, "employee/ApprovePayroll.html", context)

def FetchUnapprovedPayroll(request):
    db = request.user.company_id.db_name
    payrolls = payroll.objects.using(db).values('month_year').distinct()
    unique_payroll = []

    for pay in payrolls:
        new_paryroll = payroll.objects.using(db).filter(month_year=pay['month_year'], status='unapprove').values()
        total_salary = payroll.objects.using(db).filter(month_year=pay['month_year'], status='unapprove').aggregate(total=Sum('net_pay'))['total']

        if new_paryroll.exists():
            new_paryroll = new_paryroll.first()
            new_paryroll['total'] = total_salary
            unique_payroll.append(new_paryroll)

    return JsonResponse(list(unique_payroll), safe=False)

@login_required(login_url='/')
@urls_name(name="Salary Approval")
def ViewApprovePayroll(request):
    db = request.user.company_id.db_name
    accounts = chart_of_account.objects.using(db).all()
    payrolls = payroll.objects.using(db).values('month_year').distinct()
   
    unique_payroll = []
    for pay in payrolls:
        new_paryroll = payroll.objects.using(db).filter(month_year = pay['month_year'], status="approve")
        if new_paryroll.exists():
            unique_payroll.append(new_paryroll.first())
    for i in unique_payroll:
        i.total = payroll.objects.using(db).aggregate(total=Sum('bsaic_salary'))['total']

    if request.method == "POST":
        add_payroll(request, db)
    context = {
        'accounts':accounts,
        # 'payrolls':unique_payroll
    }
    return render(request, "employee/ViewApprovePayroll.html", context)

def FetchApprovedPayroll(request):
    db = request.user.company_id.db_name
    payrolls = payroll.objects.using(db).values('month_year').distinct()
    unique_payroll = []

    for pay in payrolls:
        new_paryroll = payroll.objects.using(db).filter(month_year=pay['month_year'], status='approve').values()
        total_salary = payroll.objects.using(db).filter(month_year=pay['month_year'], status='approve').aggregate(total=Sum('net_pay'))['total']

        if new_paryroll.exists():
            new_paryroll = new_paryroll.first()
            new_paryroll['total'] = total_salary
            unique_payroll.append(new_paryroll)

    return JsonResponse(list(unique_payroll), safe=False)

def Payrolls(request):
    db = request.user.company_id.db_name
    data = request.GET.get('data')
    Payroll = payroll.objects.using(db).filter(month_year=data).values()
    total= payroll.objects.using(db).filter(month_year=data).aggregate(total=Sum('net_pay'))['total']

    executed = False
    
    serialze = list(Payroll)
    data = {
        'data':serialze,
        'total':total
    }
    
    return JsonResponse(data, safe=False)

def ApprovedPayrolls(request):
    db = request.user.company_id.db_name
    data = request.GET.get('data')
    Payrolls = payroll.objects.using(db).filter(month_year=data).values()
    
    pay_account = []

    for pay in Payrolls:
        new_data = payroll.objects.using(db).filter(month_year=data, staffID=pay['staffID']).values()
        
        account_details = employee_account_details.objects.using(db).filter(employee_id=pay['staffID']).first()
        
        if new_data and account_details:
            new_data = new_data.first()
            new_data['account_no'] = str(account_details.account_no)
            new_data['account_name'] = account_details.account_name
            new_data['bank_name'] = account_details.bank_name
            pay_account.append(new_data)

    total= payroll.objects.using(db).filter(month_year=data).aggregate(total=Sum('net_pay'))['total']
  
    serialze = list(pay_account)
    data = {
        'data':serialze,
        'total':total
    }
    
    return JsonResponse(data, safe=False)

def Payroll(request):
    db = request.user.company_id.db_name
    id = request.GET.get('id')
    staffID = request.GET.get('staffID')
    Payroll = payroll.objects.using(db).filter(id=id, staffID=staffID).values()
   

    serialze = list(Payroll)
    
    return JsonResponse(serialze, safe=False)

def SaveChanges(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        id = request.POST.get('id')
        month = request.POST.get('month[]')
        employee_name = request.POST.get('name[]')
        staffID = request.POST.get('staff_ID[]')
        bsaic_salary = request.POST.get('salary[]')
        overtime = request.POST.get('overtime[]')
        allowance = request.POST.get('allowance[]')
        others = request.POST.get('others[]')
        gross_pay = request.POST.get('gross-pay[]')
        tax = request.POST.get('tax[]')
        loan_repay = request.POST.get('loan-repay[]')
        union_pay = request.POST.get('union-pay[]')
        sanction = request.POST.get('sanction[]')
        NHF = request.POST.get('NHF[]')
        NSIFT = request.POST.get('NSIFT[]')
        other_deduction = request.POST.get('other-deductions[]')
        total_due = request.POST.get('total-dues[]')
        net_pay = request.POST.get('net-pay[]')
       
        form_data = {
                'month_year': month,
                'employee_name' :employee_name,
                'staffID': staffID,
                'bsaic_salary': bsaic_salary,
                'overtime': overtime,
                'allowance': allowance,
                'others': others,
                'gross_pay': gross_pay,
                'tax': tax,
                'loan_repay':loan_repay,
                'union_pay': union_pay,
                'sanction': sanction,
                'NHF': NHF,
                'NSIFT': NSIFT,
                'other_deduction': other_deduction,
                'total_due': total_due,
                'net_pay': net_pay
            }
        form_instance = payroll.objects.using(db).get(id=id, staffID=staffID)
        form = PayRollForm(form_data, instance=form_instance)
        
        
        if form.is_valid():
            form_i = form.save(commit=False)
            form_i.save(using=db)
            return JsonResponse(data=staffID, safe=False)
        else:
           
            return JsonResponse(data=None, safe=False) 
        
def ApprovePayroll(request):
    db = request.user.company_id.db_name
    if request.method == "GET":
        account = request.GET.get('account')
        c_account = request.GET.get('c-account')
        month_year = request.GET.get('month_year')
        total_salary = request.GET.get('total_salary')

        account = chart_of_account.objects.using(db).get(account_id=account)
        c_account = chart_of_account.objects.using(db).get(account_id=c_account)
        payrolls = payroll.objects.using(db).filter(month_year=month_year)

        
        form = PayRollLogForm({'month_year':month_year, 'Amount':total_salary,'status':"Approved", 'account_debited':account.account_id})
        dater = date.today()

        if account and c_account:
           if account.actual_balance >= decimal.Decimal(total_salary):
                
                   
                    if form.is_valid():
                            # create payroll log 
                            form_i = form.save(commit=False)
                            form_i.Userlogin = request.user.username
                            form.save(using=db)

                            #   Debit account
                            account.actual_balance -= decimal.Decimal(total_salary)
                            account.save()
                            CreateLog(db, account, total_salary)

                            #   Credit account
                            c_account.actual_balance += decimal.Decimal(total_salary)
                            c_account.save()
                            CreateLog(db, c_account, total_salary)

                            #   Update payroll status
                            payrolls.update(status='Approve')

                            # create debit account log 
                            debit_acc_log = account_log(
                                transaction_source  = "Salary",
                                amount              = total_salary,
                                date                = date.today(),
                                account             = account.account_id,
                                account_type        = account.account_type,
                                Userlogin           = request.user.username
                            )
                            # debit_acc_log.save(using=db)

                            # create credit account log 
                            credit_acc_log = account_log(
                                transaction_source  = "Salary",
                                amount              = total_salary,
                                date                = date.today(),
                                account             = c_account.account_id,
                                account_type        = c_account.account_type,
                                Userlogin           = request.user.username
                            )
                            # credit_acc_log.save(using=db)

                            #credit staff
                            # Generate a new transaction ID
                            transaction_id = uuid.uuid4()
                            for i in payrolls:
                                staff = employee.objects.using(db).get(staff_ID=i.staffID)
                                # net_pay = payroll.objects.using(db).get(month_year=month_year, staffID=i.staffID).net_pay
                                loan_repay = payroll.objects.using(db).get(month_year=month_year, staffID=i.staffID).loan_repay

                                if loan_repay > 0:
                                    #get staf last account balance 
                                    if staff_account.objects.using(db).filter(staff_id=i.staffID).exists():
                                        initial_bal = staff_account.objects.using(db).filter(staff_id=i.staffID).last().balance
                                    else: 
                                        initial_bal = 0.00
                                    
                                    if initial_bal > 0:
                                        balance = decimal.Decimal(initial_bal) - decimal.Decimal(loan_repay)
                                    else:
                                        balance = decimal.Decimal(initial_bal) + decimal.Decimal(loan_repay)

                                    # insert into staff accpunt   
                                    staff = staff_account(
                                        date = dater, staff_id = staff.staff_ID,
                                        staff_name = staff.fullname, amount =loan_repay, 
                                        initial_amount = initial_bal,
                                        balance = balance,
                                        account_posted = c_account.account_id,
                                        description ="Loan Repayment", type = "Credit", 
                                        payment_method = "Transfer",invoice_status = "Unused",
                                        transaction_id = transaction_id,
                                        Userlogin = request.user.username)
                                    staff.save(using=db)

                            
                            return JsonResponse({'type':'success','message': month_year+" Salary Approved"})
                    else:
                        return JsonResponse({'type':'error','message':"Approve Payroll Unsuccessful"}) 
           else:
              return JsonResponse({'type':'error','message':"Insufficient funds"})       
        else:
            return JsonResponse({'type':'error','message':"Account does not exists"})
        
def ConfirmPayment(request):
    db = request.user.company_id.db_name
    if request.method == "GET":
        id = request.GET.get('id')
        staffID = request.GET.get('staff_id')
        amount = request.GET.get('amount')

        payrolls = payroll.objects.using(db).get(id=id, staffID=staffID)
       
        if payrolls:
            if payrolls.confirm_payment == 'pending':
                #   Update payroll status
                payrolls.confirm_payment='confirmed'
                payrolls.save()

                return JsonResponse({'type':'success','message': "Confirm Payment Successful"})
            else:
                return JsonResponse({'type':'error','message':"Confirm Payment Unsuccessful"})         
        else:
            return JsonResponse({'type':'error','message':"Staff does not exists"})
        
def ConfirmAllPayment(request):
    db = request.user.company_id.db_name
    if request.method == "GET":
        month_year = request.GET.get('month_year')

        payrolls = payroll.objects.using(db).filter(month_year=month_year)

       
        if payrolls.exists():
            if payroll.objects.using(db).filter(confirm_payment='pending'):
                #   Update payroll status
                payrolls.update(confirm_payment='confirmed')

                return JsonResponse({'type':'success','message': "Confirm Payment Successful"})
            else:
                return JsonResponse({'type':'error','message':"Confirm Payment Unsuccessful"})         
        else:
            return JsonResponse({'type':'error','message':"Staffs does not exists"})

       


