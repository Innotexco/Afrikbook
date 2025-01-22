from settings.forms import PriceChangeForm
from settings.models import pricechange_history
from django.contrib import messages


def add_price_management(request, db):
    form = PriceChangeForm(request.POST or None)
    
    if form.is_valid():
        form_i = form.save(commit=False)
        form_i.Userlogin = request.user.username
        form_i.save(using=db)
        messages.success(request, "Price History added successfully")

def update_price_management(request, id, db):
    price_history = pricechange_history.objects.using(db).get(id=id)
    form = PriceChangeForm(request.POST or None, instance=price_history)
    if request.method == "POST":
        if form.is_valid():
            form_i = form.save(commit=False)
            form_i.save(using=db)
            messages.success(request, "Price History Update successfully")