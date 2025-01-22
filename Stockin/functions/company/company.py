from django.shortcuts import render, redirect, get_object_or_404
from Stockin.forms import CompanyForm
from main.forms import UserRegistrationForm
from main.models import User, Pages, Privilege
from Stockin.models import company_table
from django.contrib import messages
from django.db import connection
from Stockin.utils import generate_company_id
import os
import time
import subprocess
from django.urls import reverse


def add_company(request, db_name):
    form = CompanyForm(request.POST or None)
    
    db_name = db_name
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    db = company_table.objects.filter(db_name=db_name)
    Email = User.objects.filter(email=email)
    if db.exists():
        messages.success(request, "Database already exists")
    elif Email.exists():
        messages.success(request, "Email already exists")
    else:
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.db_name = db_name
            form_instance.save()

            request.session['company_id'] = form_instance.id
            request.session['db_name'] = db_name
            CreateUser(request, db_name, username, email, password)
        else:
            messages.error(request, form.errors)
           



   
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
       
        AssingPrevilage(request, user, username)
        CreateDatabase_Migration(request, db_name)




def CreateDatabase_Migration(request, db_name):
    db_user = 'root'
    db_password = ''
    db_host = 'localhost'
    db_port = '3306'

  
    with connection.cursor() as cursor:
         cursor.execute(f"CREATE DATABASE {db_name}")   

    # #Update settings.py
    with open('Afrikbook_proj/settings.py', 'a') as f:
        f.write(f"\nDATABASES['{db_name}'] = {{\n  'ENGINE': 'django.db.backends.mysql',\n  'NAME':  '{db_name}', \n  'USER':  '{db_user}',\n  'PASSWORD': '{db_password}',\n  'HOST': '{db_host}',\n  'PORT': '{db_port}',\n}} ")
    

    # # # Perform migrations
    make = f'python manage.py makemigrations --database={db_name}'
    migrate_cmd = f'python manage.py migrate --database={db_name}'
    
    subprocess.Popen(make, shell=True)
    migrate_process = subprocess.Popen(migrate_cmd, shell=True)
    subprocess.Popen('python manage.py runserver', shell=True)


    # migrate_process.wait()
    # Check if migration was successful
    # if migrate_process.returncode == 0:
    #     # Redirect to another page
    #     # subprocess.Popen('python manage.py runserver', shell=True)
    #     messages.error(request, "Miration successful")
   
    #     return redirect('main:login')

    # else:
    #     # Handle migration failure
    #     # subprocess.Popen('python manage.py runserver', shell=True)
    #     messages.error(request, "Miration Unsuccessful")




def AssingPrevilage(request, user, username):
    pages = Pages.objects.all()

    if pages.count() > 0:
        for page in pages:
            Privilege.objects.create(name=page.page_name, user=user)
        messages.error(request, str(pages.count())+" Previlages was assinged to "+username)
    

        