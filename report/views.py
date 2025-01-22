from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum, F, Q
from customer.models import *
from vendor.models import *
from django.contrib import messages
from employee.models import payroll, employee
from datetime import datetime, timedelta, time, date
import decimal

from settings.models import Warehouse, company_details

from Stock.models import *
from .functions.globalFunctions.globalFunctions import *
from .functions.functionHub.functionHub import *
from account.models import account_log, chart_of_account
from customer.functions.generalFunction import *
from account.models import Expenses_account, Income_account, Assets_account, Liability_account

from main.models import company_table
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name




def getdateReport(fromDate, toDate):
    from_date = None
    to_date = None
   
    if fromDate != '':
        from_date = datetime.strptime(fromDate, '%Y-%m-%d').date()
    if toDate != '':
        to_date = datetime.strptime(toDate, '%Y-%m-%d').date()

    return from_date, to_date

def getdate(request):
    from_date = None
    to_date = None
    toDate = request.GET.get('toDate')
    fromDate = request.GET.get('fromDate')
    if toDate and fromDate is not None:
        from_date = datetime.strptime(fromDate, '%Y-%m-%d').date()
        to_date = datetime.strptime(toDate, '%Y-%m-%d').date()
    return from_date, to_date


# def gettime(beginTime, endTime):
#     from_time = None
#     to_time   = None
#     if beginTime and endTime is not None:
#         date_obj = datetime.strptime(beginTime,'%Y-%m-%d')
#         start_day = date_obj - timedelta(days=date_obj.weekday())
#         end_of_week = start_day + timedelta(days=4)
#     return from_time, to_time

def gettime(beginTime, endTime, fromDate):
    from_time = None
    to_time   = None
    from_date   = None

    if beginTime and endTime is not None:
        from_time = time(int(beginTime), 0)
        to_time = time(int(endTime), 0)
        from_date = datetime.strptime(fromDate, '%Y-%m-%d').date()
    return from_time, to_time, from_date


def getSum(request, search_query, field, value):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    getFiltered = account_log.objects.using(db).filter(Q(account__startswith=search_query) & Q(**{field:value}) & Q(date__range=(from_date, to_date)))
    getFilteredSum = sum(amt.amount for amt in getFiltered)
    return getFilteredSum


def getSum3(request, search_query, field, value,  field2, value2):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    getFiltered = account_log.objects.using(db).filter(Q(account__startswith=search_query) & Q(**{field:value}) & ~Q(**{field2:value2}) & Q(date__range=(from_date, to_date)))
    getFilteredSum = sum(amt.amount for amt in getFiltered)
    return getFilteredSum


def getSum2(request, field, value, field2, value2):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    getFiltered = account_log.objects.using(db).filter(Q(**{field:value}) & ~Q(**{field2:value2}) & Q(date__range=(from_date, to_date)))
    getFilteredSum = sum(amt.amount for amt in getFiltered)
    return getFilteredSum 


@login_required(login_url='/')
@urls_name(name="Trial Balance")
def TrialBalance(request):
    from_date, to_date = getdate(request)
    context = None
    if from_date and  to_date:
        get_Purchase_Sum            = ammountSummer(request, Expenses_account,  (Q(account_type='Cash') & Q(date__range=(from_date, to_date))))
        get_Sales_Sum               = ammountSummer(request, Assets_account, (~Q(account_bankname__icontains='Return Inward') & Q(account_type='Cash') & Q(date__range=(from_date, to_date))))
        get_acct_payable_Sum        = ammountSummer(request, Liability_account, (Q(account_type='Payable') & Q(date__range=(from_date, to_date))))
        get_acct_receivable_Sum     = ammountSummer(request, Assets_account, (Q(account_type='Receivable') & Q(date__range=(from_date, to_date))))
        get_expenses_Sum            = ammountSummer(request, Expenses_account,  (~Q(account_bankname__icontains='Salaries')  & ~Q(account_bankname__icontains='Discount Allowed') & ~Q(account_type='Cash') &  Q(date__range=(from_date, to_date))))
        get_Salaries_Sum            = ammountSummer(request, Expenses_account, (Q(account_bankname__icontains='Salaries') & Q(date__range=(from_date, to_date))))
        get_discountallowed_Sum     = ammountSummer(request, Expenses_account, (Q(account_bankname__icontains='Discount Allowed') & Q(date__range=(from_date, to_date))))
        get_discountrecieved_Sum    = ammountSummer(request, Assets_account, (Q(account_bankname__icontains='Discount Allowed') & Q(date__range=(from_date, to_date))))
        get_returnInward_Sum        = ammountSummer(request, Assets_account, (Q(account_bankname__icontains='Return Inward') & Q(date__range=(from_date, to_date))))
        get_returnoutward_Sum       = ammountSummer(request, Assets_account, (Q(account_bankname__icontains='Return Outward') & Q(date__range=(from_date, to_date))))
        get_loan_Sum                = ammountSummer(request, Liability_account,  (Q(account_type='Loan') & Q(account_bankname__icontains='Loan') & Q(date__range=(from_date, to_date))))
        get_rapaid_loan_Sum         = ammountSummer(request, Liability_account, (Q(account_bankname__icontains='Rapaid_Loan') & Q(date__range=(from_date, to_date))))
        get_retained_earnings       = 0



        context= {
            # 'CashSum': get_Cash_Sum,
            'SalesSum': get_Sales_Sum,
            'PurchaseSum': get_Purchase_Sum,
            'acctpayableSum': get_acct_payable_Sum,
            'acctreceivableSum': get_acct_receivable_Sum,
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


@login_required(login_url='/')
@urls_name(name="Balance Sheet")
def BalanceSheet(request):
    context = None
    from_date, to_date = getdate(request)
    if from_date and  to_date:
        # ***************************CURRENT ASSET***********************

        get_Cash_Sum                = ammountSummer(request, Assets_account, (Q(account_type='Cash') & Q(date__range=(from_date, to_date))))
        accountReceivables          = ammountSummer(request, Assets_account, (Q(account_bankname='Account Receivable') & Q(date__range=(from_date, to_date))))
        get_Inventory_Sum           = ammountSummer(request, CreateStockIn, (Q(datetx__range=(from_date, to_date))))
        get_Prepaid_Expenses_Sum    = ammountSummer(request, Expenses_account, (Q(account_bankname__icontains='Prepaid Expenses') & Q(date__range=(from_date, to_date))))
        Total_Current_Assets        =  float(get_Cash_Sum) + float(accountReceivables) + float(get_Inventory_Sum) + float(get_Prepaid_Expenses_Sum)
        # ***************************END CURRENT ASSET***********************


        # ***************************END NON-CURRENT ASSET***********************
        get_PPE_Sum                 = ammountSummer(request, Assets_account, (Q(account_bankname__icontains='Property_plant_equipment') & Q(date__range=(from_date, to_date))))
        Total_Non_Current_Assets    = get_PPE_Sum #sums non current assets
        # ***************************END NON-CURRENT ASSET***********************

        # TOTAL ASSETS 
        Total_Assets                = float(Total_Current_Assets) + float(Total_Non_Current_Assets)

        # ***************************CURRENT LIABILITY***********************
        get_acct_payable_Sum        =  ammountSummer(request, Liability_account, (~Q(account_bankname__icontains='tax_income_payable') & Q(account_type='Payable') & Q(date__range=(from_date, to_date))))
        Income_Tax_Payables_Sum     = ammountSummer(request,  Liability_account, (Q(account_bankname__icontains='tax_income_payable') & Q(date__range=(from_date, to_date))))
        Total_Current_Liabilities   = float(get_acct_payable_Sum) + float(Income_Tax_Payables_Sum)
        # ***************************END CURRENT LIABILITY***********************


        # ***************************NON CURRENT LIABILITY***********************
        Long_term_debit                 = ammountSummer(request, Liability_account,  (Q(status='Long_term_debit') & Q(date__range=(from_date, to_date))))
        Other_debt                      = 0
        Total_Non_Current_Liabilities   =  Long_term_debit + Other_debt

        # ***************************END NON CURRENT LIABILITY***********************


        # ***************************END Owner's Equity***********************
        capital_Investment              = ammountSummer(request, Assets_account, (Q(account_bankname__icontains='capital_Investment') & Q(date__range=(from_date, to_date))))
        Retained_Earning                = ammountSummer(request, Assets_account,  (Q(account_bankname__icontains='Retained_Earning') & Q(date__range=(from_date, to_date))))
        Total_Owners_equity             = float(capital_Investment) + float(Retained_Earning)

        # ***************************END Owner's Equity***********************
        
    
        context= {
            'CashSum': get_Cash_Sum,
            'AccountReceivables': accountReceivables,
            'Inventory_Sum': get_Inventory_Sum,
            'Prepaid_Expenses_Sum': get_Prepaid_Expenses_Sum,
            'Total_Current_Assets': Total_Current_Assets,
            'get_PPE_Sum': get_PPE_Sum,
            'Total_Non_Current_Assets':Total_Non_Current_Assets,
            'Total_Assets':Total_Assets,
            'acctpayableSum': get_acct_payable_Sum,
            'Income_Tax_Payables_Sum': Income_Tax_Payables_Sum,
            'Total_Current_Liabilities':Total_Current_Liabilities,
            'Long_term_debit': Long_term_debit,
            'Other_Sum': Other_debt,
            'Total_Non_Current_Liabilities': Total_Non_Current_Liabilities,
            'capital_Investment': capital_Investment,
            'Retained_Earning': Retained_Earning,
            'Total_Owners_equity':Total_Owners_equity,
        }
    return render(request, 'report/BalanceSheet.html', context)



def AfrikBookDB(request):
    db = request.user.company_id.db_name
    return db

def Sumfunction(getFiltered):
    getFilteredSum1 = sum(amt.amount for amt in getFiltered)
    return getFilteredSum1


def getCOGSSum(request, model, itemcode):
    db = AfrikBookDB(request)
    from_date, to_date                  = getdate(request)
    getgItemPrice                       = 0.00;
    try:
        getItemSold                     = model.objects.using(db).filter(Q(invoice_date__range=(from_date, to_date)))
        for i in getItemSold:
            getItemSold                 = Item.objects.using(db).get(Q(generated_code=i.itemcode))
            getgItemPrice               = float(getgItemPrice) + float(getItemSold.selling_price)

        return getgItemPrice
    except customer_invoice.DoesNotExist or Item.DoesNotExist:
        pass


def ammountSummer(request, model, query_kwargs):
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    model_object = model.objects
    getSum = 0.00
    try:
        getFiltered = model_object.using(db).filter(query_kwargs)
        if getFiltered  is not None:
            if model is CreateStockIn:
                for qty_price in getFiltered:
                    getamount           = float(qty_price.quantity) * float(qty_price.amount)
                    getSum              = float(getSum) + float(getamount)
            else:
                getSum                  = Sumfunction(getFiltered)
    except model.DoesNotExist:
        return 0
    return getSum
    

@login_required(login_url='/')
@urls_name(name="Profit / Loss")
def ProfitLossStatement(request):
    context = None
    db = AfrikBookDB(request)
    from_date, to_date = getdate(request)
    if from_date and  to_date:
        sales                           = ammountSummer(request,  Assets_account, (Q(account_type='Cash') & Q(date__range=(from_date, to_date))))
        get_salesReturn                 = ammountSummer(request, Assets_account, (Q(account_type='Cash') & Q(account_bankname__icontains='Return Inward') & Q(date__range=(from_date, to_date))))
        get_discountallowed_Sum         = ammountSummer(request, Expenses_account, (Q(account_type='Cash') & Q(account_bankname__icontains='Discount Allowed') & Q(date__range=(from_date, to_date))))
        get_cost_of_goods               = getCOGSSum(request, customer_invoice, 'itemcode')
        get_expenses                    = ammountSummer(request, Expenses_account,  (~Q(account_bankname__icontains='Tax')  & ~Q(account_bankname__icontains='Discount Allowed') &  Q(date__range=(from_date, to_date))))

        getOperatingExpensesSum         = ammountSummer(request, Expenses_account, Q(date__range=(from_date, to_date)))
        get_other_income                = ammountSummer(request, Income_account,  (Q(account_type='Cash') & Q(date__range=(from_date, to_date))))

        
        totalSales                      = sales - get_salesReturn 
        totalLiability                  = get_discountallowed_Sum +  get_cost_of_goods
        # TotalGrossProfit = totalSales - totalLiability
        TotalGrossProfit                = totalSales

        
        get_operatong_income            = TotalGrossProfit - getOperatingExpensesSum
        getNetProfit                    = totalSales + get_operatong_income + get_other_income
        get_totalNetProfit              = getNetProfit - getOperatingExpensesSum


        getTax                          = Expenses_account.objects.using(db).filter(Q(account_bankname__icontains='Tax') & Q(date__range=(from_date, to_date)))
        getTaxSum                       = sum(amt.amount for amt in getTax)

        context={
            'sales' : sales,
            'salesReturn' : get_salesReturn,
            'discountallowed_Sum' : get_discountallowed_Sum,
            'COGS' : get_cost_of_goods,
            'TotalGrossProfit' : TotalGrossProfit,
            'expenses' : get_expenses,
            'operatingIncome' : get_operatong_income,
            'other_income' : get_other_income,
            'tax' : getTaxSum,
            'totalNetProfit' : get_totalNetProfit,
        }
    return render(request, 'report/ProfitLossStatement.html', context)




# ********************************************************************************************************

         


def getStockAdjustmentDate(request, db, value):
    if request.method == 'GET':
        getfromdate = request.GET.get('fromdate')
        gettodate = request.GET.get('todate')
        invoiceid = request.GET.get('invoiceid')
        #   sortbyItem = request.GET.get('sortbyItem')
        failed = {'failed': "No Data Found"}
        if getfromdate and gettodate:
                from_date, to_date =getdate(getfromdate, gettodate)
                getstock = StockAdjustmentLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)) & Q(type=value))
            
        if invoiceid  is not None or getfromdate and gettodate is not None:
            # whatever is in outlet is what i have in stock(installed) so i sort by outlet, that is == warehouse(sortby)
            getstock = StockAdjustmentLog.objects.using(db).filter(Q(invoice_no=invoiceid) & Q(type=value))
            if getstock:
                result = [({
                    'id': data.id if data and data.id is not None else None,
                    'datetx': data.datetx if data and data.datetx is not None else None,
                    'invoice_no': data.invoice_no if data and data.invoice_no is not None else None,
                    'item_code': data.item_code if data and data.item_code is not None else None,
                    'initial_qty': data.initial_qty if data and data.initial_qty is not None else None,
                    'new_qty': data.new_qty if data and data.new_qty is not None else None,
                    'Userlogin': data.Userlogin if data and data.Userlogin is not None else None,
                    })
                    for data in getstock
                ]
                return result
            else:
                return failed






@login_required(login_url='/')
@urls_name(name="Stock Adjustment")
def StockAdjustmentHistory(request):
   db = request.user.company_id.db_name
   stockinadjustmentlog = StockAdjustmentLog.objects.using(db).filter(type='stock')

   context = {
      'stockinadjustmentlog': stockinadjustmentlog,
   }

 
   # get function
   stockadjustmentdata =getStockAdjustmentDate(request, db, 'stock')
   if stockadjustmentdata:
     return JsonResponse({'data':stockadjustmentdata})

   return render(request, 'report/StockAdjustmentHistory.html', context)




@login_required(login_url='/')
@urls_name(name="Purchase Adjustment")
def PurchaseAdjustmentHistory(request):
   db = request.user.company_id.db_name
   stockinadjustmentlog = StockAdjustmentLog.objects.using(db).filter(type='purchase')

   context = {
      'adjustmentlog': stockinadjustmentlog,
   }

 
   # get function
   stockadjustmentdata =getStockAdjustmentDate(request, db, 'purchase')
   if stockadjustmentdata:
     return JsonResponse({'data':stockadjustmentdata})

   return render(request, 'report/PurchaseAdjustmentHistory.html', context)






# ********************************************************************************************************







def seriesReport(data, db):
    getaccttype = chart_of_account.objects.using(db).values('account_id', 'actual_balance', 'account_type').filter(Q(series_name=data) )
    return getaccttype

def AccountSeriesReport(request):
    db = AfrikBookDB(request)
    get_all_assets = seriesReport('Assets', db)
    get_all_liability = seriesReport('Liability', db)
    get_all_equity = seriesReport('Equity', db)
    
    context  = {
        'allassets': get_all_assets,
        'allliabilities': get_all_liability,
        'equities': get_all_equity,
    }
    return render(request, 'report/AccountSeriesReport.html', context)


@login_required(login_url='/')
@urls_name(name="Stock In Report")
def StockInReport(request):
    db = AfrikBookDB(request)
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
    
    storkReport= ForStockInReport(request, context, db)
    if storkReport:
        storkreport, qty = storkReport
        return JsonResponse({'data':storkreport, 'qty':qty})

    return render(request, 'report/StockInReport.html', context)




def OutletStockinReport(request):
    db = AfrikBookDB(request)
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

@login_required(login_url='/')
@urls_name(name="Sales Report")
def SalesReport(request):
    db = AfrikBookDB(request)
    company = company_table.objects.get(id=request.user.company_id_id)
    item_name = Item.objects.using(db).values("item_name")
    customer = customer_table.objects.using(db)
    sales = customer_invoice.objects.using(db).all().exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()
    try:
       note = company_details.objects.get(type='Invoice').detail
    except company_details.DoesNotExist:
        note=""

    sales_total = customer_invoice.objects.using(db).values("invoiceID").distinct().count()
    qty_total = customer_invoice.objects.using(db).aggregate(total_qty=Sum("qty"))['total_qty']

    context = {
        'sales':unique_invoices,
        'total_sales': 0.00,
        'qty_total':0.00,
        'item_name':item_name,
        'customer':customer,
        'company': company,
        'note': note
    }
   
    return render(request, 'report/SalesReport.html', context)

def StockIn(request):
   
    return render(request, 'report/StockIn.html')

@login_required(login_url='/')
@urls_name(name="Purchase Invoices")
def PurchaseInvoice(request):
    db = AfrikBookDB(request)
    item_name = Item.objects.using(db).values("item_name")
    sales = Vendor_invoice.objects.using(db).all().exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()
    company = company_table.objects.get(id=request.user.company_id_id)
    supplier = vendor_table.objects.using(db).all()
    operator = Vendor_invoice.objects.using(db).values("Userlogin").distinct()
    sales_total = Vendor_invoice.objects.using(db).values("invoiceID").distinct().count()
    qty_total = Vendor_invoice.objects.using(db).aggregate(total_qty=Sum("qty"))['total_qty']
    context = {
        'sales':unique_invoices,
        'sales_total':sales_total,
        'qty_total':qty_total,
        'item_name':item_name,
        'company': company,
        'supplier': supplier,
        'operator': operator
    }
   
    return render(request, 'report/PurchaseInvoice.html', context)

@login_required(login_url='/')
@urls_name(name="Payroll")
def PayrollReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = AfrikBookDB(request)
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

    total_amount = payroll.objects.using(db).aggregate(total=Sum('net_pay'))['total'] or 0.00
    
    context = {
        'payrolls':unique_payroll,
        'total_amount':total_amount,
        'years':years,
        'company': company
    }
   
    return render(request, 'report/PayrollReport.html', context)


@login_required(login_url='/')
@urls_name(name="Receivables")
def Receivables(request):
    db = AfrikBookDB(request)
    receivables = receivable.objects.using(db).all()
    customers = customer_table.objects.using(db).all()
    company = company_table.objects.get(id=request.user.company_id_id)

    # Calculate total amount where type is "credit"
    credit_total = receivable.objects.using(db).filter(type="credit").aggregate(total_credit=Sum("amount"))['total_credit'] or 0
    # Calculate total amount where type is "debit"
    debit_total = receivable.objects.using(db).filter(type="debit").aggregate(total_debit=Sum("amount"))['total_debit'] or 0
    
    
    
    balance = Decimal(credit_total) - Decimal(debit_total) 
        
    context = {
        'recievables':receivables,
        'credit':credit_total,
        'debit':debit_total,
        'balance':balance,
        'customers':customers,
        'company':company
    }
    return render(request, 'report/Receivables.html', context)


@login_required(login_url='/')
@urls_name(name="Aged Receivables")
def AgedReceivables(request):
    db = AfrikBookDB(request)
    customers = customer_table.objects.using(db).all()
    aged = receivable.objects.using(db).filter(amount__lt=F('initial_amount')).distinct()
    amount_total = receivable.objects.using(db).aggregate(total_amount=Sum("amount"))['total_amount']
    company = company_table.objects.get(id=request.user.company_id_id)
    
    if request.method == "POST":
        discount = request.POST.get("Discount")
        cost = request.POST.get("cost")
        customer = request.POST.get("customer")
        invoice = request.POST.get("invoice")
        today = datetime.now()
        try:
            cus = customer_table.objects.using(db).get(customer_code=customer)
            account = chart_of_account.objects.using(db).get(account_bankname="Sales account").account_id
            if discount == "NaN":
                description = "Payment Received"
                CreditReceivable(request, db, cus, today, description, "Transfer", account, cost)
                customer_invoice.objects.using(db).filter(invoiceID=invoice, cusID=customer).update(amount_paid=F('amount_paid')+cost)
            else:
                description = "Payment Received"
                CreditReceivable(request, db, cus, today, description, "Transfer", account, cost)
                description = "Discount Allowed"
                CreditReceivable(request, db, cus, today, description, "Transfer", account, discount)
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
        'amount_total':amount_total,
        'company': company
    }
    return render(request, 'report/AgedReceivables.html', context)


@login_required(login_url='/')
@urls_name(name="Payables")
def Payables(request):
    db = AfrikBookDB(request)
    receivables = payable.objects.using(db).all()
    vendors = vendor_table.objects.using(db).all()
    company = company_table.objects.get(id=request.user.company_id_id)
    
    # Calculate total amount where type is "credit"
    credit_total = payable.objects.using(db).filter(type="credit").aggregate(total_credit=Sum("amount"))['total_credit'] or 0.00
    # Calculate total amount where type is "debit"
    debit_total = payable.objects.using(db).filter(type="debit").aggregate(total_debit=Sum("amount"))['total_debit'] or 0.00

    
    if  credit_total is None and debit_total is None:
        balance =  0.00
    else:
        balance = Decimal(credit_total) - Decimal(debit_total)  
    
    
    context = {
        'recievables':receivables,
        'credit':credit_total,
        'debit':debit_total,
        'balance':balance,
        'vendors':vendors,
        'company': company
    }
   
    return render(request, 'report/Payables.html', context)


@login_required(login_url='/')
@urls_name(name="Aged Payable")
def AgedPayable(request):
    db = AfrikBookDB(request)
    vendors = vendor_table.objects.using(db).all()
    aged = payable.objects.using(db).filter(amount__lt=F('initial_amount')).distinct()
    amount_total = payable.objects.using(db).aggregate(total_amount=Sum("amount"))['total_amount']
    company = company_table.objects.get(id=request.user.company_id_id)
    
    if request.method == "POST":
       
        discount = request.POST.get("Discount")
        cost = request.POST.get("cost")
        vendor = request.POST.get("vendor")
        invoice = request.POST.get("invoice")
        today = datetime.now()
        try:
            ven = vendor_table.objects.using(db).get(custID=vendor)
            account = chart_of_account.objects.using(db).get(account_bankname="Purchase account").account_id
            if discount == "NaN":
                description = "Payment Received"
                CreditPayable(request, db, ven, today, description, "Transfer", account, cost)
                Vendor_invoice.objects.using(db).filter(invoiceID=invoice, cusID=vendor).update(amount_paid=F('amount_paid')+cost)
            else:
                description = "Payment Received"
                CreditPayable(request, db, ven, today, description, "Transfer", account, cost)
                description = "Discount Allowed"
                CreditPayable(request, db, ven, today, description, "Transfer", account, discount)
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
        'amount_total':amount_total,
        'company': company
    }
   
    return render(request, 'report/AgedPayable.html', context)

def GetCustomerDetailsAndInvoice(request, code, cusID):
    db = AfrikBookDB(request)
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
            # 'address': customer.address,
            'balance': customer.Balance,
           },
           "invoice": serialized_data
            
        }
       return JsonResponse(data)
    except customer_table.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewSalesLadger(request, code):
    db = AfrikBookDB(request)
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
    db = AfrikBookDB(request)
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
        #    address = customer.address
           balance = ""
       else:
           customer = customer_table.objects.using(db).get(lookups)
           name = customer.name
           phone = customer.phone
           email = customer.email
           category = customer.category
           cus_code = customer.customer_code
           company = customer.company_name
        #    address = customer.address
           balance = customer.Balance
              
        

       invoice = customer_invoice.objects.using(db).filter(invoiceID=code).values()
       serialized_data = list(invoice)

       amount_total = customer_invoice.objects.using(db).filter(invoiceID=code).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']

       try:
            vat = Vat.objects.using(db).get(source=code).amount
       except Vat.DoesNotExist:
            vat = None
    
       data={
           'serialized_data':serialized_data,
           'amount_total':amount_total,
           'vat':vat,
           "customer":{
            'name': name,
            'phone': phone,
            'email': email,
            'category': category,
            'code': cus_code,
            'company': company,
            # 'address': address,
            'balance': balance,
           }
       }
       return JsonResponse(data, safe=False)
    except customer_invoice.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewPurchase(request, code):
    db = AfrikBookDB(request)
    cusID = request.GET.get("cusID")
    
    if cusID:
        lookups = Q(id__iexact=cusID) | Q(custID__iexact=cusID)
    try:

       invoice = Vendor_invoice.objects.using(db).filter(invoiceID=code, cusID=cusID).values()
       vendor = vendor_table.objects.using(db).get(lookups)

       serialized_data = list(invoice)
      
       amount_total = Vendor_invoice.objects.using(db).filter(invoiceID=code, cusID=cusID).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']

       try:
            vat = Vat.objects.using(db).get(source=code).amount
       except Vat.DoesNotExist:
            vat = None

       data={
           'serialized_data':serialized_data,
           'amount_total':amount_total,
           'vat':vat,
           "vendor":{
            'name': vendor.name,
            'phone': vendor.phone,
            'email': vendor.email,
            # 'category': vendor.category,
            'code': vendor.custID,
            'company': vendor.company_name,
            # 'address': vendor.address,
            # 'balance': vendor.balance,
           }
       }
       return JsonResponse(data, safe=False)
    except Vendor_invoice.DoesNotExist: 
       
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def ViewPurchaseLadger(request, code):
    db = AfrikBookDB(request)
  
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

@login_required(login_url='/')
@urls_name(name="Customer Ledger")
def CustomerLedger(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    return render(request, 'report/CustomerLedger.html',{'company':company})

@login_required(login_url='/')
@urls_name(name="Customer Ledger")
def ViewCustomerLedger(request, code, invoice):
    db = AfrikBookDB(request)
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


@login_required(login_url='/')
@urls_name(name="Sales Ledger")
def SalesLedger(request):
    db = AfrikBookDB(request)
    item_name = Item.objects.using(db).values("item_name")
    sales = customer_invoice.objects.using(db).filter(invoice_state="Supplied").exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices = {sale.invoiceID: sale for sale in sales}.values()
    company = company_table.objects.get(id=request.user.company_id_id)

    sales_total = customer_invoice.objects.using(db).values("invoiceID").distinct().count()
    amount_total = customer_invoice.objects.using(db).values("invoiceID").distinct().aggregate(total_amount=Sum("amount"))['total_amount']

    context = {
        'sales':unique_invoices,
        'amount_total':amount_total,
        'item_name':item_name,
        'company':company
    }
   
   
    return render(request, 'report/SalesLedger.html', context)

def EditSalesLedgerDate(request):
    db = AfrikBookDB(request)
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

@login_required(login_url='/')
@urls_name(name="Purchase Ledger")
def PurchaseLedger(request):
    db = AfrikBookDB(request)
    item_name = Item.objects.using(db).values("item_name")
    sales = Vendor_invoice.objects.using(db).all() #.distinct()
    # sales = Vendor_invoice.objects.filter(invoice_state="Supplied").exclude(invoiceID__icontains=str('returned')) #.distinct()
    unique_invoices =  {sale.invoiceID: sale for sale in sales}.values()
    company = company_table.objects.get(id=request.user.company_id_id)

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
        'balance':balance,
        'company': company
    }
   
    return render(request, 'report/PurchaseLedger.html', context)

def EditPurchaseLedgerDate(request):
    db = AfrikBookDB(request)
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

@login_required(login_url='/')
@urls_name(name="Vendor Ledger")
def VendorLedger(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    return render(request, 'report/VendorLedger.html', {'company': company})

@login_required(login_url='/')
@urls_name(name="Vendor Ledger")
def ViewVendorLedger(request, code, invoice):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = AfrikBookDB(request)
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
        'balance':balance,
        'company':company    
    }
   
    return render(request, 'report/ViewVendorLedger.html',context)


def CheckStockCondition(request):
   
    return render(request, 'report/CheckStockCondition.html')




def stockReport_none_iterable_result_unused(model1, model2, begin, end, fromdate, todate, daily, db):
    timeRange = None
    current_qty = 0.00
    No_qty = 0.00
    selling_price = 0.00
    if fromdate and todate is not None:
        from_date, to_date = getdateReport(fromdate, todate)
        timeRange = Q(datetx__range=(from_date, to_date))
    if begin and end != '_ _Choose Hour_ _':
        from_time, to_time, fromtimeDate = gettime(begin, end, fromdate)
        timeRange = (Q(datetx=fromtimeDate) & Q(datetx__time__range=(from_time, to_time)))

    try:
        if timeRange is not None:
            qs_for_log = model1.objects.using(db).filter(timeRange)
            for qs in qs_for_log:
                c_qty = model2.objects.using(db).get(item_code=qs.item_code)
                current_qty = float(current_qty) + float(c_qty.quantity)

            AM = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]
            # PM = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
            period1 = 'am' if begin in AM else 'pm'
            period2 = 'am' if end in AM  else 'pm'
        
            from_ =  begin+period1 if begin != '_ _Choose Hour_ _' else from_date
            to_ =  end+period2 if end != '_ _Choose Hour_ _' else to_date
            for i in qs_for_log:
                No_qty = float(No_qty) + float(i.quantity)
                No_qty = float(No_qty) + float(i.quantity) 
                selling_price = float(selling_price) + float(i.selling_price)

            No_items = qs_for_log.count()
            if daily == 'daily':
                from_ =  datetime.strptime(fromdate, '%Y-%m-%d').strftime('%A')
                to_ =  datetime.strptime(todate, '%Y-%m-%d').strftime('%A')

            stockLevel={
                'datetx': from_date if from_date is not None else None,
                'begin': from_ if from_ is not None else None,
                'end': to_ if to_ is not None else None,
                'Noqty': No_qty if No_qty is not None else None,
                'Noitems': No_items if No_items is not None else None,
                'selling_price': selling_price if selling_price is not None else None,
                # 'previous_qty': item.quantity if item.quantity is not None else None,
                'current_qty': current_qty if current_qty is not None else None,
            } 
            return stockLevel 
    except model1.DoesNotExist:
        pass



def stockReport2(model1, model2, begin, end, fromdate, todate, daily, db):
    timeRange = None
    current_qty = 0.00
    No_qty = 0.00
    selling_price = 0.00
    stockLevel = []
    indices_to_delete=[]
    if fromdate and todate is not None:
        from_date, to_date = getdateReport(fromdate, todate)
        timeRange = Q(datetx__range=(from_date, to_date))
    if begin and end != '_ _Choose Hour_ _':
        from_time, to_time, fromtimeDate = gettime(begin, end, fromdate)
        timeRange = (Q(datetx=fromtimeDate) & Q(datetx__time__range=(from_time, to_time)))

    try:
        if timeRange is not None:
            qs_for_log = model1.objects.using(db).filter(timeRange)

            
            for qs in qs_for_log:
                # c_qty = model2.objects.using(db).get(item_code=qs.item_code)
                # current_qty = float(current_qty) + float(c_qty.quantity)
                if daily == 'daily':
                    from_ =  datetime.strptime(str(qs.datetx), '%Y-%m-%d').strftime('%A')
                    to_ =  datetime.strptime(todate, '%Y-%m-%d').strftime('%A')

                # for index, data in enumerate(stockLevel):
                #     if 'datetx' in data and data['datetx'] == qs.datetx:
                #         # Update quantities and prices
                #         data['Noqty'] = float(data['Noqty']) + float(qs.quantity)
                #         data['selling_price'] = float(data['selling_price']) + float(qs.selling_price)
               
                #         # Mark the index for deletion
                #         indices_to_delete.append(index)
               
                    # else:
                stockLevel.append({
                    'datetx': qs.datetx if qs and qs.datetx is not None else None,
                    'begin': from_ if from_ is not None else None,
                    'end': to_ if to_ is not None  else None,
                    'Noqty': qs.quantity if qs and qs.quantity is not None else None,
                    'Noitems': qs.item if qs and qs.item is not None else None,
                    'selling_price': qs.selling_price if qs and qs.selling_price is not None else None,
                    # 'previous_qty': item.quantity if item.quantity is not None else None,
                })
            # for index in sorted(indices_to_delete, reverse=True):
            #     del stockLevel[index]
            return stockLevel 
    except model1.DoesNotExist:
        pass
    # if you want to use this function, copy the below code to where you want to call it
        # if request.method == 'GET':
        #     begin = request.GET.get('begin')
        #     end = request.GET.get('end')
        #     daily = request.GET.get('daily')
        #     fromdate    = request.GET.get('fromdate')
        #     todate      = request.GET.get('todate')
        #     from_time = time(14, 0)
        #     to_time = time(16, 0)
        #     stock_level_data= stockReport2(CreateOutletStockInLog, CreateOutletStockIn, begin, end, fromdate, todate, daily, db)
        #     if stock_level_data is not None:
        #         stockLevel = stock_level_data
        #         return JsonResponse({'data': stockLevel})



def OutletStockLevelReport(request):
    db = AfrikBookDB(request)

    if request.method == 'GET':
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        Yearly      = request.GET.get('Yearly')
        monthly      = request.GET.get('monthly')
        Quaterly      = request.GET.get('Quaterly')
       
        if fromdate and todate is not None or Yearly is not None or monthly or Quaterly:
           return levelReportOutlet(request, db, fromdate, todate, daily, Yearly, monthly, Quaterly)
            

    return render(request, 'report/OutletStockLevelReport.html')



def levelReportOutlet(request, db, fromdate, todate, daily, year, month, quater):
    quaterLog =[]
    if daily == 'daily':
        from_date, to_date = getdateReport(fromdate, todate)
        select_date_range = Q(datetx__range=(from_date, to_date))
    elif daily == 'monthly':
        period = month
        select_date_range = Q(datetx__year=year) & Q(datetx__month=month)
        select_date_range_for_cusInv = Q(invoice_date__year=year) & Q(invoice_date__month=month)
    elif daily == 'quaterly':
        date_parts= quater.split('-')
        num = int(date_parts[0])

        while num <= int(date_parts[1]):
            quaterLog.append(num)
            num = num + 1
        # period = quater
        select_date_range = (Q(datetx__year=year) & Q(datetx__month__range=(date_parts[0], date_parts[1])))
        
    else:
        period = year
        select_date_range = Q(datetx__year=year)
        select_date_range_for_cusInv = Q(invoice_date__year=year)
    try:
        report = CreateOutletStockInLog.objects.using(db).filter(select_date_range)
        if report.count() > 1:
            itemLog =[]
            period_log =[]
            non_dict_item_log =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_outlet =0.00
            all_qty_sent_within_outlet_table =0.00
            all_qty_sold_from_outlet =0.00
            all_qty_sent_from_outlet =0.00
            count = 0
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)
                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                # year = date_obj.strftime('%Y')
                # month = date_obj.strftime('%m')
                if daily == 'daily':
                    period = strDate
                    select_date_range = Q(datetx=strDate)
                    select_date_range_for_cusInv = Q(invoice_date=strDate)
                elif daily == 'quaterly':
                    period = quaterLog[count]
                    if count != len(quaterLog) -1:
                        count = count + 1
                    select_date_range = (Q(datetx__year=year) & Q(datetx__month=str(period)))
                    select_date_range_for_cusInv = Q(invoice_date__year=year) & Q(invoice_date__month=str(period))
                # elif daily == 'monthly':
                #     period = month
                #     select_date_range = Q(datetx__year=year) & Q(datetx__month=month)
                #     select_date_range_for_cusInv = Q(invoice_date__year=year) & Q(invoice_date__month=month)
                # else:
                #     period = year
                #     select_date_range = Q(datetx__year=year)
                #     select_date_range_for_cusInv = Q(invoice_date__year=year)

                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    qtyLevel = currentStockLevel_Outlet(db, data.item_code)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item, 'qtyLevel':qtyLevel})


                if  period not in period_log:
                    period_log.append(period)
                    total_qty = 0
                    all_qty_sent_to_outlet =0.00
                    all_qty_sent_within_outlet_table =0.00
                    all_qty_sold_from_outlet =0.00
                    all_qty_sent_from_outlet =0.00
                    all_qty_sent_to_warehouse_for_that_day = CreateOutletStockInLog.objects.using(db).filter(~Q(outlet=None) & select_date_range)
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_outlet_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop')  & select_date_range)
                    for outlet_qty_in_warehouse in get_item_transfered_from_outlet_to_warehouse:
                        all_qty_sent_from_outlet = float(all_qty_sent_from_outlet) + float(outlet_qty_in_warehouse.quantity)
                    
                    get_item_transfered_from_outlet_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop') & select_date_range)
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_outlet_table = float(all_qty_sent_within_outlet_table) + float(outlet_qty_in_outlet.quantity)

                    get_item_sold_from_outlet = customer_invoice.objects.using(db).filter(~Q(cancellation_status=1) & select_date_range_for_cusInv)
                    for warehouse_qty_in_outlet in get_item_sold_from_outlet:
                        all_qty_sold_from_outlet = float(all_qty_sold_from_outlet) + float(warehouse_qty_in_outlet.qty)

                    add_deductions = float(all_qty_sent_from_outlet) + float(all_qty_sold_from_outlet) + float(all_qty_sent_within_outlet_table)
                    total_qty = float(all_qty_sent_to_outlet) - float(add_deductions)

                    # non_dict_year_log.append(year)
                    # non_dict_month_log.append(month)

                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    


                    if daily == 'daily':
                        date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                        day_of_week_name = date_obj.strftime('%A')
                        DayLog.append(day_of_week_name)
                    elif daily == 'monthly':
                        fullmonthName = date_obj.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    elif daily == 'quaterly':
                        date_obj_ = datetime.strptime(str(period), '%m')
                        fullmonthName = date_obj_.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    else:
                        DayLog.append('{year}'.format(year=year))

                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == year:
                    #         item['qty'] = total_qty

            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})


            # return render(request, 'report/OutletStockLevelReport.html')
        else:
            return JsonResponse({'error': 'No record found'})
    except CreateOutletStockInLog.DoesNotExist:
            return JsonResponse({'error': 'No record found'})



def currentStockLevel_Outlet(db, item_):
    all_qty_sent_to_store = 0.00
    all_qty_sent_from_store = 0.00
    all_qty_sent_within_store_table = 0.00
    all_qty_sold_from_outlet = 0.00
    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(Q(item_code=item_))
    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
        all_qty_sent_to_store = float(all_qty_sent_to_store) + float(warehouse_qty_sent_to_warehouse.quantity)

    get_item_transfered_from_outlet_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(item_code=item_))
    for outlet_qty_in_warehouse in get_item_transfered_from_outlet_to_warehouse:
        all_qty_sent_from_store = float(all_qty_sent_from_store) + float(outlet_qty_in_warehouse.quantity)
    
    get_item_transfered_from_outlet_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(item_code=item_))
    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
        all_qty_sent_within_store_table = float(all_qty_sent_within_store_table) + float(outlet_qty_in_outlet.quantity)

    get_item_sold_from_outlet = customer_invoice.objects.using(db).filter(~Q(cancellation_status=1) & Q(itemcode=item_))
    for warehouse_qty_in_outlet in get_item_sold_from_outlet:
        all_qty_sold_from_outlet = float(all_qty_sold_from_outlet) + float(warehouse_qty_in_outlet.qty)

 
    add_deductions = float(all_qty_sent_from_store)  + float(all_qty_sent_within_store_table) + float(all_qty_sold_from_outlet)
    total_qty = float(all_qty_sent_to_store) - float(add_deductions)
    return total_qty

            





def WarehouseStockLevelReport(request):
    db = AfrikBookDB(request)

    if request.method == 'GET':
        daily       = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        Yearly      = request.GET.get('Yearly')
        monthly      = request.GET.get('monthly')
        Quaterly      = request.GET.get('Quaterly')
        if fromdate and todate is not None or Yearly is not None or monthly or Quaterly:
           return levelReportWarehouse(request, db, fromdate, todate, daily, Yearly, monthly, Quaterly)
   
    return render(request, 'report/WarehouseStockLevelReport.html')




def levelReportWarehouse(request, db, fromdate, todate, daily, year, month, quater):
    quaterLog =[]
    if daily == 'daily':
        from_date, to_date = getdateReport(fromdate, todate)
        select_date_range = Q(datetx__range=(from_date, to_date))
    elif daily == 'monthly':
        period = month
        select_date_range = (Q(datetx__year=year) & Q(datetx__month=month))
    elif daily == 'quaterly':
        date_parts= quater.split('-')
        num = int(date_parts[0])

        while num <= int(date_parts[1]):
            quaterLog.append(num)
            num = num + 1
        # period = quater
        select_date_range = (Q(datetx__year=year) & Q(datetx__month__range=(date_parts[0], date_parts[1])))
    else:
        period = year
        select_date_range = Q(datetx__year=year)
    try:
        report = CreateStockInLog.objects.using(db).filter(select_date_range)
        if report.count() > 1:
            itemLog =[]
            period_log =[]
            non_dict_item_log =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_warehouse =0.00
            all_qty_sent_from_warehouse =0.00
            all_qty_sent_within_warehouse_table =0.00
            count = 0
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)
                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                # year = date_obj.strftime('%Y')
                # month = date_obj.strftime('%m')
                if daily == 'daily':
                    period = strDate
                    select_date_range = Q(datetx=strDate)
                elif daily == 'quaterly':
                    period = quaterLog[count]
                    if count != len(quaterLog) -1:
                        count = count + 1
                    select_date_range = (Q(datetx__year=year) & Q(datetx__month=str(period)))
                # elif daily == 'monthly':
                #     period = month
                #     select_date_range = Q(datetx__year=year) & Q(datetx__month=month)
                # else:
                #     period = year
                #     select_date_range = Q(datetx__year=year)

                if itemName not in non_dict_item_log:
                    # qtyLevel=0.00
                    non_dict_item_log.append(itemName)
                    qtyLevel = currentStockLevel(db, data.item_code)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item, 'qtyLevel':qtyLevel})

                if  period not in period_log:
                    period_log.append(period)
                    total_qty =0.00
                    all_qty_sent_to_warehouse =0.00
                    all_qty_sent_from_warehouse =0.00
                    all_qty_sent_within_warehouse_table =0.00
                    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(~Q(outlet=None) & select_date_range)
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_warehouse_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & select_date_range)
                    for warehouse_qty_in_outlet in get_item_transfered_from_warehouse_to_outlet:
                        all_qty_sent_from_warehouse = float(all_qty_sent_from_warehouse) + float(warehouse_qty_in_outlet.quantity)
                    

                    get_item_transfered_from_outlet_to_outlet = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & select_date_range)
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_warehouse_table = float(all_qty_sent_within_warehouse_table) + float(outlet_qty_in_outlet.quantity)

                    add_deductions = float(all_qty_sent_from_warehouse) + float(all_qty_sent_within_warehouse_table)

                    total_qty = float(all_qty_sent_to_warehouse) - float(add_deductions)

                    # non_dict_year_log.append(year)
                    # non_dict_month_log.append(month)

                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    


                    if daily == 'daily':
                        date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                        day_of_week_name = date_obj.strftime('%A')
                        DayLog.append(day_of_week_name)
                    elif daily == 'monthly':
                        fullmonthName = date_obj.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    elif daily == 'quaterly':
                        date_obj_ = datetime.strptime(str(period), '%m')
                        fullmonthName = date_obj_.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    else:
                        DayLog.append('{year}'.format(year=year))

                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == year:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        else:
            return JsonResponse({'error': 'No record found'})
    except CreateStockInLog.DoesNotExist:
            return JsonResponse({'error': 'No record found'})
   





def currentStockLevel(db, item_, total_qty=0.00):
    all_qty_sent_to_store = 0.00
    all_qty_sent_from_store = 0.00
    all_qty_sent_within_store_table = 0.00
    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(Q(item_code=item_))
    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
        all_qty_sent_to_store = float(all_qty_sent_to_store) + float(warehouse_qty_sent_to_warehouse.quantity)

    get_item_transfered_from_outlet_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(item_code=item_))
    for outlet_qty_in_warehouse in get_item_transfered_from_outlet_to_warehouse:
        all_qty_sent_from_store = float(all_qty_sent_from_store) + float(outlet_qty_in_warehouse.quantity)
    
    get_item_transfered_from_outlet_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(item_code=item_))
    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
        all_qty_sent_within_store_table = float(all_qty_sent_within_store_table) + float(outlet_qty_in_outlet.quantity)

    add_deductions = float(all_qty_sent_from_store)  + float(all_qty_sent_within_store_table)
    total_qty = float(all_qty_sent_to_store) - float(add_deductions)
    return total_qty










def report_payroll_filter_by_date(request):
    db = AfrikBookDB(request)
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





def WarehouseStockinReport(request):
    db = AfrikBookDB(request)

    if request.method == 'GET':
        daily       = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        Yearly      = request.GET.get('Yearly')
        monthly     = request.GET.get('monthly')
        Quaterly    = request.GET.get('Quaterly')
        if fromdate and todate is not None or Yearly is not None or monthly or Quaterly:
           return WarehouseReport(request, db, fromdate, todate, daily, Yearly, monthly, Quaterly)
   
    return render(request, 'report/warehouseStockinReport.html')

def WarehouseReport(request, db, fromdate, todate, daily, year, month, quater):
    data = []
    items = Item.objects.using(db).all()
    if daily == 'daily':
        from_date, to_date = getdateReport(fromdate, todate)
        select_date_range = Q(datetx__range=(from_date, to_date))
        period = fromdate +" to "+ todate
    elif daily == 'monthly':
        mm = year+"-"+month+"-01"
        m = datetime.strptime(mm, '%Y-%m-%d')
        
        period = m.strftime('%B')+" "+year
        select_date_range = (Q(datetx__year=year) & Q(datetx__month=month))
    elif daily == 'quaterly':
        date_parts= quater.split('-')
        num = int(date_parts[0])
        period = None
        if quater == "01-04":
           period = "January - April" 
        elif quater == "05-08":
            period = "May - August"
        elif quater == "09-12":
            period = "September - December"
        
        # while num <= int(date_parts[1]):
        #     quaterLog.append(num)
        #     num = num + 1
        select_date_range = (Q(datetx__year=year) & Q(datetx__month__range=(date_parts[0], date_parts[1])))
    else:
        period = year
        select_date_range = Q(datetx__year=year)
    
    for item in items:
        report = CreateStockInLog.objects.using(db).filter(select_date_range, item_code=item.generated_code).values().aggregate(total=Sum('quantity'))['total'] or 0.0
        entry = {
            'item':item.item_name,
            'report': report,
            'period':period
        }
        
        if not any(record['item'] == item.item_name and record['period'] == period for record in data):
            data.append(entry)
   
    if data is not None:
            return JsonResponse({'data': list(data)})
    else:
        return JsonResponse({'error': 'No record found'})

def WarehouseReports(request, db, fromdate, todate, daily, year, month, quater):
    quaterLog =[]
    if daily == 'daily':
        from_date, to_date = getdateReport(fromdate, todate)
        select_date_range = Q(datetx__range=(from_date, to_date))
    elif daily == 'monthly':
        period = month
        select_date_range = (Q(datetx__year=year) & Q(datetx__month=month))
    elif daily == 'quaterly':
        date_parts= quater.split('-')
        num = int(date_parts[0])

        while num <= int(date_parts[1]):
            quaterLog.append(num)
            num = num + 1
        # period = quater
        select_date_range = (Q(datetx__year=year) & Q(datetx__month__range=(date_parts[0], date_parts[1])))
    else:
        period = year
        select_date_range = Q(datetx__year=year)
    try:
        report = CreateStockInLog.objects.using(db).filter(select_date_range)
        if report.count() > 1:
            itemLog =[]
            period_log =[]
            non_dict_item_log =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_warehouse =0.00
            all_qty_sent_from_warehouse =0.00
            all_qty_sent_within_warehouse_table =0.00
            count = 0
            for data in report:
                strDate = str(data.datetx)
                warehouseName = str(data.outlet)
                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                if daily == 'daily':
                    period = strDate
                    select_date_range = Q(datetx=strDate)
                elif daily == 'quaterly':
                    period = quaterLog[count]
                    if count != len(quaterLog) -1:
                        count = count + 1
                    select_date_range = (Q(datetx__year=year) & Q(datetx__month=str(period)))

                if warehouseName not in non_dict_item_log:
                    non_dict_item_log.append(warehouseName)
                    # qtyLevel = currentStockLevel(db, data.item_code)
                    qtyLevel = 0
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'warehouse':data.outlet, 'qtyLevel':qtyLevel})
           
                if  period not in period_log:
                    period_log.append(period)
                    all_qty_sent_to_warehouse =0.00
                    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(Q(outlet=data.outlet) & select_date_range )
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)
                    qtyLog.append({'qty':all_qty_sent_to_warehouse, 'warehouse':data.outlet, 'month':month, 'date':strDate})
                    

                    if daily == 'daily':
                        date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                        day_of_week_name = date_obj.strftime('%A')
                        DayLog.append(day_of_week_name)
                    elif daily == 'monthly':
                        fullmonthName = date_obj.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    elif daily == 'quaterly':
                        date_obj_ = datetime.strptime(str(period), '%m')
                        fullmonthName = date_obj_.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    else:
                        DayLog.append('{year}'.format(year=year))
                else:
                    pass
            
            # for index, item in enumerate(itemLog):
            #     for inde, qty in enumerate(qtyLog):
            #         if qty['date'] == item['date'] and qty['warehouse'] != item['warehouse']:
            #             all_qty_sent_to_warehouse =0.00
            #             all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(Q(outlet=item['warehouse']) & Q(datetx=item['date']) )
            #             for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
            #                 all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)
            #             # qtyLog.append({'qty':all_qty_sent_to_warehouse, 'warehouse':item['warehouse'].append(), 'month':month, 'date':strDate})
            #             qty['qty'].append(all_qty_sent_to_warehouse)
            #         else:
            
            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        else:
            return JsonResponse({'error': 'No record found'})
    except CreateStockInLog.DoesNotExist:
            return JsonResponse({'error': 'No record found'})



# Sales Report
from .functions.sales.sales import *
from .functions.sales.customer import *

def HourlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    if request.method == "POST":
        day = request.POST.get("day")
        start_date = datetime.strptime(day, '%Y-%m-%d').date()
       
        hourly_sales_data, total_sales, total_qty = hourly_sales_func(request, start_date, start_date)
    else:
        day =  datetime.now().date()
       
        hourly_sales_data, total_sales, total_qty = hourly_sales_func(request, day, day)
    
    
    
    context = {
        'hourly_sales_data': hourly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'day': day,
        'company': company
    }
  
    return render(request, 'report/Hourly.html', context)


@login_required(login_url='/')
@urls_name(name="Sales Report")
def DailySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            start = start_date
            end = end
            daily_sales_data, total_sales, total_purchase, total = daily_sales_report(request, start_date, end_date)
        else:
            start =  datetime.now().date()
            end = None
            daily_sales_data, total_sales, total_purchase, total = daily_sales_report(request, start, None)
       
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now().date()
        end = None
        daily_sales_data, total_sales, total_purchase, total = daily_sales_report(request, start, None)
         
    
    context = {
        'daily_sales_data':daily_sales_data,
        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'total': total,
        'company': company,
        'start': start,
        'end': end
        
        }
    
    return render(request, 'report/Daily.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def MonthlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m') #.date()
            end_date = datetime.strptime(end, '%Y-%m') #.date()
            start = start_date
            end = end
            monthly_sales_data, total_sales,  total_purchase, total = monthly_sales_report(request, start_date, end_date)
        else:
            start =  datetime.now() #.date()
            end = None
            monthly_sales_data, total_sales,  total_purchase, total = monthly_sales_report(request, start, None)
       
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_s_price':total_s_price})
        
    else:
        start =  datetime.now() #.date()
        end = None
        monthly_sales_data, total_sales,  total_purchase, total = monthly_sales_report(request, start, None)
        
    context = {
        'monthly_sales_data':monthly_sales_data,
        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'total': total,
        'company': company,
        'start': start,
        'end': end
        }
    
    return render(request, 'report/Monthly.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def QuaterlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    if request.method == "POST":
        start = request.POST.get("start_date")
        if start:
            start_date = datetime.strptime(start, '%Y-%m-%d') 
            start = start_date
            quaterly_sales_data, total_sales, total_purchase, total = quaterly_sales_report(request, start_date)
        else:
            start =  datetime.now() #.date()
          
            quaterly_sales_data, total_sales, total_purchase, total = quaterly_sales_report(request, start)
       
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_purchase, total':total_purchase, total})
        
    else:
        start =  datetime.now() #.date()
        
        quaterly_sales_data, total_sales, total_purchase, total = quaterly_sales_report(request, start)
       
    context = {
        'quaterly_sales_data':quaterly_sales_data,
        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'total': total,
        'company': company,
        'start': start.year,
        }
    
    return render(request, 'report/Quaterly.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def YearlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            start = start_date
            end = end
            yearly_sales_data, total_sales, total_purchase, total = yearly_sales_report(request, start_date, end_date)
        else:
            start =  datetime.now().date()
            end = None
            yearly_sales_data, total_sales, total_purchase, total = yearly_sales_report(request, start, None)
       
            messages.error(request, 'Enter valid Year')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_purchase, total':total_purchase, total})
        
    else:
        start =  datetime.now().date()
        end = None
        yearly_sales_data, total_sales, total_purchase, total = yearly_sales_report(request, start, None)
        
    context = {
        'yearly_sales_data':yearly_sales_data,
        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'total': total,
        'company': company, 
        'start': start,
        'end': end  
        }
    
    return render(request, 'report/Yearly.html', context)


@login_required(login_url='/')
@urls_name(name="Sales Report")
def CustomerMonthlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db)
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m') #.date()
            end_date = datetime.strptime(end, '%Y-%m') #.date()
            monthly_sales_data, total_sales, total_qty = customer_monthly_sales_report(request, start_date, end_date, customer, 1)
            cols = end_date.month
        else:
            start =  datetime.now() #.date()
    
            monthly_sales_data, total_sales, total_qty = customer_monthly_sales_report(request, start, None, customer, 1)
            cols = 1
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now() #.date()
        cols = 1
        monthly_sales_data, total_sales, total_qty = customer_monthly_sales_report(request, start, None, customer, 1)
        
    context = {
        'customer':customer.all(),
        'customers':customer,
        'monthly_sales_data':monthly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'company': company,
        'cols': cols + 1
        
        }
    
    return render(request, 'customer_sales/Monthly.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def CustomerQuaterlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    if request.method == "POST":
        start = request.POST.get("start_date")
        if start:
            start_date = datetime.strptime(start, '%Y-%m-%d') #.date()
            quarterly_sales_data, total_sales, total_qty = customer_quaterly_sales_report(request, start_date, customer, 1)
            
        else:
            start =  datetime.now() #.date()
    
            quarterly_sales_data, total_sales, total_qty = customer_quaterly_sales_report(request, start, customer, 1)
       
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now() #.date()
    
        quarterly_sales_data, total_sales, total_qty = customer_quaterly_sales_report(request, start, customer, 1)
        
    context = {
        'customer':customer.all(),
        'customers':customer,
        'quarterly_sales_data':quarterly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'company': company,
        'cols': customer.count() + 1
        
        }
    
    
    return render(request, 'customer_sales/Quaterly.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def CustomerYearlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db)
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start:
            start_date = datetime.strptime(start, '%Y-%m-%d') #.date()
            end_date = datetime.strptime(end, '%Y-%m-%d') #.date()
            yearly_sales_data, total_sales, total_qty = customer_yearly_sales_report(request, start_date, end_date, customer, 1)
        else:
            start =  datetime.now() #.date()
    
            yearly_sales_data, total_sales, total_qty = customer_yearly_sales_report(request, start, start_date, customer, 1)
       
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now() #.date()
    
        yearly_sales_data, total_sales, total_qty = customer_yearly_sales_report(request, start, start, customer, 1)
        
    context = {
        'customer':customer.all(),
        'customers':customer,
        'yearly_sales_data':yearly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'company': company,
        'cols': customer.count() + 1
        
        }
    
    return render(request, 'customer_sales/Yearly.html', context)


@login_required(login_url='/')
@urls_name(name="Sales Report")
def SalesPersonMonthlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = request.user.company_id.db_name
    customer = customer_invoice.objects.using(db).values('Userlogin').distinct()  
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m') #.date()
            end_date = datetime.strptime(end, '%Y-%m') #.date()
            monthly_sales_data, total_sales, total_qty = customer_monthly_sales_report(request, start_date, end_date, customer, 2)
            cols = end_date.month
            
        else:
            start =  datetime.now() #.date()
    
            monthly_sales_data, total_sales, total_qty = customer_monthly_sales_report(request, start, None, customer, 2)
            cols = 1
            messages.error(request, 'Enter valid date')
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now() #.date()
        
        cols = 1
        
        monthly_sales_data, total_sales, total_qty = customer_monthly_sales_report(request, start, None, customer, 2)
     
    context = {
        'customer':customer.all(),
        'customers':customer,
        'monthly_sales_data':monthly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'company': company,
        'cols': cols + 1
        
        }
    
    return render(request, 'sales_person/Monthly.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def SalesPersonQuaterlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = request.user.company_id.db_name
    customer = customer_invoice.objects.using(db).values('Userlogin').distinct()
    if request.method == "POST":
        start = request.POST.get("start_date")
        if start:
            start_date = datetime.strptime(start, '%Y-%m-%d') #.date()
            quarterly_sales_data, total_sales, total_qty = customer_quaterly_sales_report(request, start_date, customer, 2)
        else:
            start =  datetime.now() #.date()
    
            quarterly_sales_data, total_sales, total_qty = customer_quaterly_sales_report(request, start, customer, 2)
       
            messages.error(request, 'Enter valid date')
        
        
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now() #.date()
    
        quarterly_sales_data, total_sales, total_qty = customer_quaterly_sales_report(request, start, customer, 2)
        
    context = {
        'customer':customer.all(),
        'customers':customer,
        'quarterly_sales_data':quarterly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'company': company,
        'cols': customer.count() + 1
        
        }
    
    return render(request, 'sales_person/Quaterly.html', context)

@login_required(login_url='/')
@urls_name(name="Sales Report")
def SalesPersonYearlySalesReport(request):
    company = company_table.objects.get(id=request.user.company_id_id)
    db = request.user.company_id.db_name
    customer = customer_invoice.objects.using(db).values('Userlogin').distinct()
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        if start:
            start_date = datetime.strptime(start, '%Y-%m-%d') #.date()
            end_date = datetime.strptime(end, '%Y-%m-%d') #.date()
            yearly_sales_data, total_sales, total_qty = customer_yearly_sales_report(request, start_date, end_date, customer, 2)
        else:
            start =  datetime.now() #.date()
    
            yearly_sales_data, total_sales, total_qty = customer_yearly_sales_report(request, start, start_date, customer, 2)
       
            messages.error(request, 'Enter valid date')
        
        # JsonResponse({'data':daily_sales_data, 'total_sales': total_sales, 'total_qty':total_qty})
        
    else:
        start =  datetime.now() #.date()
    
        yearly_sales_data, total_sales, total_qty = customer_yearly_sales_report(request, start, start, customer, 2)
        
    context = {
        'customer':customer.all(),
        'customers':customer,
        'yearly_sales_data':yearly_sales_data,
        'total_sales': total_sales,
        'total_qty': total_qty,
        'company': company,
        'cols': customer.count() + 1
        
        }
    
    return render(request, 'sales_person/Yearly.html', context)




import openpyxl
# from openpyxl.writer.excel import save_virtual_workbook
from django.http import HttpResponse
import json, io

def export_sales_report_to_excel(request):
    if request.method == 'POST':
        # Parse JSON data from the request
        data = json.loads(request.body.decode('utf-8'))
        table_data = data.get('table_data', [])
        #  heading = data.get('heading', '')
        total_sales = data.get('total_sales', '')
        total_expenses = data.get('total_expenses', '')
        balance = data.get('balance', '')
        
        # Create a workbook and a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Sales Report'

        # Populate the worksheet with table data
        for row in table_data:
            worksheet.append(row)

        # Append totals
        # worksheet.append([])
      
        worksheet.append(['', '', '', '', '', '', ''])
        worksheet.append(['', '', '', '', '', '', ''])
        if total_sales != "":
           worksheet.append(['Total Sales', '', '', '', '', '', total_sales])
        if total_expenses != "":
           worksheet.append(['Total Expenses', '', '', '', '', '', total_expenses])
        if balance != "":
           worksheet.append(['Balance', '', '', '', '', '', balance])

        # Save the workbook to a BytesIO object
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        # Create HTTP response with the Excel file
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'

        return response
    else:
        return HttpResponse(status=405)  # Method Not Allowed