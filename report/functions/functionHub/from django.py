from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum, F, Q
from customer.models import *
from vendor.models import *
from django.contrib import messages
from employee.models import payroll
from datetime import datetime
import decimal


from Stock.models import *
from .functions.globalFunctions.globalFunctions import *
from .functions.functionHub.functionHub import *
from account.models import account_log, chart_of_account
from customer.functions.generalFunction import *
from account.models import Expenses_account, Income_account, Assets_account, Liability_account







def getdate(request):
    from_date = None
    to_date = None
    toDate = request.GET.get('toDate')
    fromDate = request.GET.get('fromDate')
    if toDate and fromDate is not None:
        from_date = datetime.strptime(fromDate, '%Y-%m-%d').date()
        to_date = datetime.strptime(toDate, '%Y-%m-%d').date()
    return from_date, to_date


def AfrikBookDB(request):
    db = request.user.company_id.db_name
    return db

def Sumfunction(getFiltered):
    getFilteredSum1 = sum(amt.amount for amt in getFiltered)
    return getFilteredSum1


def ammountSummer1(request, model, field, search_query, field1, value):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    try:
        getFiltered = model.objects.using(db).filter(~Q(**{field:search_query}) & Q(**{field1:value}) & Q(date__range=(from_date, to_date)))
        Sumfunction(getFiltered)
    except model.DoesNotExist:
        pass

def ammountSummer2(request, value, othervalue, field, othervalue2):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    try:
        getOtherExpense = Expenses_account.objects.using(db).filter(~Q(account_bankname__icontains=value)  & ~Q(account_bankname__icontains=othervalue) & ~Q(**{field:othervalue2}) &  Q(date__range=(from_date, to_date)))
        getSum1 = Sumfunction(getOtherExpense)

        getOtherExpense = Expenses_account.objects.using(db).filter(~Q(account_bankname__icontains=value)  & ~Q(account_bankname__icontains=othervalue) & Q(date__range=(from_date, to_date)))
        getSum2 = Sumfunction(getOtherExpense)

        return getSum1, getSum2
    except Expenses_account.DoesNotExist:
        pass


def getCOGSSum(request):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    getgItemPrice = 0;
    try:
        getItemSold = customer_invoice.objects.using(db).filter(Q(date__range=(from_date, to_date))).values('itemcode').distinct()
        for i in getItemSold:
            getItemSold = Item.objects.using(db).get(Q(generated_code=i))
            getgItemPrice+= getItemSold.selling_price

        return getgItemPrice
    except customer_invoice.DoesNotExist or Item.DoesNotExist:
        pass


def ammountSummer3(request, model):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    try:
        expenses = model.objects.using(db).filter(Q(date__range=(from_date, to_date)))
        getSum = Sumfunction(expenses)
        return getSum
    except model.DoesNotExist:
        pass


def ammountSummer4(request, model, search_query):
    db = request.user.company_id.db_name
    from_date, to_date = getdate(request)
    try:
        getFiltered1 = model.objects.using(db).filter(Q(account_bankname__icontains=search_query) & Q(date__range=(from_date, to_date)))
        getFilteredSum1 = sum(amt.amount for amt in getFiltered1)
        return getFilteredSum1
    except model.DoesNotExist:
        pass




def ammountSummer5(request, model,  field, value, otherfield, othervalue):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    model_object = model.objects
    try:
        getFiltered1 = model_object.using(db).filter(Q(**{field:value}) & Q(date__range=(from_date, to_date)))
        getSum = Sumfunction(getFiltered1)
        getFiltered2 = model_object.using(db).filter(Q(**{field:value}) & Q(**{otherfield:othervalue}) & Q(date__range=(from_date, to_date)))
        getSum2 = Sumfunction(getFiltered2)
        return getSum, getSum2
    except model.DoesNotExist:
        pass





