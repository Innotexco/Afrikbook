
# from main.db_router import add_db_connection

# class DatabaseMiddleware:
#     """Middleware to set the database for each request."""

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Assume user is authenticated and has a company_id attribute
#         if hasattr(request.user, "company_id"):
#             # print(f"⚡ Middleware setting DB: {request.user.company_id.db_name}")  # Debugging
#             add_db_connection(request.user.company_id.db_name)

#         response = self.get_response(request)
#         return response






















from django.utils.deprecation import MiddlewareMixin
# from main.thread_local import set_tenant_db

import threading

# Thread-local storage for the database name
thread_local = threading.local()

def set_tenant_db(db_name):
    """Store the database name in the current thread."""
    thread_local.db_name = db_name

def get_tenant_db():
    """Retrieve the database name for the current request."""
    return getattr(thread_local, "db_name", "default")


from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import os
from Stockin.models import company_table  # Ensure correct import

class DatabaseMiddleware(MiddlewareMixin):
    """Middleware to set the database for each request and update settings.DATABASES."""

    def process_request(self, request):
        """Set the database name and update settings.DATABASES dynamically."""
        if hasattr(request.user, "company_id"):
            db_name = request.user.company_id.db_name

            # Save the DB name in thread-local storage
            set_tenant_db(db_name)

            # Add the database configuration if it doesn't exist
            if db_name not in settings.DATABASES:
                tenant = company_table.objects.filter(db_name=db_name).first()
                if tenant:
                    settings.DATABASES[db_name] = {
                        "ENGINE": "django.db.backends.postgresql",
                        "NAME": tenant.db_name,
                        "USER": os.getenv("DATABASE_USER"),
                        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
                        "HOST": os.getenv("DATABASE_HOST"),
                        "PORT": "5432",
                        "CONN_MAX_AGE": 600,
                        "TIME_ZONE": "UTC",
                        "OPTIONS": {"options": "-c timezone=UTC"},
                        "CONN_HEALTH_CHECKS": False,
                        "AUTOCOMMIT": True,
                        "ATOMIC_REQUESTS": False,
                    }

