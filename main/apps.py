# from django.apps import AppConfig
# import os
# import psycopg2
# from django.db import connections
# from django.conf import settings

# class MainConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'main'
    
#     def ready(self):
#         """Load all existing databases when the Django app starts"""
#         self.load_existing_databases()
    
#     def load_existing_databases(self):
#         """Query PostgreSQL to find all afrikbook_* databases and add them to connections"""
#         try:
#             db_user = os.getenv('DATABASE_USER')
#             db_password = os.getenv('DATABASE_PASSWORD')
#             db_host = os.getenv('DATABASE_HOST')
            
#             # Connect to PostgreSQL to get list of existing databases
#             pg_connection = psycopg2.connect(
#                 dbname="postgres",
#                 user=db_user,
#                 password=db_password,
#                 host=db_host,
#                 port='5432'
#             )
            
#             with pg_connection.cursor() as cursor:
#                 # Find all databases that start with 'afrikbook_'
#                 cursor.execute("""
#                     SELECT datname FROM pg_database 
#                     WHERE datname LIKE 'afrikbook_%' 
#                     AND datistemplate = false
#                 """)
                
#                 databases = cursor.fetchall()
                
#                 for (db_name,) in databases:
#                     if db_name not in connections.databases:
#                         db_config = {
#                             "ENGINE": "django.db.backends.postgresql",
#                             "NAME": db_name,
#                             'USER': db_user,
#                             'PASSWORD': db_password,
#                             'HOST': db_host,
#                             'PORT': '5432',
#                             'TIME_ZONE': 'UTC',
#                             "OPTIONS": {"options": "-c timezone=UTC"},
#                             "CONN_HEALTH_CHECKS": False,
#                             "CONN_MAX_AGE": 0,
#                             "AUTOCOMMIT": True, 
#                             "ATOMIC_REQUESTS": False,   
#                         }
                        
#                         settings.DATABASES[db_name] = db_config
#                         connections.databases[db_name] = db_config
            
#             pg_connection.close()
            
#         except Exception as e:
#             print(f"Error loading existing databases: {e}")




from django.apps import AppConfig
import sys
import os

class MainConfig(AppConfig):  # Change 'MainConfig' to match your app name
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'  # Change this to your app name
    
    def ready(self):
        # Only run in actual server processes, not during management commands
        # that don't need database connections
        skip_commands = ['makemigrations', 'migrate', 'collectstatic', 'createsuperuser']
        
        if any(cmd in sys.argv for cmd in skip_commands):
            return
        
        # Check if we're running under gunicorn or runserver
        is_server = (
            'gunicorn' in sys.argv[0] or 
            'runserver' in sys.argv or
            'WERKZEUG_RUN_MAIN' in os.environ  # For Django runserver reload
        )
        
        if not is_server:
            return
            
        # Import and load dynamic databases
        try:
            from .db_utils import load_dynamic_databases
            print("Loading dynamic databases on worker startup...")
            load_dynamic_databases()
        except ImportError:
            # db_utils doesn't exist yet
            pass
        except Exception as e:
            # Log but don't crash - let the app start
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load dynamic databases on startup: {e}")
            print(f"Warning: Could not load dynamic databases on startup: {e}")
