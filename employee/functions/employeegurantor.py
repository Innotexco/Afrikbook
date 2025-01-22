from employee.forms import EmployeeGurantorForm
from employee.models import employee_guarantor
from django.contrib import messages


def add_employee_guarantor(request):
    form = EmployeeGurantorForm(request.POST or None)
    if form.is_valid():
        form.save()
        # messages.success(request, "Employee  was added successfully")
    # else:
  
def update_employee_guarantor(request, id):
    Employee_guarantor = employee_guarantor.objects.get(id=id)
    form = EmployeeGurantorForm(request.POST or None, instance=Employee_guarantor)
    if form.is_valid():
        form.save()
        # messages.success(request, "Employee was updated successfully")
    else:
        pass
     