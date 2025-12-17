from django.db import connections
import os
from django.conf import settings


def add_db_connection(db_name):
    """
    Safely add a dynamic database connection that works across Gunicorn workers
    """
    with _db_lock:
        # Check if connection already exists
        if db_name in connections.databases:
            print(f'Database {db_name} already exists, setting up connection...')
            return True
        
        # Database configuration
        db_config = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_name,
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
        
        try:
            # Add to settings.DATABASES
            settings.DATABASES[db_name] = db_config
            
            # Add to connections.databases
            connections.databases[db_name] = db_config
            
            # Store in cache so other workers can discover it
            # Use a reasonable timeout (e.g., 1 hour)
            cache_key = f'dynamic_db_{db_name}'
            cache.set(cache_key, db_config, timeout=3600)
            
            # Also maintain a set of all dynamic databases
            dynamic_dbs = cache.get('dynamic_databases_list', set())
            dynamic_dbs.add(db_name)
            cache.set('dynamic_databases_list', dynamic_dbs, timeout=None)
            
            print(f'Successfully registered database: {db_name}')
            return True
            
        except Exception as e:
            print(f"Error registering database {db_name}: {e}")
            return False


def ensure_db_connection(db_name):
    """
    Ensure database connection exists, checking cache if not in current worker
    """
    with _db_lock:
        # If connection exists locally, we're good
        if db_name in connections.databases:
            return True
        
        # Check if another worker registered this database
        cache_key = f'dynamic_db_{db_name}'
        db_config = cache.get(cache_key)
        
        if db_config:
            # Found in cache, add to this worker
            settings.DATABASES[db_name] = db_config
            connections.databases[db_name] = db_config
            print(f'Loaded database {db_name} from cache')
            return True
        
        # Database doesn't exist anywhere
        return False


def load_dynamic_databases():
    """
    Load all dynamic databases from cache on worker startup
    Call this in your AppConfig.ready() method
    """
    dynamic_dbs = cache.get('dynamic_databases_list', set())
    
    for db_name in dynamic_dbs:
        if db_name not in connections.databases:
            cache_key = f'dynamic_db_{db_name}'
            db_config = cache.get(cache_key)
            
            if db_config:
                settings.DATABASES[db_name] = db_config
                connections.databases[db_name] = db_config
                print(f'Pre-loaded database: {db_name}')


# def add_db_connection(db_name):
#     # Check if connection already exists in both places
#     if db_name in connections.databases and db_name in settings.DATABASES:
#         # print('exist', db_name)
#         return
    
#     # Database configuration
#     db_config = {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": db_name,  # Dynamic database name
#         'USER': os.getenv('DATABASE_USER'),
#         'PASSWORD': os.getenv('DATABASE_PASSWORD'),
#         'HOST': os.getenv('DATABASE_HOST'),
#         'PORT': '5432',
#         'TIME_ZONE': 'UTC',
#         "OPTIONS": {"options": "-c timezone=UTC"},
#         "CONN_HEALTH_CHECKS": False,
#         "CONN_MAX_AGE": 0,
#         "AUTOCOMMIT": True, 
#         "ATOMIC_REQUESTS": False,   
#     }
    
#     # Add to both settings.DATABASES and connections.databases
#     settings.DATABASES[db_name] = db_config
#     connections.databases[db_name] = db_config
    
#     # Optional: Write to a persistent file that gets loaded on worker startup
#     # This helps with the multi-worker issue
#     try:
#         with open('dynamic_databases.txt', 'a') as f:
#             f.write(f"{db_name}\n")
#     except Exception as e:
#         print(f"Could not write to dynamic databases file: {e}")


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



