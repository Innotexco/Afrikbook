from django.contrib.auth.base_user import BaseUserManager

class CustomVendorManager(BaseUserManager):
    def create_user(self, name, email, phone, **extra_fields):
        if not name:
            raise ValueError("The vendor name must be set")
        
        if not email:
            raise ValueError("The email must be set")
        
        
        email = self.normalize_email(email)
        vendor = self.model(
            name=name,
            email=email,
            phone=phone,
            **extra_fields
        )
        vendor.save()
        return vendor
        





