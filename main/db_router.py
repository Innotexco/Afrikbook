from django.db import connections
import os
from django.conf import settings

def add_db_connection(db_name):
    # Check if connection already exists in both places
    if db_name in connections.databases and db_name in settings.DATABASES:
        # print('exist', db_name)
        return
    
    # Database configuration
    db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,  # Dynamic database name
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '5432',
        'TIME_ZONE': 'UTC',
        "OPTIONS": {"options": "-c timezone=UTC"},
        "CONN_HEALTH_CHECKS": False,
        "CONN_MAX_AGE": 0,
        "AUTOCOMMIT": True, 
        "ATOMIC_REQUESTS": False,   
    }
    
    # Add to both settings.DATABASES and connections.databases
    settings.DATABASES[db_name] = db_config
    connections.databases[db_name] = db_config
    
    # Optional: Write to a persistent file that gets loaded on worker startup
    # This helps with the multi-worker issue
    try:
        with open('dynamic_databases.txt', 'a') as f:
            f.write(f"{db_name}\n")
    except Exception as e:
        print(f"Could not write to dynamic databases file: {e}")


from django.conf import settings
from Stockin.models import company_table
from main.middleware import get_tenant_db

class MultiTenantRouter:
    """Database router to dynamically switch between tenant databases."""

    def db_for_read(self, model, **hints):
        """Get the tenant database from thread-local storage."""
        db_name = get_tenant_db()
    
        return db_name if db_name in settings.DATABASES else "default"

    def db_for_write(self, model, **hints):
        """Use the same logic for writing."""
        return self.db_for_read(model, **hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Only allow migrations on the default database."""
        return db == "default"  # Prevents accidental migrations on tenant DBs


