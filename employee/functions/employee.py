from employee.forms import EmployeeForm, EmployeeGurantorForm, EmployeeAccountForm
from employee.models import employee, employee_guarantor, employee_account_details
from django.contrib import messages



def add_employee(request, db):
    form = EmployeeForm(request.POST or None)
    account_form = EmployeeAccountForm(request.POST or None)
    eg_form = EmployeeGurantorForm(request.POST or None)
    
    if form.is_valid() and eg_form.is_valid() and account_form.is_valid():
        form_i = form.save(commit=False)
        form_i.Userlogin = request.user.username
        form_i.save(using=db)
        
        account = account_form.save(commit=False)
        account.employee_id = form_i.staff_ID
        account.save(using=db)
        
        employee_g = eg_form.save(commit=False)
        employee_g.employee_id = form_i.id
        employee_g.save(using=db)

        messages.success(request, "Employee was added successfully")
    # else:
       
        
def update_employee(request, id, db):
    Employee = employee.objects.using(db).get(id=id)
    account = employee_account_details.objects.using(db).get(employee_id=Employee.staff_ID)
    Employeeg = employee_guarantor.objects.using(db).get(employee_id=id)

    form = EmployeeForm(request.POST or None, instance=Employee)
    account_form = EmployeeAccountForm(request.POST or None, instance=account)
    eg_form = EmployeeGurantorForm(request.POST or None, instance=Employeeg)
    if form.is_valid() and eg_form.is_valid() and account_form.is_valid():
        form_i = form.save(commit=False)
        form_i.save(using=db)

        account_form_i = account_form.save(commit=False)
        account_form_i.save(using=db)

        eg_form_i = eg_form.save(commit=False)
        eg_form_i.save(using=db)
        messages.success(request, "Employee was updated successfully")
    else:
        messages.success(request, "Employee was not updated")