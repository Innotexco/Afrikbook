from settings.forms import UserForm, UserUpdateForm
from settings.models import user
from django.contrib import messages

def add_user(request):
    form = UserForm(request.POST or None)
    
    password = request.POST["password"]
    confirm_password = request.POST["confirm_password"]

    if confirm_password != password:
        messages.error(request, "Password and confirm Password does not match")
    else:
        if form.is_valid():
            form.save()
            messages.success(request, "User was added successfully")
        else:
            messages.error(request, "Create user was unsuccessful")

def update_user(request, id):
    users = user.objects.get(id=id)
    form = UserUpdateForm(request.POST or None, instance=users)
    if request.method == "POST":
        if form.is_valid():
            form.save()