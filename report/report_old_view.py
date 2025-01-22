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
from account.models import Expenses_account, Income_account







def getdate(request):
    from_date = None
    to_date = None
    toDate = request.GET.get('toDate')
    fromDate = request.GET.get('fromDate')
    if toDate and fromDate is not None:
        from_date = datetime.strptime(fromDate, '%Y-%m-%d').date()
        to_date = datetime.strptime(toDate, '%Y-%m-%d').date()
    return from_date, to_date


def getSum(request, search_query, field, value):
    db = request.user.company_id.db_name
    from_date, to_date = getdate(request)
    getFiltered = account_log.objects.using(db).filter(Q(account__startswith=search_query) & Q(**{field:value}) & Q(date__range=(from_date, to_date)))
    getFilteredSum = sum(amt.amount for amt in getFiltered)
    return getFilteredSum


def getSum3(request, search_query, field, value,  field2, value2):
    db = request.user.company_id.db_name
    from_date, to_date = getdate(request)
    getFiltered = account_log.objects.using(db).filter(Q(account__startswith=search_query) & Q(**{field:value}) & ~Q(**{field2:value2}) & Q(date__range=(from_date, to_date)))
    getFilteredSum = sum(amt.amount for amt in getFiltered)
    return getFilteredSum


def getSum2(request, field, value, field2, value2):
    db = request.user.company_id.db_name
    from_date, to_date = getdate(request)
    getFiltered = account_log.objects.using(db).filter(Q(**{field:value}) & ~Q(**{field2:value2}) & Q(date__range=(from_date, to_date)))
    getFilteredSum = sum(amt.amount for amt in getFiltered)
    return getFilteredSum 

def TrialBalance(request):
    get_Cash_Sum      = getSum3(request, '1','account_type', 'Cash', 'transaction_source', 'Return Outward')
    get_Sales_Sum     = getSum2(request, 'transaction_source', 'Sales', 'account_type', 'Accounts Receivable')
    get_Purchase_Sum  = getSum(request, '2','transaction_source', 'Purchase')
    get_acct_receivable_Sum  = getSum(request, '1','account_type', 'Accounts Receivable')
    get_acct_payable_Sum  = getSum(request, '2','account_type', 'Accounts payable')
    get_expenses_Sum  = getSum(request, '6','account_type', 'expenses')
    get_Salaries_Sum  = getSum(request, '6','account_type', 'Salaries')
    get_returnInward_Sum  = getSum(request, '1','transaction_source', 'Returned inward')
    get_returnoutward_Sum  = getSum(request, '1','transaction_source', 'Returned outward')
    get_discountallowed_Sum  = getSum(request, '2','transaction_source', 'Discount Allowed')
    get_discountrecieved_Sum  = getSum(request, '1','transaction_source', 'Discount Receivable')
    get_loan_Sum  = getSum(request, '4','account_type', 'Loan')
    get_rapaid_loan_Sum  = getSum(request, '2','account_type', 'Rapaid Loan')
    get_retained_earnings  = getSum(request, '3','account_type', 'retained earnings')



    context= {
        'CashSum': get_Cash_Sum,
        'SalesSum': get_Sales_Sum,
        'PurchaseSum': get_Purchase_Sum,
        'acctreceivableSum': get_acct_receivable_Sum,
        'acctpayableSum': get_acct_payable_Sum,
        'Expenses': get_expenses_Sum,
        'SalariesSum': get_Salaries_Sum,
        'returnInwardSum': get_returnInward_Sum,
        'returnoutward_Sum': get_returnoutward_Sum,
        'discountallowed_Sum': get_discountallowed_Sum,
        'discountrecieved_Sum': get_discountrecieved_Sum,
        'loan_Sum': get_loan_Sum,
        'rapaid_loan_Sum': get_rapaid_loan_Sum,
        'retained_earnings': get_retained_earnings,
    }
    return render(request, 'report/TrialBalance.html', context)



def BalanceSheet(request):
    # ***************************ASSET***********************
    get_Cash_Sum      = getSum3(request, '1','account_type', 'Cash', 'transaction_source', 'Return Outward')
    get_Inventory_Sum  = getSum(request, '1','account_type', 'Inventory')
    get_Prepaid_Expenses_Sum  = getSum(request, '1','account_type', 'Prepaid Expenses')
    get_PPE_Sum  = getSum(request, '1','account_type', 'Property plant equipment ')
    # ***************************END ASSET***********************

    # ***************************LIABILITY***********************
    get_acct_payable_Sum  = getSum(request, '2','account_type', 'Accounts payable')
    Income_Tax_Payables_Sum  = getSum(request, '2','account_type', 'Income Tax Payables')
    Other_Sum  = getSum(request, '2','account_type', 'Other')

    # ***************************END LIABILITY***********************


    # ***************************END Owner's Equity***********************
    capital_Investment   = getSum(request, '3','account_type', 'capital Investment')
    Retained_Earning   = getSum(request, '3','account_type', 'Retained Earning')
    Long_term_debit   = getSum(request, '3','account_type', 'Long term debit')

    # ***************************END Owner's Equity***********************
    
   
    context= {
        'CashSum': get_Cash_Sum,
        'Inventory_Sum': get_Inventory_Sum,
        'Prepaid_Expenses_Sum': get_Prepaid_Expenses_Sum,
        'get_PPE_Sum': get_PPE_Sum,
        'acctpayableSum': get_acct_payable_Sum,
        'Income_Tax_Payables_Sum': Income_Tax_Payables_Sum,
        'Other_Sum': Other_Sum,
        'capital_Investment': capital_Investment,
        'Retained_Earning': Retained_Earning,
        'Long_term_debit': Long_term_debit,

    }
    return render(request, 'report/BalanceSheet.html', context)

def getSumrevenue(request, search_query, field, value):
    db = request.user.company_id.db_name
    from_date, to_date = getdate(request)
    model_object = account_log.objects
    acct = Q(account__startswith=search_query)
    getFiltered1 = model_object.using(db).filter(acct & Q(**{field:value}) & Q(date__range=(from_date, to_date)))
    getFilteredSum1 = sum(amt.amount for amt in getFiltered1)

    getFiltered2 = model_object.using(db).filter(acct & ~Q(**{field:value}) & Q(date__range=(from_date, to_date)))
    getFilteredSum2 = sum(amt.amount for amt in getFiltered2)
    return getFilteredSum1, getFilteredSum2

def getIncome(request):
    db = request.user.company_id.db_name
    from_date, to_date = getdate(request)
    # if account starts with 4 or any given degit
    getFiltered2 =  account_log.objects.using(db).filter(Q(account__startswith='4') & Q(date__range=(from_date, to_date)))
    get_income = sum(amt.amount for amt in getFiltered2)
    return get_income

def ProfitLossStatement(request):
    sales, sales2   = getSumrevenue(request, '1', 'transaction_source', 'Returned inward')
    get_returnInward_Sum, get_returnInward_Sum2  = getSumrevenue(request, '1','transaction_source', 'Returned inward')
    get_discountallowed_Sum, get_discountallowed_Sum2  = getSumrevenue(request, '2', 'transaction_source', 'Discount Allowed')
    get_cost_of_goods, get_cost_of_goods2  = getSumrevenue(request, '2', 'transaction_source', 'Purchase')
    get_expenses, get_expenses2  = getSumrevenue(request, '6', 'account_type', 'expenses')
    get_other_income, get_other_income2  = getSumrevenue(request, '4', 'account_type', 'other-income')

    totalSales = sales2 + get_returnInward_Sum 
    totalLiability = get_discountallowed_Sum +  get_cost_of_goods
    TotalGrossProfit = totalSales - totalLiability

    
    get_income = getIncome(request)
    getNetProfit = totalSales + get_income + get_other_income
    get_totalNetProfit = getNetProfit - TotalGrossProfit

    context={
        'sales' : sales2,
        'returnInward_Sum' : get_returnInward_Sum,
        'discountallowed_Sum' : get_discountallowed_Sum,
        'Purchase' : get_cost_of_goods,
        'TotalGrossProfit' : TotalGrossProfit,
        'expenses' : get_expenses,
        'getincome' : get_income,
        'other_income' : get_other_income,
        'totalNetProfit' : get_totalNetProfit,
    }
    return render(request, 'report/ProfitLossStatement.html', context)


def seriesReport(data, db):
    getaccttype = chart_of_account.objects.using(db).values('account_id', 'actual_balance', 'account_type').filter(Q(series_name=data) )
    return getaccttype

def AccountSeriesReport(request):
    db = request.user.company_id.db_name
    get_all_assets = seriesReport('Assets', db)
    get_all_liability = seriesReport('Liability', db)
    get_all_equity = seriesReport('Equity', db)
    
    context  = {
        'allassets': get_all_assets,
        'allliabilities': get_all_liability,
        'equities': get_all_equity,
    }
    return render(request, 'report/AccountSeriesReport.html', context)



def StockInReport(request):
    db = request.user.company_id.db_name
    getstock = CreateStockIn.objects.using(db).all()
    items = Encountered(getstock,'item')
    getware_H = Encountered(getstock,'warehouse')
    total_quantity = sum(item.quantity for item in getstock)

    context = {
        'stock' : getstock,
        'warehouse' : getware_H,
        'item' : items,
        'qty' : total_quantity,
    }
    ForStockInReport(request, context, db)

    return render(request, 'report/StockInReport.html', context)




def OutletStockinReport(request):
    db = request.user.company_id.db_name
    getstock = CreateOutletStockIn.objects.using(db).all()
    items = Encountered(getstock,'item')
    outlet = Encountered(getstock,'outlet')
    total_quantity = sum(item.quantity for item in getstock)
    
    context = {
        'stock' : getstock,
        'outlet' : outlet,
        'item' : items,
        'qty' : total_quantity,
    }
    
    ForOutletStockinReport(request, context, db)
    return render(request, 'report/OutletStockinReport.html', context)

def SalesReport(request):
    db = request.user.company_id.db_name
    item_name = Item.objects.using(db).values("item_name")
    sales = customer_invoice.objects.using(db).all().exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()

    sales_total = customer_invoice.objects.using(db).values("invoiceID").distinct().count()
    qty_total = customer_invoice.objects.using(db).aggregate(total_qty=Sum("qty"))['total_qty']
    context = {
        'sales':unique_invoices,
        'sales_total':sales_total,
        'qty_total':qty_total,
        'item_name':item_name
    }
   
    return render(request, 'report/SalesReport.html', context)

def StockIn(request):
   
    return render(request, 'report/StockIn.html')

def PurchaseInvoice(request):
    db = request.user.company_id.db_name
    item_name = Item.objects.using(db).values("item_name")
    sales = Vendor_invoice.objects.using(db).all().exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()

    sales_total = Vendor_invoice.objects.using(db).values("invoiceID").distinct().count()
    qty_total = Vendor_invoice.objects.using(db).aggregate(total_qty=Sum("qty"))['total_qty']
    context = {
        'sales':unique_invoices,
        'sales_total':sales_total,
        'qty_total':qty_total,
        'item_name':item_name
    }
   
    return render(request, 'report/PurchaseInvoice.html', context)

def PayrollReport(request):
    db = request.user.company_id.db_name
    year = datetime.today().year
    years = range(year, year - 10, -1)
    payrolls = payroll.objects.using(db).values('month_year').distinct()
   
    unique_payroll = []
    for pay in payrolls:
        new_paryroll = payroll.objects.using(db).filter(month_year = pay['month_year'])
        if new_paryroll.exists():
            unique_payroll.append(new_paryroll.first())
    for i in unique_payroll:
        i.employee = payroll.objects.using(db).filter(month_year=i.month_year).count()
        i.gross_pay = payroll.objects.using(db).filter(month_year=i.month_year).aggregate(total=Sum('bsaic_salary'))['total']
        i.total_due = payroll.objects.using(db).filter(month_year=i.month_year).aggregate(total=Sum('total_due'))['total']
        i.net_pay = payroll.objects.using(db).filter(month_year=i.month_year).aggregate(total=Sum('net_pay'))['total']

    total_amount = payroll.objects.using(db).aggregate(total=Sum('net_pay'))['total']
    
    context = {
        'payrolls':unique_payroll,
        'total_amount':total_amount,
        'years':years
    }
   
    return render(request, 'report/PayrollReport.html', context)



def Receivables(request):
    db = request.user.company_id.db_name
    receivables = receivable.objects.using(db).all()
    customers = customer_table.objects.using(db).all()

    # Calculate total amount where type is "credit"
    credit_total = receivable.objects.using(db).filter(type="credit").aggregate(total_credit=Sum("amount"))['total_credit'] or 0
    # Calculate total amount where type is "debit"
    debit_total = receivable.objects.using(db).filter(type="debit").aggregate(total_debit=Sum("amount"))['total_debit'] or 0
    
    
    
    balance = credit_total - debit_total 
        
    context = {
        'recievables':receivables,
        'credit':credit_total,
        'debit':debit_total,
        'balance':balance,
        'customers':customers
    }
    return render(request, 'report/Receivables.html', context)

def AgedReceivables(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()
    aged = receivable.objects.using(db).filter(amount__lt=F('initial_amount')).distinct()
    amount_total = receivable.objects.using(db).aggregate(total_amount=Sum("amount"))['total_amount']
    
    if request.method == "POST":
        discount = request.POST.get("Discount")
        cost = request.POST.get("cost")
        customer = request.POST.get("customer")
        invoice = request.POST.get("invoice")
        today = datetime.now()
        try:
            cus = customer_table.objects.using(db).get(customer_code=customer)
            if discount == "NaN":
                description = "Payment Received"
                CreditReceivable(request, db, cus, today, description, cost)
                customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=customer).update(amount_paid=F('amount_paid')+cost)
            else:
                description = "Payment Received"
                CreditReceivable(request, db, cus, today, description, cost)
                description = "Discount Allowed"
                CreditReceivable(request, db, cus, today, description, discount)
                # acc = Expenses_account.objects.using(db).get(account_bankname="Discount Allowed").actual_balance += discount
                # acc.save()
                total = int(cost) + int(discount)
                customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=customer).update(amount_paid=F('amount_paid')+total)
                
            # DebitReceivable(request, db, cus, today, description, "Transfer", cost)    
            return JsonResponse(True, safe=False)
        except customer_table.DoesNotExist:
            return JsonResponse(False, safe=False)
        
  

    context ={
        'customers': customers,
        'aged_recievable':aged, 
        'amount_total':amount_total
    }
    return render(request, 'report/AgedReceivables.html', context)

def Payables(request):
    db = request.user.company_id.db_name
    receivables = payable.objects.using(db).all()
    vendors = vendor_table.objects.using(db).all()
    
    # Calculate total amount where type is "credit"
    credit_total = payable.objects.using(db).filter(type="credit").aggregate(total_credit=Sum("amount"))['total_credit']
    # Calculate total amount where type is "debit"
    debit_total = payable.objects.using(db).filter(type="debit").aggregate(total_debit=Sum("amount"))['total_debit']

    
    if  credit_total is None and debit_total is None:
        balance =  0.00
    else:
        balance = credit_total - debit_total  
    
    
    context = {
        'recievables':receivables,
        'credit':credit_total,
        'debit':debit_total,
        'balance':balance,
        'vendors':vendors
    }
   
    return render(request, 'report/Payables.html', context)

def AgedPayable(request):
    db = request.user.company_id.db_name
    vendors = vendor_table.objects.using(db).all()
    aged = payable.objects.using(db).filter(amount__lt=F('initial_amount')).distinct()
    amount_total = payable.objects.using(db).aggregate(total_amount=Sum("amount"))['total_amount']
    
    if request.method == "POST":
        discount = request.POST.get("Discount")
        cost = request.POST.get("cost")
        vendor = request.POST.get("vendor")
        invoice = request.POST.get("invoice")
        today = datetime.now()
        try:
            ven = vendor_table.objects.using(db).get(custID=vendor)
            if discount == "NaN":
                description = "Payment Received"
                CreditPayable(request, db, ven, today, description, cost)
                Vendor_invoice.objects.using(db).filter(invoiceID=invoice, cusID=vendor).update(amount_paid=F('amount_paid')+cost)
            else:
                description = "Payment Received"
                CreditPayable(request, db, ven, today, description, cost)
                description = "Discount Allowed"
                CreditPayable(request, db, ven, today, description, discount)
                # acc = Income_account.objects.using(db).get(account_bankname="Discount Received").actual_balance += discount
                # acc.save()
                total = int(cost) + int(discount)
                Vendor_invoice.objects.using(db).filter(invoiceID=invoice, cusID=vendor).update(amount_paid=F('amount_paid')+total)
                
            # DebitPayable(request, db, ven, today, description, "Transfer", cost)    
            return JsonResponse(True, safe=False)
        except vendor_table.DoesNotExist:
            return JsonResponse(False, safe=False)

    context ={
        'vendors': vendors,
        'aged_recievable':aged, 
        'amount_total':amount_total
    }
   
    return render(request, 'report/AgedPayable.html', context)

def GetCustomerDetailsAndInvoice(request, code, cusID):
    db = request.user.company_id.db_name
    try:
       customer = customer_table.objects.using(db).get(customer_code=cusID)
       
       lookups = Q(cusID=cusID) & Q(invoiceID=code)
       
       invoice = customer_invoice.objects.using(db).filter(lookups).values()
       serialized_data = list(invoice)
       data = {
           "customer":{
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'category': customer.category,
            'code': customer.customer_code,
            'company': customer.company_name,
            'address': customer.address,
            'balance': customer.Balance,
           },
           "invoice": serialized_data
            
        }
       return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewSalesLadger(request, code):
    db = request.user.company_id.db_name
    try:
       invoice = customer_invoice.objects.using(db).filter(invoiceID=code).values()
       serialized_data = list(invoice)

       amount_total = customer_invoice.objects.using(db).filter(invoiceID=code).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']
       data={
           'serialized_data':serialized_data,
           'amount_total':amount_total
       }
       return JsonResponse(data, safe=False)
    except customer_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewSales(request, code):
    db = request.user.company_id.db_name
    cusID = request.GET.get("cusID")
  
    if cusID:
        lookups = Q(id__iexact=cusID) | Q(customer_code__iexact=cusID)
        v_lookups = Q(custID__iexact=cusID)
    try:
       if vendor_table.objects.using(db).filter(v_lookups).exists():
           customer = vendor_table.objects.using(db).get(v_lookups)
           name = customer.name
           phone = customer.phone
           email = customer.email
           category = ""
           cus_code = ""
           company = customer.company_name
           address = customer.address
           balance = ""
       else:
           customer = customer_table.objects.using(db).get(lookups)
           name = customer.name
           phone = customer.phone
           email = customer.email
           category = customer.category
           cus_code = customer.customer_code
           company = customer.company_name
           address = customer.address
           balance = customer.Balance
              
       

       invoice = customer_invoice.objects.using(db).filter(invoiceID=code).values()
       serialized_data = list(invoice)

       amount_total = customer_invoice.objects.using(db).filter(invoiceID=code).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']
       data={
           'serialized_data':serialized_data,
           'amount_total':amount_total,
           "customer":{
            'name': name,
            'phone': phone,
            'email': email,
            'category': category,
            'code': cus_code,
            'company': company,
            'address': address,
            'balance': balance,
           }
       }
       return JsonResponse(data, safe=False)
    except customer_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewPurchase(request, code):
    db = request.user.company_id.db_name
    cusID = request.GET.get("cusID")
   
    if cusID:
        lookups = Q(id__iexact=cusID) | Q(custID__iexact=cusID)
    try:
       vendor = vendor_table.objects.using(db).get(lookups)

       invoice = Vendor_invoice.objects.using(db).filter(invoiceID=code, cusID=cusID).values()
       serialized_data = list(invoice)

       amount_total = Vendor_invoice.objects.using(db).filter(invoiceID=code).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']
       data={
           'serialized_data':serialized_data,
           'amount_total':amount_total,
           "vendor":{
            'name': vendor.name,
            'phone': vendor.phone,
            'email': vendor.email,
            # 'category': vendor.category,
            'code': vendor.custID,
            'company': vendor.company_name,
            'address': vendor.address,
            # 'balance': vendor.balance,
           }
       }
       return JsonResponse(data, safe=False)
    except Vendor_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewPurchaseLadger(request, code):
    db = request.user.company_id.db_name.using(db)
  
    try:
       invoice = Vendor_invoice.objects.using(db).filter(invoiceID=code).values()
       serialized_data = list(invoice)

       amount_total = Vendor_invoice.objects.using(db).filter(invoiceID=code).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']
       data={
           'serialized_data':serialized_data,
           'amount_total':amount_total
       }
       return JsonResponse(data, safe=False)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    

def ExpiredItems(request):
   
    return render(request, 'report/ExpiredItems.html')

def CustomerLedger(request):
   
    return render(request, 'report/CustomerLedger.html')

def ViewCustomerLedger(request, code, invoice):
    db = request.user.company_id.db_name
    if code:
        lookups = Q(cusID__iexact=code) | Q(invoiceID__iexact=invoice)

        invoice1 = customer_invoice.objects.using(db).filter(lookups).first()
        invoices = customer_invoice.objects.using(db).filter(lookups)

        total_amount = customer_invoice.objects.using(db).filter(lookups).values('invoiceID').distinct().aggregate(a_e=Sum('amount_expected'))['a_e'] or 0
        total_amount_paid = customer_invoice.objects.using(db).filter(lookups).values('invoiceID').distinct().aggregate(a_p=Sum('amount_paid'))['a_p'] or 0

        balance = total_amount - total_amount_paid
        
      
        for i in invoices:
            i.total = i.amount_expected + i.amount_paid
            i.balance = i.amount_expected - i.amount_paid

    context = {
        "invoice": invoice1,
        "invoices": invoices,
        'amount':total_amount,
        'paid':total_amount_paid,
        'balance':balance
        
    }
   
    return render(request, 'report/ViewCustomerLedger.html',context)

def SalesLedger(request):
    db = request.user.company_id.db_name
    item_name = Item.objects.using(db).values("item_name")
    sales = customer_invoice.objects.using(db).filter(invoice_state="Supplied").exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()

    sales_total = customer_invoice.objects.using(db).values("invoiceID").distinct().count()
    amount_total = customer_invoice.objects.using(db).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']

   
    context = {
        'sales':unique_invoices,
        'amount_total':amount_total,
        'item_name':item_name
    }
   
   
    return render(request, 'report/SalesLedger.html', context)

def EditSalesLedgerDate(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        invoice_id = request.POST['invoice_id']
        invoice_date = request.POST['invoice_date']
        new_date = request.POST['new_date']
        if new_date:

           invoice = customer_invoice.objects.using(db).filter(invoice_date=invoice_date, invoiceID=invoice_id).update(invoice_date=new_date) 
       

           messages.success(request, "Invoice date updated successfully")
           return JsonResponse(new_date, safe=False)
        else:
            return JsonResponse(new_date, safe=False) 


def PurchaseLedger(request):
    db = request.user.company_id.db_name
    item_name = Item.objects.using(db).values("item_name")
    sales = Vendor_invoice.objects.using(db).all() #.distinct()
    # sales = Vendor_invoice.objects.filter(invoice_state="Supplied").exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()

    sales_total = Vendor_invoice.objects.using(db).values("invoiceID").distinct().count()
    amount_total = Vendor_invoice.objects.using(db).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']
    amount_paid_total = Vendor_invoice.objects.using(db).values("invoiceID").distinct().aggregate(total_amount_paid=Sum("amount_paid"))['total_amount_paid'] or 0
    amount_expected_total = Vendor_invoice.objects.using(db).values("invoiceID").distinct().aggregate(total_amount_expected=Sum("amount_expected"))['total_amount_expected'] or 0

    balance= amount_expected_total - amount_paid_total
    context = {
        'purchase':unique_invoices,
        'amount_total':amount_total,
        'item_name':item_name,
        'amount_paid_total':amount_paid_total,
        'amount_expected_total':amount_expected_total,
        'balance':balance
    }
   
    return render(request, 'report/PurchaseLedger.html', context)

def EditPurchaseLedgerDate(request):
    db = request.user.company_id.db_name
    if request.method == "POST":
        invoice_id = request.POST['invoice_id']
        invoice_date = request.POST['invoice_date']
        new_date = request.POST['new_date']
        if new_date:

           invoice = Vendor_invoice.objects.using(db).filter(invoice_date=invoice_date, invoiceID=invoice_id)
           invoice.update(invoice_date=new_date) 
       

           messages.success(request, "Invoice date updated successfully")
           return JsonResponse(new_date, safe=False)
        else:
            return JsonResponse(new_date, safe=False) 

def VendorLedger(request):
   
    return render(request, 'report/VendorLedger.html')

def ViewVendorLedger(request, code, invoice):
    db = request.user.company_id.db_name
    if code:
        lookups = Q(cusID__iexact=code) | Q(invoiceID__iexact=invoice)

        invoice1 = Vendor_invoice.objects.using(db).filter(lookups).first()
        invoices = Vendor_invoice.objects.using(db).filter(lookups)

        total_amount = Vendor_invoice.objects.using(db).filter(lookups).values('invoiceID').distinct().aggregate(a_e=Sum('amount_expected'))['a_e']
        total_amount_paid = Vendor_invoice.objects.using(db).filter(lookups).values('invoiceID').distinct().aggregate(a_p=Sum('amount_paid'))['a_p']

        balance = total_amount - total_amount_paid
        
      
        for i in invoices:
            i.total = i.amount_expected + i.amount_paid
            i.balance = i.amount_expected - i.amount_paid

    context = {
        "invoice": invoice1,
        "invoices": invoices,
        'amount':total_amount,
        'paid':total_amount_paid,
        'balance':balance    
    }
   
    return render(request, 'report/ViewVendorLedger.html',context)


def CheckStockCondition(request):
   
    return render(request, 'report/CheckStockCondition.html')

def report_payroll_filter_by_date(request):
    db = request.user.company_id.db_name
    month = request.GET.get('month')
    year = request.GET.get('year')

    month_year = str(month+"_"+year)

    payrolls = payroll.objects.using(db).filter(month_year = month_year).values("month_year").distinct()
    
    unique_payroll = []

    for i in payrolls:
        new_payroll = payroll.objects.using(db).filter(month_year = month_year).values()
        employee = payroll.objects.using(db).filter(month_year=month_year).count()
        gross_pay = payroll.objects.using(db).filter(month_year=month_year).aggregate(total=Sum('bsaic_salary'))['total']
        total_due = payroll.objects.using(db).filter(month_year=month_year).aggregate(total=Sum('total_due'))['total']
        net_pay = payroll.objects.using(db).filter(month_year=month_year).aggregate(total=Sum('net_pay'))['total']
        
        if new_payroll.exists():
            new_payroll = new_payroll.first()
            new_payroll['employee'] = str(employee)
            new_payroll['gross_pay'] = gross_pay
            new_payroll['total_due'] = total_due
            new_payroll['net_pay'] = net_pay
            unique_payroll.append(new_payroll)


    amount_total = payroll.objects.using(db).filter(month_year=month_year).aggregate(total_amount=Sum("net_pay"))['total_amount']
    
    serializer_data = list(unique_payroll)

    data ={
        'amount_total':amount_total,
        'payroll':serializer_data
    }

    return JsonResponse(data, safe=False)


