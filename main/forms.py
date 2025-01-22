from django import forms

from .models import User, Privilege, Pages, Billing


class LoginForm(forms.Form):
    username = forms.CharField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)





class UserRegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "email", "password", "company_id")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        model = self.Meta.model
        user = model.objects.filter(username__iexact = username)

        if user.exists():
            raise forms.ValidationError("A user with that name already exists!")
        return self.cleaned_data.get('username')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        model = self.Meta.model
        user = model.objects.filter(email__iexact = email)

        if user.exists():
            raise forms.ValidationError("A user with that email already exists!")
        return self.cleaned_data.get('email') 

    def clean_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        # if password != confirm_password:
        #     raise forms.ValidationError("Password does not match")
        
        return self.cleaned_data.get('password')





class NewUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ( "email", "password","priviledge")

    username = forms.CharField(required=False)

class PrivilegeForm(forms.ModelForm):
    class Meta:
        model = Privilege
        fields = '__all__'





class PagesForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = '__all__'


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = '__all__'
        exclude = ['reference', 'date', 'subscription',]


















class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'Userlogin',
            'priviledge',
            'outlet',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UserSettingsForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['username'].disabled = True

    def save(self):
        user = super(UserSettingsForm, self).save()
        return user


# class UserPermissonsForm(forms.ModelForm):
#     class Meta:
#         model = Permission
#         fields = (
#             'name',
#             'content_type',
#             'codename',
#         )



# class PermissonGrantForm(forms.ModelForm):
#     class Meta:
#         model = User_Permission
#         fields = (
#             'status',
#             'access',
#         )








class EditUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)

        def get_label(obj):
            permission_name = str(obj).split('|')[2].strip()
            model_name = permission_name.split(' ')[2].strip()
            return '%s | %s' % (model_name.title(), permission_name)

        # User = get_user_model()
        content_type = ContentType.objects.get_for_model(User)
        self.fields['user_permissions'].queryset = Permission.objects.filter(content_type=content_type)
        self.fields['user_permissions'].widget.attrs.update({'class': 'permission-select'})
        self.fields['user_permissions'].help_text = None
        self.fields['user_permissions'].label = "Label"
        self.fields['user_permissions'].label_from_instance = get_label

    def save(self, commit=True):
        user_instance = super(EditUserForm, self).save(commit)
        user_instance.save()
        user_instance.user_permissions.set(self.cleaned_data.get('user_permissions'))
        return user_instance

    class Meta:
        model = User
        fields = ['username', 'password', 'outlet', 'user_permissions']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'outlet': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'user_permissions': forms.SelectMultiple(attrs={'style': 'width: 350px; height: 200px;'})
        }











