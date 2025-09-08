from django.core.management import call_command
from django.db import connection
from django.contrib import messages
import subprocess
from main.db_router import add_db_connection

def CreateDatabase_Migration(request, db_name):
    db_user = 'root'
    db_password = ''
    db_host = 'localhost'
    db_port = '3306'
  
    try:
        # Create the database
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {db_name}")   
        
        # Update settings.py - but this is problematic in production
        # Consider using add_db_connection() function instead
        add_db_connection(db_name)
        #with open('Afrikbook_proj/settings.py', 'a') as f:
            #f.write(f"\nDATABASES['{db_name}'] = {{\n  'ENGINE': 'django.db.backends.mysql',\n  'NAME':  '{db_name}', \n  'USER':  '{db_user}',\n  'PASSWORD': '{db_password}',\n  'HOST': '{db_host}',\n  'PORT': '{db_port}',\n}} ")
        
        # DON'T run makemigrations - use existing migrations only
        # Run migrate using Django's call_command instead of subprocess
        try:
            call_command('migrate', '--database', db_name, '--run-syncdb')
            messages.success(request, "Database created and migrated successfully")
            
        except Exception as migrate_error:
            print(f"Migration error: {migrate_error}")
            messages.error(request, f"Database created but migration failed: {migrate_error}")
            
    except Exception as db_error:
        print(f"Database creation error: {db_error}")
        messages.error(request, f"Database creation failed: {db_error}")
    
    # DON'T restart the server automatically - this is dangerous
    # subprocess.Popen('python manage.py runserver', shell=True)  # Remove this line
