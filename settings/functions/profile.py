# from settings.forms import ProfileForm
# from settings.models import profile
# from django.contrib import messages

# def create_profile(request):
#     form = ProfileForm (request.POST or None, request.FILES)
#     # logo = request.POST['logo']

#     if form.is_valid():
#         form.save()
#         messages.success(request, "Profile was created successfully")
#     else:
#         

# def update_profile(request, id):
#     users = profile.objects.get(id=id)
#     form = ProfileForm (request.POST, instance=users)
#     if form.is_valid():
#         form.save()
#         messages.success(request, "Profile was updated successfully")
#     else:
#         messages.error(request, "Create Profile was unsuccessful")
