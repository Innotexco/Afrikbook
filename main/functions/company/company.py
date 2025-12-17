from django.shortcuts import render, redirect, get_object_or_404
from Stockin.forms import CompanyForm
from main.forms import UserRegistrationForm
from main.models import User, Pages, Privilege, currency
from Stockin.models import company_table
from django.contrib import messages
from django.db import connection
from Stockin.utils import generate_company_id
import os
from dotenv import load_dotenv

load_dotenv()
import time
import subprocess
from django.urls import reverse
from settings.models import CreateProfile
from account.models import chart_of_account
from django.core.management import call_command
import psycopg2
from main.db_router import add_db_connection


def add_company(request, db_name):
    form = CompanyForm(request.POST or None)
    
    db_name = db_name
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    company_name = request.POST.get('company_name')
    country = request.POST.get('country')
    phone = request.POST.get('phone')
    address = request.POST.get('address')

   

    db = company_table.objects.filter(db_name=db_name)
    Email = User.objects.filter(email=email)
    Username = User.objects.filter(username=username)
    
    if Email.exists():
        messages.success(request, "Email already exists")
    elif Username.exists():
        messages.success(request, "Username already exists")
    else:
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.db_name = db_name
            form_instance.save()

            request.session['company_id'] = form_instance.id
            request.session['db_name'] = db_name
            CreateUser(request, db_name, username, email, password)
            
            return True
        else:
            # messages.error(request, form.errors)
            
            return False
        
def update_company(request, id):
    customer = company_table.objects.get(id=id)
    form = CompanyForm(request.POST or None, instance=customer)

    if form.is_valid():   
        form.save()
        messages.success(request, form.cleaned_data['company_name'] + "'s Account is Updated")




def CreateUser(request, db_name, username, email, password):

    company_id =  request.session.get('company_id')
    if company_id == "":
        messages.error(request, "You need company ID to register")
    else:
        company = company_table.objects.get(pk=company_id)  
        user = User.objects.create_user(username=username, company_id=company, email=email, password=password)
        
        AssignPrevilage(request, user, username)
        # CreateDatabase_Migration(request, db_name)
        CreatePostgresDatabase_Migration(request, db_name)




def CreateDatabase_Migration(request, db_name):
    db_user = 'root'
    db_password = ''
    db_host = 'localhost'
    db_port = '3306'

    # CREATE DATABASE
    with connection.cursor() as cursor:
         cursor.execute(f"CREATE DATABASE {db_name}")   

    # #Update settings.py
    with open('Afrikbook_proj/settings.py', 'a') as f:
        f.write(f"\nDATABASES['{db_name}'] = {{\n  'ENGINE': 'django.db.backends.mysql',\n  'NAME':  '{db_name}', \n  'USER':  '{db_user}',\n  'PASSWORD': '{db_password}',\n  'HOST': '{db_host}',\n  'PORT': '{db_port}',\n}} ")
    
    makemigrations(db_name)
    



def CreatePostgresDatabase_Migration(request, db_name):
    db_user = os.getenv('DATABASE_USER')
    db_password = os.getenv('DATABASE_PASSWORD')
    db_host = os.getenv('DATABASE_HOST')
    db_port = '5432'  # Default PostgreSQL port
    
    pg_connection = None
    
    try:
        # Establish a connection to PostgreSQL
        pg_connection = psycopg2.connect(
            dbname="postgres",  # Connect to the default 'postgres' database
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        pg_connection.autocommit = True
        
        # Check if database already exists first
        with pg_connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cursor.fetchone():
                print(f"Database {db_name} already exists, setting up connection...")
                
                # Add connection for existing database
                add_db_connection(db_name)
                
                # Also add to current process settings
                settings.DATABASES[db_name] = {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': db_name,
                    'USER': db_user,
                    'PASSWORD': db_password,
                    'HOST': db_host,
                    'PORT': db_port,
                }
                connections.databases[db_name] = settings.DATABASES[db_name]
                
                messages.success(request, f"Connected to existing database {db_name}")
                return True
            
            # Create the new database if it doesn't exist
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"Created new database: {db_name}")
        
        # Add database connection to Django settings
        add_db_connection(db_name)
        
        # Also add to current process settings
        settings.DATABASES[db_name] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
        }
        connections.databases[db_name] = settings.DATABASES[db_name]
        
        try:
            # DON'T run makemigrations - use existing migrations only
            call_command('migrate', '--database', db_name, '--fake-initial')
            messages.success(request, "Database created and migrated successfully")
            return True
            
        except Exception as migrate_error:
            print(f"Migration error: {migrate_error}")
            # Try alternative migration approach
            try:
                call_command('migrate', '--database', db_name, '--run-syncdb')
                messages.success(request, "Database created with syncdb")
                return True
            except Exception as sync_error:
                print(f"Sync error: {sync_error}")
                messages.error(request, f"Database created but migration failed: {migrate_error}")
                return False
                
    except psycopg2.Error as db_error:
        print(f"PostgreSQL error: {db_error}")
        messages.error(request, f"Database operation failed: {db_error}")
        return False
        
    except Exception as general_error:
        print(f"General error: {general_error}")
        messages.error(request, f"An error occurred: {general_error}")
        return False
        
    finally:
        # Close the PostgreSQL connection
        if pg_connection:
            pg_connection.close()

    #makemigrations(db_name)


def makemigrations(db_name):
    try:
        # Sync database migrations for the new database
        call_command('makemigrations')
        call_command('migrate', '--database', db_name)
      
    except Exception as e:
        #pass
        print(f"migration eror: {e}")
       


def AssignPrevilage(request, user, username):
    pages = Pages.objects.all()

    if pages.count() > 0:
        for page in pages:
            Privilege.objects.create(name=page.page_name, user=user)
        messages.success(request, str(pages.count()) +" Previlages was assinged to "+username)
    

def create_pages(request):
    pages = ['Chart of account', 'Purchase Invoices', 'Purchase Invoices', 'Purchase Quotes', 'Purchase Order',
              'Returns Outwards', 'Vendor', 'Sales Invoices', 'Sales Quotes', 'Sales Order', 
              'Returns Inwards', 'Customer', 'Employee', 'Payroll', 'Salary Approval', 'Item Receipt', 
              'Item Issue', 'Transfer Stock', 'Stock Adjustment', 'Item', 'Journal Entries', 'Loan Manager',
              'Sales Report', 'Stock In Report', 'Purchase Report', 'Purchase Adjustment', 'Stock Adjustment Outlet',
              'Payroll Report', 'Receivables', 'Payables', 'Aged Receivables', 'Aged Payable', 'Accounts', 
              'General Ledger', 'Balance Sheet', 'Balance Sheet', 'Trial Balance', 'Price Management', 'Users', 'Add Warehouse', 
              'Server Setup', 'Profile Setup', 'Sales Unit', 'Inter Account Transfer', 'Expired Items', 'Customer Incentives',
              'Warehouse to Outlet', 'Outlet to Warehouse', 'Stock Adjustment', 'Verify Transfer', 'Add New Journal',
              'Receive Payment', 'View Journal Entries', 'Profit / Loss', 'Other Series', 'Customer Ledger', 'Sales Ledger',
              'Purchase Ledger', 'Vendor Ledger', 'Add New Item', 'Item Category', 'Stock Level', 'Dashboard', 'Profile',
              'Purchase Price (Optional)', 'Selling Price (Retail)', 'Selling Price (Wholesale)', 'Change Price',
              '2.5% Sales Discount', '5% Sales Discount', '7.5% Sales Discount', '10% Sales Discount', '12.5% Sales Discount',
              'Change Sales Price'
            ]
    
    for page in pages:
        try:
           pages = Pages.objects.get(page_name=page)
        except Pages.DoesNotExist:
            Pages.objects.create(page_name=page)
            

def create_profile(request, loginuser):
    company = loginuser.company_id  # get the related company object, not just ID
    
    # Make sure migrations are run for this database
    makemigrations(company.db_name)

    # Check if profile exists
    if not CreateProfile.objects.using(company.db_name).filter(
        CompanyName=company.company_name, email=company.email
    ).exists():
        try:
            cu = currency.objects.get(Country=company.country).Currency
        except currency.DoesNotExist:
            cu = None  # fallback if currency not found

        # Create profile
        CreateProfile.objects.using(company.db_name).create(
            CompanyName=company.company_name,
            phone=company.phone,
            email=company.email,
            address=company.address,
            country=company.country,
            currency=cu,
        )
    
    #Create default Accounts
    default_account(request, company.db_name)

def default_account(request, db):
   
    accounts = [
        {
            'account_id': "6001-Salary",
            'series_name': "Expenses",
            'account_type': "Payable",
            'account_bankname': "Salary Account"

        },
        {
            'account_id': "2001-ReturnInward",
            'series_name': "Liability",
            'account_type': "Cash",
            'account_bankname': "Return Inward"

        },
        {
            'account_id': "1001-ReturnOutward",
            'series_name': "Assets",
            'account_type': "Cash",
            'account_bankname': "Return Outward"

        },
        {
            'account_id': "4001-Sales",
            'series_name': "Income",
            'account_type': "Cash",
            'account_bankname': "Sales Account"

        },
        {
            'account_id': "2002-Purchase",
            'series_name': "Liability",
            'account_type': "Cash",
            'account_bankname': "Purchase Account"

        },
        {
            'account_id': "1002-Receivable",
            'series_name': "Assets",
            'account_type': "Receivable",
            'account_bankname': "Account Receivable"

        },
        {
            'account_id': "2003-Payable",
            'series_name': "Liablity",
            'account_type': "Payable",
            'account_bankname': "Account Payable"

        },
        {
            'account_id': "6002-Vat",
            'series_name': "Expenses",
            'account_type': "Payable",
            'account_bankname': "Vat Account"

        }
       
    ]
  
    for acc in accounts:
        account_id   = acc['account_id']
        series_name  = acc['series_name']
        account_type = acc['account_type']
        bank         = acc['account_bankname']
        
        try:
            account = chart_of_account.objects.using(db).get(account_id=account_id, series_name=series_name, account_type=account_type, account_bankname=bank)
        except chart_of_account.DoesNotExist:
            chart_of_account.objects.using(db).create(account_id=account_id, series_name=series_name, account_type=account_type, account_bankname=bank, status="Active")


def create_country_currency(request):
   
    country = [
        {'country': 'Albania', 'currency': 'Lek'},
        {'country': 'Afghanista', 'currency': '؋'},
        {'country': 'Argentina', 'currency': '$'},
        {'country': 'Aruba', 'currency': 'ƒ'},
        {'country': 'Australia', 'currency': '$'},
        {'country': 'Azerbaijan', 'currency': '₼'},
        {'country': 'Bahamas', 'currency': '$'},
        {'country': 'Barbados', 'currency': '$'},
        {'country': 'Belarus', 'currency': 'Br'},
        {'country': 'Belize', 'currency':'BZ$'},
        {'country': 'Bermuda', 'currency':'$'},
        {'country': 'Bolivia', 'currency':'$b'},
        {'country': 'Bosnia and Herzegovina', 'currency':'KM'},
        {'country': 'Botswana', 'currency':'P'},
        {'country': 'Bulgaria', 'currency':'лв'},
        {'country': 'Brazil', 'currency':'R$'},
        {'country': 'Brunei Darussalam', 'currency':'$'},
        {'country': 'Cambodia', 'currency':'៛'},
        {'country': 'Canada', 'currency':'$'},
        {'country': 'Cayman Islands', 'currency':'$'},
        {'country': 'Chile', 'currency':'$'},
        {'country': 'China', 'currency':'¥'},
        {'country': 'Colombia', 'currency':'$'},
        {'country': 'Costa Rica','currency':'₡'},
        {'country': 'Croatia', 'currency':'kn'},
        {'country': 'Cuba', 'currency':'₱'},
        {'country': 'Czech Republic', 'currency':'Kč'},
        {'country': 'Denmark', 'currency':'kr'},
        {'country': 'Dominican Republic', 'currency':'RD$'},
        {'country': 'East Caribbean', 'currency':'$'},
        {'country': 'Egypt', 'currency':'£'},
        {'country': 'El Salvador', 'currency':'$'},
        {'country': 'Euro Member Countries', 'currency':'€'},
        {'country': 'Falkland Islands (Malvinas)', 'currency':'£'},
        {'country': 'Fiji', 'currency':'$'},
        {'country': 'Ghana', 'currency':'¢'},
        {'country': 'Gibraltar', 'currency':'£'},
        {'country': 'Guatemala', 'currency':'Q'},
        {'country': 'Guernsey', 'currency':'£'},
        {'country': 'Guyana', 'currency':'$'},
        {'country': 'Honduras', 'currency':'L'},
        {'country': 'Hong Kong', 'currency':'$'},
        {'country': 'Hungary', 'currency':'Ft'},
        {'country': 'Iceland', 'currency':'kr'},
        {'country': 'India', 'currency':'₹'},
        {'country': 'Indonesia', 'currency':'Rp'},
        {'country': 'Iran', 'currency':'﷼'},
        {'country': 'Isle of Man', 'currency':'£'},
        {'country': 'Israel', 'currency':'₪'},
        {'country': 'Jamaica', 'currency':'J$'},
        {'country': 'Japan', 'currency':'¥'},
        {'country': 'Jersey', 'currency':'£'},
        {'country': 'Kazakhstan', 'currency':'лв'},
        {'country': 'Korea (North)', 'currency':'₩'},
        {'country': 'Korea (South)', 'currency':'₩'},
        {'country': 'Kyrgyzstan', 'currency':'лв'},
        {'country': 'Laos', 'currency':'₭'},
        {'country': 'Lebanon', 'currency':'£'},
        {'country': 'Liberia', 'currency':'$'},
        {'country': 'Macedonia', 'currency':'ден'},
        {'country': 'Malaysia', 'currency':'RM'},
        {'country': 'Mauritius', 'currency':'₨'},
        {'country': 'Mexico', 'currency':'$'},
        {'country': 'Mongolia', 'currency':'₮'},
        {'country': 'Mozambique', 'currency':'MT'},
        {'country': 'Namibia', 'currency':'$'},
        {'country': 'Nepal', 'currency':'₨'},
        {'country': 'Netherlands', 'currency':'ƒ'},
        {'country': 'New Zealand', 'currency':'$'},
        {'country': 'Nicaragua', 'currency':'C$'},
        {'country': 'Nigeria', 'currency':'₦'},
        {'country': 'Norway', 'currency':'kr'},
        {'country': 'Oman', 'currency':'﷼'},
        {'country': 'Pakistan', 'currency':'₨'},
        {'country': 'Panama', 'currency':'B/.'},
        {'country': 'Paraguay', 'currency':'Gs'},
        {'country': 'Peru', 'currency':'S/.'},
        {'country': 'Philippines', 'currency':'₱'},
        {'country': 'Poland', 'currency':'zł'},
        {'country': 'Qatar', 'currency':'﷼'},
        {'country': 'Romania', 'currency':'lei'},
        {'country': 'Russia', 'currency':'₽'},
        {'country': 'Saint Helena', 'currency':'£'},
        {'country': 'Saudi Arabia', 'currency':'﷼'},
        {'country': 'Serbia', 'currency':'Дин.'},
        {'country': 'Seychelles', 'currency':'₨'},
        {'country': 'Singapore', 'currency':'$'},
        {'country': 'Solomon Islands', 'currency':'$'},
        {'country': 'Somalia', 'currency':'S'},
        {'country': 'South Africa', 'currency':'R'},
        {'country': 'Sri Lanka', 'currency':'₨'},
        {'country': 'Sweden', 'currency':'kr'},
        {'country': 'Switzerland', 'currency':'CHF'},
        {'country': 'Suriname', 'currency':'$'},
        {'country': 'Syria', 'currency':'£'},
        {'country': 'Taiwan', 'currency':'NT$'},
        {'country': 'Thailand', 'currency':'฿'},
        {'country': 'Trinidad and Tobago', 'currency':'TT$'},
        {'country': 'Turkey', 'currency':'₺'},
        {'country': 'Tuvalu', 'currency': '$'},
        {'country': 'Ukraine', 'currency': '₴'},
        {'country': 'United Kingdom', 'currency': '£'},
        {'country': 'United States', 'currency': '$'},
        {'country': 'Uruguay', 'currency': '$U'},
        {'country': 'Uzbekistan', 'currency': 'лв'},
        {'country': 'Venezuela', 'currency': 'Bs'},
        {'country': 'Viet Nam', 'currency': '₫'},
        {'country': 'Yemen', 'currency': '﷼'},
        {'country': 'Zimbabwe', 'currency': 'Z$'}
        
    ]
    
    for i in country:
        ctry   = i['country']
        cu  = i['currency']
        
        try:
            account = currency.objects.get(Country=ctry, Currency=cu)
        except currency.DoesNotExist:
             currency.objects.create(Country=ctry, Currency=cu)
    

