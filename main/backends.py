from django.contrib.auth.backends import ModelBackend

from .models import User


class EmailAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, *args, **kwargs):
        if username is None or password is None:
            return None
        identifier = str(username).strip()
        if not identifier:
            return None
        user = (
            User.objects.filter(email__iexact=identifier).first()
            or User.objects.filter(username__iexact=identifier).first()
        )
        if user is None:
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id: int):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None





