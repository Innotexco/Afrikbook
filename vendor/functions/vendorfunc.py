from django.shortcuts import redirect
from django.contrib import messages 
from ..models import vendor_table
from vendor.forms import(
    VendorRegistrationForm,
    VendorUpdateForm
)



# New Purchase
# def GetVendorDetails(request, id):
#     try:
#         vendor = vendor_table.objects.get(pk=id)
#         data = {
#                 'name': vendor.name,
#                 'phone': vendor.phone,
#                 'email': vendor.email,
#                 'Customer ID': vendor.custID,
#                 'company': vendor.company_name,
#                 'address': vendor.address,
#             }
#         return JsonResponse(data)
#     except vendor_table.DoesNotExist: 
#         return JsonResponse({'error': 'Item not found'}, status=404)




def add_vendor(request, db):
   
    form = VendorRegistrationForm(request.POST)
    email = request.POST.get('email')
    try:
        vendor_table.objects.using(db).get(email=email)
        messages.success(request, "Email alredy exists")
    except vendor_table.DoesNotExist:
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.Userlogin = request.user.username
            vendor.save(using=db)
            messages.success(request, "Vendor Add Successful")
            return redirect('vendor:register_vendor')


def edit_vendor(request, id, db):

    vendor = vendor_table.objects.using(db).get(id = id)
    form = VendorUpdateForm(request.POST, instance=vendor)

    if form.is_valid():
        vendor = form.save(commit=False)
        vendor.Userlogin = request.user.username
        vendor.save(using=db)
        messages.success(request, "Vendor data has been updated successfully")
        
