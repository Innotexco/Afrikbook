from django.shortcuts import render, redirect

from .models import chart_of_account, accounts, transfer_account, account_log
from account.forms import *
from django.contrib import messages
from django.http.response import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name
from django.utils import timezone
import decimal
from django.db.models import Sum, F, Q

from django.views.decorators.csrf import csrf_exempt

from .acct_functions.account import *
from .utils import unique_accountId_generator
from main.utils import pagenation


@login_required(login_url='/')
@urls_name(name = "Chart of account")
def new_chart_of_account(request):
    db = request.user.company_id.db_name

    acct_type = accounts.objects.using(db).all()
    acctType = Encountered(acct_type, 'account_type')

    if request.method == "POST":
        type = request.POST['account_type']
        Account = checkType(request, type)
        form = ChartOfAccount(request.POST)
        
        if form.is_valid():
            account_id = form.cleaned_data.get('account_id')
            # print(account_id[0], 'account_banknameaccount_bankname')
            
            Account = checkType(request, account_id[0])
               
            GetSeriseName =  accounts.objects.using(db).filter(Q(account_series__startswith=account_id[0])).first()
            new_account_id=unique_accountId_generator(chart_of_account, db, new_account_id=account_id)
            if Account:

                form_i = form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.series_name = Account
                form_i.account_id = new_account_id
                form_i.save(using=db)
                messages.success(request, "Chart of account Added Successful")
           
                # return redirect('account:ViewChartOfAccount')
            else:
                messages.error(request, "Account ID cannot start with "+account_id[0])
        else:
            print("here", form.errors)
    else:
        form = ChartOfAccount()
    
    return render(request, 'account/NewChartOfAccount.html', {'form' : form, 'acct_type': acctType })
    

# PREVENTS ITME FROM APPREARING TWICE
def Encountered(any,item):
   encountered_any = set()
   for i in any:
      # val = i.item
      val = getattr(i, item, None)
      if val not in encountered_any:
         encountered_any.add(val)
   return encountered_any


@login_required(login_url='/')
@urls_name(name ="Accounts")
def AccountSetup(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        form = AccountForm(request.POST)

        if form.is_valid():
            try:
                form_i = form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.save(using=db)
                messages.success(request, "Account Added Successful")
           
                return redirect('account:AccountSetup')
            except: 
                # print(form.errors)
                pass
        else:
            # print(form.errors)
            pass
    else:
        form = AccountForm()
   
    return render(request, 'account/AccountSetup.html', {'form': form})


@login_required(login_url='/')
@urls_name(name = "Chart of account")
def ViewChartOfAccount(request):
    db = request.user.company_id.db_name
    account_chart = chart_of_account.objects.using(db).all()

    account_chart = pagenation(request, account_chart, 1, 20)
    
    return render(request, 'account/ViewChartOfAccount.html', {'account_chart': account_chart})



def ViewChartOfAccountDetails(request, account_id):
    db = request.user.company_id.db_name
    try:
        chart_of_account_details = transfer_account.objects.using(db).filter(received_in=account_id)
        
        data = {
            'chart_of_account_detail': list(chart_of_account_details.values())
        }
        return JsonResponse(data)
    except transfer_account.DoesNotExist:
        return JsonResponse({'error': 'Account Not Found'}, status=404)


    # try:
    #     chart_of_account_detail = transfer_account.objects.filter(received_in=account_id)
    #     data = {
    #         'date_tx': chart_of_account_detail.date_tx,
    #         'paid_from': chart_of_account_detail.paid_from,
    #         'amount': chart_of_account_detail.amount
    #     }

    #     return JsonResponse({'chart_of_account_detail': data})
    # except transfer_account.DoesNotExist:
    #     return JsonResponse({'error': 'Account Not Found'}, status=404)

    
    # try:
    #     chart_of_account_detail = transfer_account.objects.filter(received_in = account_id,)
    #     data = {
    #         'date_tx': chart_of_account_detail.date_tx,
    #         'paid_from': chart_of_account_detail.paid_from,
    #         'amount': chart_of_account_detail.amount
    #     }
        
    #     return JsonResponse(data)
    # except chart_of_account_detail.DoesNotExist: 
    #     return JsonResponse({'error': 'Account Not Found'}, status=404)


@login_required(login_url='/')
@urls_name(name = "Inter Account Transfer")
def ViewInterAccountTransfer(request):
    db = request.user.company_id.db_name
    view_account = transfer_account.objects.using(db).all()

    amount = transfer_account.objects.using(db).filter(amount=1000)

    # if amount > 3 :
    #     amount - 2
    # else:
    #     print(amount)
   
    return render(request, 'account/ViewInterAccountTransfer.html', {'view_account': view_account, 'amount': amount})



@csrf_exempt 
@login_required(login_url='/')
@urls_name(name = "Inter Account Transfer")
def InterAccountTransfer(request):
    db = request.user.company_id.db_name
    if request.method == 'POST':
        form = AccountTransfer(request.POST)
        if form.is_valid():
            # Get form data
            date_tx = form.cleaned_data['date_tx']
            description = form.cleaned_data['description']
            acct_paid_from = form.cleaned_data['paid_from']
            acct_received_in = form.cleaned_data['received_in']
            amount = form.cleaned_data['amount']

            # print(paid_from)
            # print(received_in)
            received_in = chart_of_account.objects.using(db).get(account_id=acct_received_in)
            paid_from = chart_of_account.objects.using(db).get(account_id=acct_paid_from)
            
            if paid_from.actual_balance == 0:
                messages.error(request, "insufficient Fund !!!")
                return redirect('account:InterAccountTransfer')
            else:
                paid_from.actual_balance -= decimal.Decimal(amount)
                paid_from.Userlogin = request.user.username
                paid_from.save()

                received_in.actual_balance += decimal.Decimal(amount)
                received_in.Userlogin = request.user.username
                received_in.save()

            # Insert into transfer_account model
            transfer_obj = transfer_account.objects.using(db).create(
                date_tx=date_tx,
                description=description,
                paid_from=paid_from.account_id,
                received_in=received_in.account_id,
                amount=amount, 
                user = request.user.username
            )

            # Insert into account_log model
            # account_log_obj = account_log.objects.using(db).create(
            #     transaction_source="INTER ACCOUNT TRANSFER",
            #     amount=amount,
            #     account=received_in.account_id,
            #     account_type="Cash",
            #     timestamp=timezone.now(),
            #     Userlogin = request.user.username
            # )
            

            # return JsonResponse({'success': 'Transfer successful'})
            messages.success(request, "Transfer Successful")
            return redirect('account:ViewInterAccountTransfer')

        else:
            return form.errors

    account_detail = chart_of_account.objects.using(db).filter(account_id__startswith='1')
    
    return render(request, 'account/InterAccountTransfer.html', {'account_detail': account_detail, 'form': AccountTransfer()})



def fetchaccounts(request, value):
    db = request.user.company_id.db_name
    # print("/////////////////////",value)
    try:
        accounts = chart_of_account.objects.using(db).filter(series_name = value.upper()).values()
        
        return JsonResponse(list(accounts), safe=False)
    except chart_of_account.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    
def fetchaccountsname(request, value):
    db = request.user.company_id.db_name
   
    # print(value)   
    try:
        accounts = chart_of_account.objects.using(db).get(account_id = value).account_id[5:]
      
        
        return JsonResponse(accounts, safe=False)
    except chart_of_account.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)