from django.shortcuts import redirect
from main.models import Privilege
from django.contrib import messages
from main.functions.verification import check_sub
from django.urls import reverse
def urls_name(name):
    # print(name)

    def user_page_permission(view_function):
        def wrapper(request, *args, **kwargs):
              
            db = request.user.company_id.db_name
            if request.user.is_authenticated:
                remaining_days, plan = check_sub(request, request.user.company_id.id)
            
                if remaining_days <= 0:
                    billing_url = reverse('main:Billing', args=[request.user.company_id.id])
                    return redirect(billing_url)
                else:
                    Privileges = Privilege.objects.filter(name=name,is_active = 1, user_id=request.user.id)
                    if Privileges.exists():
                        return view_function(request, *args, **kwargs)
                    else:
                        messages.error(request, "You dont have the privilage to access "+name+" page")
                        return redirect('main:home')
                    
            else:
                return view_function(request, *args, **kwargs)
                
        return wrapper
    return user_page_permission




def auto_renew(request):
    print("auto renew")