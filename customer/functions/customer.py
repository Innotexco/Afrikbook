from customer.forms import CustomerForm, ReceivableForm, CustomerIncentiveForm
from customer.models import customer_table, receivable
from account.models import chart_of_account, account_log
from django.contrib import messages
from django.shortcuts import  redirect
from django.http import JsonResponse, HttpResponse
import decimal, uuid, requests, json
from main.models import User, company_table
from customer.functions.generalFunction import *
from client.models import client_companies
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings

def AfrikBookDB(request):
    db = request.user.company_id.db_name
    return db

def add_customer(request, db):
    form = CustomerForm(request.POST or None)
    db = AfrikBookDB(request)
    email = request.POST.get('email')
    csrftoken = request.POST.get('csrfmiddlewaretoken')
  
    if form.is_valid():
        form_i = form.save(commit=False)
        form_i.email = email
        form_i.Userlogin = request.user.username
        
        try:
            user = User.objects.using("afrikbook_client").get(Q(username=form.cleaned_data.get('name')) | Q(email=email))
           
            messages.error(request, "Customer already exist")
        except User.DoesNotExist:
            if customer_table.objects.using(db).filter(phone=form.cleaned_data.get('phone')).exists():
               messages.error(request, "Customer with p"+form.cleaned_data.get('phone')+" already exist")
            elif email and customer_table.objects.using(db).filter(email=email).exists():
               messages.error(request, "Customer with e"+form.cleaned_data.get('email')+" already exist")
            else:
                
                client = create_client_dtails(request, db, form.cleaned_data.get('name'), email, csrftoken)
               
                if client:  
                    form_i.save(using=db)
                    messages.success(request, "Customer  Created successfully")
                else:
                    messages.error(request, "An error occur while creating  customer")

    else:
        return form
    
 #Endpoint api 
def create_client_dtails(request, db, username, email, fallback_token):
    company = company_table.objects.get(db_name=db)
  
 
    # Sending a POST request
    payload = {
        'username': username,
        'email': email, 
        'company_id'   : company.id,
        'company_name'   : company.company_name,                  
        'company_db'  : company.db_name,
        'company_db_pass'  :  os.getenv('DATABASE_PASSWORD'),
        'company_db_user'  : os.getenv('DATABASE_USER'),
        'phone'  : company.phone,
    }

    url = f"{settings.MY_URL}"
    session = requests.Session()

    try:
        # 1. First GET the form page to get CSRF cookie
        get_response = session.get(f"{url}/Newcustomer", timeout=10)
        csrf_token = get_response.cookies.get('csrftoken', fallback_token)

        # 2. Set headers with the CSRF token
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
        }

        # 3. POST with session (cookie + headers)
        post_response = session.post(
            f"{url}/create_new_customer",
            json=payload,
            headers=headers,
            timeout=10
        )

        if post_response.status_code == 200:
            return post_response.json().get('user')
        else:
            # print("POST failed:", post_response.status_code, post_response.text)
            return False
    except requests.RequestException as e:
        # print("Error:", e)
        return False

    # Check response status
    
        
def update_customer(request, id, db):
    customer = customer_table.objects.using(db).get(pk=id)
    form = CustomerForm(request.POST or None, instance=customer)
    insant_email = request.POST.get('instant_email')

    if form.is_valid():
        form_i = form.save(commit=False)
        form_i.Userlogin = request.user.username
        form_i.save(using=db)
        if not  insant_email:
            customer.instant_email = 0
        else:
            customer.instant_email = 1
        customer.save()
        
        messages.success(request, form.cleaned_data['name'] + "'s Account is Updated")

def get_customer_details(request, id):
    try:
       customer = customer_table.objects.get(pk=id)
       data = {
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'category': customer.category,
            'code': customer.customer_code,
            'company': customer.company_name,
            'address': customer.address,
        }
       return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    

def cus_open_balance(request, db):
    if request.method == "POST":
        date = request.POST["date"]
        customer_id = request.POST["cusID"]
        transaction_type = request.POST["transaction_type"]
        amount = request.POST["amount"]
        operating_acc = request.POST["operating_acc"]
        description = request.POST["description"]

        receivable_form = ReceivableForm({"date":date,	"description":description,"type": transaction_type,	"amount": amount, "payment_method": "Cash","account_posted":"","invoice_status": "Unused"})
      
        
        if customer_id and operating_acc != "":
            cus = customer_table.objects.using(db).get(id=customer_id)
            if str(transaction_type).lower() == "debit":
                if receivable_form.is_valid():
                    # credit selected account
                    credit_account = chart_of_account.objects.using(db).get(account_id=operating_acc)
                    credit_account.actual_balance =+ decimal.Decimal(amount)
                    # credit_account.save()
                    CreateLog(db, credit_account, amount)

                    # customer balance
                    # cus.Balance = cus.Balance + decimal.Decimal(amount)
                    # cus.save()

                     #get customer last recievable balance 
                    if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
                        initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
                    else: 
                        initial_bal = decimal.Decimal(0.00)


                    if initial_bal > 0:
                        balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount)
                    else:
                        balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount) 
                        

                    # insert into recievable
                    # Generate a new transaction ID
                    transaction_id = uuid.uuid4()
                    
                    r_form = receivable_form.save(commit=False)
                    r_form.customer_id = cus.customer_code
                    r_form.customer_name = cus.name
                    r_form.initial_amount = initial_bal
                    r_form.balance = balance  
                    r_form.account_posted = credit_account.account_id
                    r_form.transaction_id = transaction_id
                    r_form.Userlogin = request.user.username
                    r_form.save(using=db)

                    #create account log
                    acc_log = account_log(
                        transaction_source  = "Customer Opening Balance",
                        amount              = amount,
                        date                = date,
                        account             = credit_account.account_id,
                        account_type        = credit_account.account_type
                    )
                    # acc_log.save(using=db)
                    messages.success(request, "Customer Balance Updated Successfullly")
            elif str(transaction_type).lower() == "credit":
                if receivable_form.is_valid():
                    # credit selected account
                    credit_account = chart_of_account.objects.using(db).get(account_id=operating_acc)
                    credit_account.actual_balance =+ decimal.Decimal(amount)
                    # credit_account.save()
                    CreateLog(db, credit_account, amount)
                    # customer balance
                    # cus.Balance = cus.Balance + decimal.Decimal(amount)
                    # cus.save()

                    #get customer last recievable balance 
                    if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
                        initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
                    else: 
                        initial_bal = decimal.Decimal(0.00)

                    if initial_bal > 0:
                        balance = decimal.Decimal(initial_bal) - decimal.Decimal(amount)
                    else:
                        balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount) 

                

                    # insert into recievable
                    # Generate a new transaction ID
                    transaction_id = uuid.uuid4()
                    
                    r_form = receivable_form.save(commit=False)
                    r_form.customer_id = cus.customer_code
                    r_form.customer_name = cus.name
                    r_form.initial_amount = initial_bal
                    r_form.balance = balance 
                    r_form.account_posted = credit_account.account_id
                    r_form.transaction_id = transaction_id
                    r_form.Userlogin = request.user.username
                    r_form.save(using=db)

                    #create account log
                    acc_log = account_log(
                        transaction_source  = "Customer Opening Balance",
                        amount              = amount,
                        date                = date,
                        account             = credit_account.account_id,
                        account_type        = credit_account.account_type
                    )
                    # acc_log.save(using=db)
                    messages.success(request, "Customer Balance Updated Successfully")
            else:
                messages.error(request, "Select transaction Type")
        else:
            messages.error(request,"Make sure customer and operating account are selected")


def refund_customer(request, db):
    if request.method == "POST":
        date = request.POST["date"]
        operating_acc = request.POST.get("account")
        customer_id = request.POST["customer_id"]
        amount = request.POST["amount"]
        description = request.POST["description"]


        receivable_form = ReceivableForm({"date":date,	"description":description,"type": "Credit",	"amount": amount, "payment_method": "Cash","account_posted":"","invoice_status": "Unused"})
        
        # cus_incentive = CustomerIncentiveForm({
        #     'customer_id':cus.id, 'customer_name':cus.name,'description':description, 'amount':amount, 'initial_amount': cus.Balance,  'date': date})
        if customer_id and operating_acc != "":
            if  receivable_form.is_valid():
                cus = customer_table.objects.using(db).get(id=customer_id)
                # cus_incentive.save()

                # customer = customer_table.objects.get(id=customer_id)
                cus.Balance = cus.Balance + decimal.Decimal(amount)
                # cus.save()

                credit_account = chart_of_account.objects.using(db).get(account_id=operating_acc)
                credit_account.actual_balance =- decimal.Decimal(amount)
                # credit_account.save()
                CreateLog(db, credit_account, amount)

                #get customer last recievable balance 
                if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
                    initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
                else: 
                    initial_bal = decimal.Decimal(0.00)
                
                if initial_bal > 0:
                    balance = decimal.Decimal(initial_bal) - decimal.Decimal(amount)
                else:
                    balance = decimal.Decimal(initial_bal) + decimal.Decimal(amount) 

                # insert into recievable
                # Generate a new transaction ID
                transaction_id = uuid.uuid4()
                
                r_form = receivable_form.save(commit=False)
                r_form.customer_id = cus.customer_code
                r_form.customer_name = cus.name
                r_form.initial_amount = initial_bal
                r_form.balance = balance
                r_form.account_posted = credit_account.account_id
                r_form.transaction_id = transaction_id
                r_form.Userlogin = request.user.username
                r_form.save(using=db)

                

                #create account log
                acc_log = account_log(
                    transaction_source  = "Customer Refund",
                    amount              = amount,
                    date                = date,
                    account             = credit_account.account_id,
                    account_type        = credit_account.account_type
                )
                # acc_log.save(using=db)
                messages.success(request, "Amount Refunded")
            else:
                return receivable_form
                messages.error(request, "Amount not Refunded")
        else:
            messages.error(request,"Make sure account and  customer are selected")
