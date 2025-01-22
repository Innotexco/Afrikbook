from employee.forms import PayRollForm
from employee.models import payroll
from django.contrib import messages


def add_payroll(request, db):

    message_display = False

    month = request.POST.get('month')
    year = request.POST.get('year')
    employee_name = request.POST.getlist('name[]')
    staffID = request.POST.getlist('staff_ID[]')
    bsaic_salary = request.POST.getlist('salary[]')
    overtime = request.POST.getlist('overtime[]')
    allowance = request.POST.getlist('allowance[]')
    others = request.POST.getlist('others[]')
    gross_pay = request.POST.getlist('gross-pay[]')
    tax = request.POST.getlist('tax[]')
    loan_repay = request.POST.getlist('loan-repay[]')
    union_pay = request.POST.getlist('union-pay[]')
    sanction = request.POST.getlist('sanction[]')
    NHF = request.POST.getlist('NHF[]')
    NSIFT = request.POST.getlist('NSIFT[]')
    other_deduction = request.POST.getlist('other-deductions[]')
    total_due = request.POST.getlist('total-dues[]')
    net_pay = request.POST.getlist('net-pay[]')

    if month is None:
        messages.error(request, 'Select month')
    elif year is None:
        messages.error(request, 'Select Year')
    elif payroll.objects.using(db).filter(month_year=month+'_'+year).exists():
        messages.error(request, 'Payroll for the selected month and year already exists')
    else:  
        for i in range(len(employee_name)):
            
            form_data = {
                'month_year': month+'_'+year,
                'employee_name' :employee_name[i],
                'staffID': staffID[i],
                'bsaic_salary': bsaic_salary[i],
                'overtime': overtime[i],
                'allowance': allowance[i],
                'others': others[i],
                'gross_pay': gross_pay[i],
                'tax': tax[i],
                'loan_repay':loan_repay[i],
                'union_pay': union_pay[i],
                'sanction': sanction[i],
                'NHF': NHF[i],
                'NSIFT': NSIFT[i],
                'other_deduction': other_deduction[i],
                'total_due': total_due[i],
                'net_pay': net_pay[i]
            }
            form = PayRollForm(form_data)

            if form.is_valid():
                form_i = form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.save(using=db)
                
                if not message_display:
                    messages.success(request, month+"-"+year+" Payroll has been created successfully")
                    message_display = True
            else:
                if not message_display:
                    messages.error(request, "unsuccessful")
                    message_display = True
                
