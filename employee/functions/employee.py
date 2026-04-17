from employee.forms import EmployeeForm, EmployeeGurantorForm, EmployeeAccountForm
from employee.models import employee, employee_guarantor, employee_account_details
from django.contrib import messages



def add_employee(request, db):
    form = EmployeeForm(request.POST or None)
    account_form = EmployeeAccountForm(request.POST or None)
    eg_form = EmployeeGurantorForm(request.POST or None)
    
    if form.is_valid() and account_form.is_valid():
        form_i = form.save(commit=False)
        form_i.Userlogin = request.user.username

        # Strip commas from basic_salary before saving
        if form_i.basic_salary:
            form_i.basic_salary = str(form_i.basic_salary).replace(',', '')
        
        form_i.save(using=db)
        
        account = account_form.save(commit=False)
        account.employee_id = form_i.staff_ID
        account.save(using=db)
        
        if eg_form.is_valid():
            employee_g = eg_form.save(commit=False)
            employee_g.employee_id = form_i.id
            employee_g.save(using=db)

        messages.success(request, "Employee was added successfully")
        return True  
    return False
       
        
def update_employee(request, id, db):
    Employee = employee.objects.using(db).get(id=id)

    try:
        account = employee_account_details.objects.using(db).get(employee_id=Employee.staff_ID)
    except employee_account_details.DoesNotExist:
        account = None

    try:
        Employeeg = employee_guarantor.objects.using(db).get(employee_id=id)
    except employee_guarantor.DoesNotExist:
        Employeeg = None

    form = EmployeeForm(request.POST, instance=Employee)
    account_form = EmployeeAccountForm(request.POST, instance=account) if account else EmployeeAccountForm(request.POST)
    eg_form = EmployeeGurantorForm(request.POST, instance=Employeeg) if Employeeg else EmployeeGurantorForm(request.POST)

    if form.is_valid():
        form_i = form.save(commit=False)
        
        # Strip commas from basic_salary
        if form_i.basic_salary:
            form_i.basic_salary = str(form_i.basic_salary).replace(',', '')
        
        form_i.save(using=db)

        # Save account only if form has data
        if account_form.is_valid():
            account_i = account_form.save(commit=False)
            account_i.employee_id = Employee.staff_ID
            account_i.save(using=db)

        # Save guarantor only if form has data and is valid
        if eg_form.is_valid():
            eg_i = eg_form.save(commit=False)
            eg_i.employee_id = id
            eg_i.save(using=db)

        messages.success(request, "Employee was updated successfully")
        return True

    messages.error(request, "Employee was not updated. Please check the required fields.")
    return False