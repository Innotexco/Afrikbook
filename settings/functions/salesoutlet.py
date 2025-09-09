from settings.forms import SalesOutletForm 
from settings.models import sales_outlet,CreateProfile
from main.models import User, currency, company_table
from django.contrib import messages


def add_sales_outlet(request, db):
    form = SalesOutletForm (request.POST or None)

    country = request.POST['country']
    cu = currency.objects.get(Country=country).Currency

    if form.is_valid():
        form_i = form.save(commit=False)
        form_i.currency = cu
        form_i.Userlogin = request.user.username
        form_i.save(using=db)
        messages.success(request, "Sales Outlet was added successfully")
    else:
        messages.error(request, "Create Sales Outlet was unsuccessful")

def update_sales_outlet(request, id, db):
    Users =sales_outlet.objects.using(db).get(id=id)
    form = SalesOutletForm (request.POST, instance=Users)

    if form.is_valid():
        form_i = form.save(commit=False)
        form_i.save(using=db)
        messages.success(request, "Sales Outlet was updated successfully")
    else:
        messages.error(request, "Create Sales Outlet was unsuccessful")



def get_currency(request):
    db = request.user.company_id.db_name
    user = User.objects.get(id=request.user.id)
   
    if user.outlet is None or user.outlet == "":
        
        currency_ = CreateProfile.objects.using(db).get(country=user.company_id.country).Currency
    else:
        
        currency_ = currency.objects.get(Country=user.company_id.country).currency
    return currency_
