#import os
#import psycopg2
#from django.core.management import call_command
#from django.contrib import messages
#from main.db_router import add_db_connection

#def CreateDatabase_Migration(request, db_name):
  #  db_user = os.getenv('DATABASE_USER')
  #  db_password = os.getenv('DATABASE_PASSWORD')
  #  db_host = os.getenv('DATABASE_HOST')
   # db_port = '5432'  # Default PostgreSQL port
    
   # pg_connection = None
    
   # try:
        # Establish a connection to PostgreSQL
    #    pg_connection = psycopg2.connect(
    #        dbname="postgres",  # Connect to the default 'postgres' database
  #          user=db_user,
  #          password=db_password,
   #         host=db_host,
    #        port=db_port
   #     )
   #     pg_connection.autocommit = True
        
        # Create the database using PostgreSQL connection
    #    with pg_connection.cursor() as cursor:
    #        cursor.execute(f"CREATE DATABASE {db_name}")
        
        # Add database connection to Django settings
    #    add_db_connection(db_name)
        
        # Run migrations using Django's call_command
   #     try:
   #         call_command('migrate', '--database', db_name, '--run-syncdb')
    #        messages.success(request, "Database created and migrated successfully")
            
    #    except Exception as migrate_error:
   #         print(f"Migration error: {migrate_error}")
    #        messages.error(request, f"Database created but migration failed: {migrate_error}")
            
  #  except psycopg2.Error as db_error:
   #     print(f"PostgreSQL error: {db_error}")
    #    messages.error(request, f"Database creation failed: {db_error}")
        
   # except Exception as general_error:
   #     print(f"General error: {general_error}")
   #     messages.error(request, f"An error occurred: {general_error}")
        
   # finally:
        # Close the PostgreSQL connection
     #   if pg_connection:
     #       pg_connection.close()
