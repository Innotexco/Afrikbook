from functools import wraps
from django.shortcuts import redirect
# from .models import User_Permission

def not_logged_in_required(view_function):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:home')
        else:
            return view_function(request, *args, **kwargs)
            
    return wrapper



# def Permission_required(view_function):
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             user = User_Permission.objects.all()  
#             if user.pages != "priviledge" and user.status != 1:
#                 return redirect('main:home')
#         else:
#             return view_function(request, *args, **kwargs)
            
#     return wrapper


# def Permission_required(view_function):
#     @wraps(view_function)
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             user = User_Permission.objects.get(user=request.user)  # Adjust the query based on your actual model and field names

#             if user.pages != "privilege" or user.status != 1:
#                 return redirect('main:home')  # Redirect to 'main:home' if the conditions are not met
#         else:
#             return view_function(request, *args, **kwargs)

#         return view_function(request, *args, **kwargs)

#     return wrapper