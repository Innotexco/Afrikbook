from django.shortcuts import render, redirect
from .models import loan_account, loan_account, new_journal_entry
from .fuctions.loanaccount import *
from .fuctions.journal import *
from .fuctions.receivepayment import *
from customer.models import customer_table
from vendor.models import vendor_table
from employee.models import employee
from account.models import *
from django.http import JsonResponse
from django.db.models import Sum
from customer.utils import generate_invoice_id
from django.contrib.auth.decorators import login_required
from routers.page_permission import  urls_name
# Create your views here.

@login_required(login_url='/')
@urls_name(name="Add New Journal")
def NewJournal(request):
    db = request.user.company_id.db_name
    loan = loan_account.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    Accounts = chart_of_account.objects.using(db).all()
    acc_types = accounts.objects.using(db).all()
    
    form = None
    if request.method == "POST":
       form = create_new_journal_enty(request, db)  
    context = {
        'vendor':vendor,
        'accounts':Accounts,
        'acc_types':acc_types,
        'invoice': generate_invoice_id(),
        'form': form,
    } 
    return render(request, "journal/NewJournalEntry.html", context)

@login_required(login_url='/')
@urls_name(name="Add New Journal")
def ViewJournalEntry(request):
    db = request.user.company_id.db_name

    unique_invoices = new_journal_entry.objects.using(db).values('invoice_no').distinct()

    # Fetch other columns for each unique invoice
    invoices_data = []
    for invoice in unique_invoices:
        invoice_data = new_journal_entry.objects.using(db).filter(invoice_no=invoice['invoice_no'])

        if invoice_data.exists():
            invoices_data.append(invoice_data.first())


  
    return render(request, 'journal/ViewJournalEntry.html', {'journals':invoices_data})


@login_required(login_url='/')
@urls_name(name="Journal Entries")
def ViewJournalEntryItem(request, invoice):
    db = request.user.company_id.db_name
    vendor = vendor_table.objects.using(db).all()
    Accounts = chart_of_account.objects.using(db).all()
    acc_types = accounts.objects.using(db).all()
    if invoice:
        # lookups = Q(id__iexact=code) | Q(customer_code__iexact=code)
   
        # customer = customer_table.objects.filter(lookups).first()
    
        
        invoice1 = new_journal_entry.objects.using(db).filter(invoice_no=invoice).first()
        invoices = new_journal_entry.objects.using(db).filter(invoice_no=invoice)
      
        if invoice1.vendor_name:
            try:
                phone = vendor_table.objects.using(db).get(name=invoice1.vendor_name).phone
            except vendor_table.DoesNotExist:
                phone = ""
        total = new_journal_entry.objects.using(db).filter(invoice_no=invoice).aggregate(total_amount=Sum("total"))['total_amount']
    form = None
    if request.method == "POST":
        invoice_no = request.POST.get('invoice_no')
        vendor = request.POST.get('vendor_name')
        phone = request.POST.get('phone')
        status = "Edited"
        transfer = transfer_to_bin(request, db, status, invoice_no)
        if transfer:
            form = create_new_journal_enty(request, db) 
        else:
            messages.error(request, "Action Unsuccessful")

    context = {
        "invoice": invoice1,
        "invoices": invoices,
        "total":total,
        'vendor':vendor,
        'phone': phone,
        'accounts':Accounts,
        'acc_types':acc_types,
        "form": form
    }    
    return render(request,"journal/ViewJournalEntryItem.html", context)

def Cancel_journal(request):
    db = request.user.company_id.db_name
    if request.method == "GET":
        invoice_no = request.GET.get('invoice_no')
        status = "Cancelled"
        transfer = transfer_to_bin(request, db, status, invoice_no)
      
        if transfer:
            return JsonResponse(True, safe=False)
        else:
            return JsonResponse(False, safe=False)
    

def GetLoanDetails(request, id):
    db = request.user.company_id.db_name
    try:
       item = loan_account.objects.using(db).get(id=id)
       data = {
            'desc': item.description,
            'debit': item.amount_borrowed,
            'credit': item.amount_paid,
        }
       return JsonResponse(data)
    except loan_account.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required(login_url='/')
@urls_name(name="Loan Manager")
def ViewLoan(request):
    db = request.user.company_id.db_name
    loan = loan_account.objects.usig(db).all()
    context = {"loan":loan}       
    return render(request, "journal/Loan.html", context)

@login_required(login_url='/')
@urls_name(name="Loan Manager")
def CreateLoan(request):
    db = request.user.company_id.db_name
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    employe = employee.objects.using(db).all()
    account = chart_of_account.objects.using(db).all()
    form = None
    if request.method == "POST":
        form = create_new_loan(request, db)  
        
    context = {
        "customer": customer,
        "vendor":vendor,
        "employee":employe,
        "accounts":account,
        "form": form
    }   
    return render(request, "journal/NewLoan.html", context)

def UpdateLoan(request, id):
    db = request.user.company_id.db_name
    loan = loan_account.objects.using(db).get(id=id)
    if request.method == "POST":
        create_new_loan(request)
        # return redirect("journal:Loan")
    
    context = {"laon": loan}
    return render(request, "journal/UpdateLoan.html", context)

def DeleteLoan(request, id):
    db = request.user.company_id.db_name
    loan = loan_account.objects.using(db).get(id=id)
    loan.delete()
    messages.error(request, "Loan was deleted successfully")
    # return redirect("journal:Loan")

@login_required(login_url='/')
@urls_name(name="Receive Payment")
def ReceivePayment(request):
    db = request.user.company_id.db_name
    customers = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).filter(series_name="Assets", account_type="Cash")
    form = None
    if request.method == "POST":
        form = receive_payment(request, db)

    context = {
        'customers':customers,
        'vendor':vendor,
        'accounts':accounts,
        'form': form
    }
   
    return render(request, 'journal/ReceivePayment.html', context)



