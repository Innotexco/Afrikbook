from journal.forms import JournalEntryForm, JournalEntryLogForm
from account.models import account_log, chart_of_account
from account.utils import generate_new_account_id
from vendor.models import vendor_table
from django.contrib import messages
from django.http import HttpResponse
import decimal
from account.acct_functions.account import checkAccountType
from customer.functions.generalFunction import CreateLog, DebitPayable, CreditPayable
from journal.models import new_journal_entry, journal_entry_bin
from django.db.models import Sum


def create_new_journal_enty(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
   
    date = request.POST['date']
    invoice_no = request.POST['invoice_no']
    order_no = request.POST['order_no']
    category = request.POST.get('category')
    account_id = request.POST.get('credit-account')
    vendor = request.POST['vendor_name']
    phone = request.POST.get('phone')
    narration = request.POST['narration']
    
    
    item = request.POST.getlist('item[]')
    descriptions = request.POST.getlist('desc[]')
    credit = request.POST.getlist('cr[]')
    amount = request.POST.getlist('dbt[]')
    # total = request.POST['total']
    # total_credit = request.POST['total-c']
    total_debit = request.POST['total-d']
    amount_paid = request.POST['amount_paid']

    transaction_type = "Debit"
    transaction_source = None
    
    if account_id != None : 
        # Account = checkAccountType(request, category)
        account = chart_of_account.objects.using(db).get(account_id=account_id)
        vendor_name = vendor + "("+ account.series_name + ")"
    
        if account.series_name == "Expenses":
            transaction_source = vendor
        elif account.series_name == "Income":
            transaction_source = "Sales"
        elif account.series_name == "Liability":
            transaction_source = vendor
        elif account.series_name == "Assets":
            transaction_source = "Purchase"
    
        for i in range(len(item)):

            # Check if the itemcode (value) is equal to 1
            if str(item[i]) != "":
            
            
                form_data = {
                    'date': date,
                    'invoice_no':invoice_no,
                    'order_no':order_no,
                    'account':account.account_id,
                    'vendor_name':vendor,
                    'category':category,
                    'narration':narration,
                    'item': item[i],
                    'description':descriptions[i],
                    'debit': amount_paid,
                    'credit': total_debit,
                    'total': amount[i],
                    'transaction_type':transaction_type
                }
                # form_data = {
                #     'date': date,
                #     'invoice_no':invoice_no,
                #     'order_no':order_no,
                #     'account':"6",
                #     'vendor_name':vendor_name,
                #     'category':category,
                #     'narration':narration,
                #     'item': item[i],
                #     'description':descriptions[i],
                #     'debit': debit[i],
                #     'credit': credit[i],
                #     'total': total,
                #     'total_debit': total_debit,
                #     'total_credit': total_credit,
                #     'transaction_type':transaction_type
                # }
                
                form = JournalEntryForm(form_data)
                journal_log_form = JournalEntryLogForm(form_data)
                if category != None:
                   
                    if form.is_valid():
                        form_i = form.save(commit=False)
                        form_i.Userlogin = request.user.username
                        form_i.save(using=db)

                        # Display the success message only once
                        if not message_displayed:

                            if vendor:
                                try:
                                    ven = vendor_table.objects.using(db).get(name=vendor, phone=phone)
                                except vendor_table.DoesNotExist:
                                    ven = vendor_table.objects.using(db).create(name=vendor, phone=phone, Userlogin=request.user.username)
                                    start =account.account_id[0]
                                    id = generate_new_account_id()
                                    new_id = start+id+"-"+vendor
                                    
                                    account = chart_of_account.objects.using(db).create(
                                        account_id = new_id,
                                        series_name = account.series_name,
                                        account_type = account.account_type,
                                        account_bankname = vendor,
                                        status = "Active",
                                        actual_balance = total_debit,
                                        Userlogin = request.user.username
                                    )
                                
                                DebitPayable(request, db, ven, date, narration, "Transfer", account.account_id, amount_paid)
                                CreditPayable(request, db, ven, date, narration, "Transfer", account.account_id,  total_debit)
                            CreateLog(db, account, amount_paid)

                      
                            messages.success(request, "New Journal Entry was created successfully")
                            message_displayed = True  # Update the message_displayed variable
                    else:
                
                        return form
                else:
                    if not message_displayed:
                        messages.error(request, "Select Operating expenses")
                        message_displayed = True
            else:
                if not message_displayed:
                    messages.error(request, "Add at least one item")
                    message_displayed = True
    else:
        messages.error(request, "Select valid Account")



def transfer_to_bin(request, db, status, invoice_no):
    

    journal = new_journal_entry.objects.using(db).filter(invoice_no=invoice_no)
    oldj = len(journal)
    total = journal.aggregate(total_amount=Sum("total"))['total_amount']

    for i in journal:
        # break
        journal_entry_bin.objects.using(db).create(
            date              = i.date,
            invoice_no        = i.invoice_no,
            order_no          = i.order_no,
            account           = i.account,
            vendor_name       = i.vendor_name,
            category          = i.category,
            narration         = i.narration,
            item              = i.item,
            description       = i.description,
            debit             = i.debit,
            credit            = i.credit,
            total             = i.total,
            transaction_type  = i.transaction_type,
            status            = status,
            Userlogin         = i.Userlogin
        )
        
    editj = journal_entry_bin.objects.using(db).filter(invoice_no=invoice_no)

    if editj.count() == oldj:
        account = chart_of_account.objects.using(db).get(account_id=journal.first().account)
        j = journal.first()

        if j.vendor_name:
            ven = vendor_table.objects.using(db).get(name=j.vendor_name)
            DebitPayable(request, db, ven, j.date, j.narration, account.account_type, "Transfer", account.account_id, j.debit)

        journal.delete()

        
        CreateLog(db, account, -abs(decimal.Decimal(j.debit)))

        return True
    else:
        return False
