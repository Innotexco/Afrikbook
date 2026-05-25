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
from customer.models import customer_table
from vendor.models import vendor_table


def create_new_journal_enty(request, db):
    message_displayed = False

    date         = request.POST['date']
    invoice_no   = request.POST['invoice_no']
    order_no     = request.POST.get('order_no', '')
    category     = request.POST.get('category')
    account_id   = request.POST.get('credit-account')
    vendor_name  = request.POST.get('vendor_name', '').strip()
    phone        = request.POST.get('phone', '').strip()
    party_type   = request.POST.get('party_type', 'vendor')  # 'vendor' or 'customer'
    narration    = request.POST['narration']

    item         = request.POST.getlist('item[]')
    descriptions = request.POST.getlist('desc[]')
    amount       = request.POST.getlist('dbt[]')
    total_debit  = request.POST['total-d']
    amount_paid  = request.POST['amount_paid']

    transaction_type = "Debit"

    if account_id:
        account = chart_of_account.objects.using(db).get(account_id=account_id)

        if account.series_name == "Expenses":
            transaction_source = vendor_name
        elif account.series_name == "Income":
            transaction_source = "Sales"
        else:
            transaction_source = vendor_name

        for i in range(len(item)):
            if str(item[i]).strip() == "":
                if not message_displayed:
                    messages.error(request, "Add at least one item")
                    message_displayed = True
                continue

            if category is None:
                if not message_displayed:
                    messages.error(request, "Select Operating expenses")
                    message_displayed = True
                continue

            form_data = {
                'date':             date,
                'invoice_no':       invoice_no,
                'order_no':         order_no,
                'account':          account.account_id,
                'vendor_name':      vendor_name,
                'category':         category,
                'narration':        narration,
                'item':             item[i],
                'description':      descriptions[i],
                'debit':            amount_paid,
                'credit':           total_debit,
                'total':            amount[i],
                'transaction_type': transaction_type,
            }

            form = JournalEntryForm(form_data)
            if form.is_valid():
                form_i = form.save(commit=False)
                form_i.Userlogin = request.user.username
                form_i.save(using=db)

                if not message_displayed:
                    if vendor_name:
                        
                        #Resolve or create vendor
                        import uuid
                        dummy_email = f"{uuid.uuid4().hex[:8]}@noemail.local"

                        try:
                            ven = vendor_table.objects.using(db).get(name__iexact=vendor_name)
                        except vendor_table.DoesNotExist:
                            # Try customer table first
                            try:
                                cus = customer_table.objects.using(db).get(name__iexact=vendor_name)
                                
                                ven = vendor_table.objects.using(db).create(
                                    name      = cus.name,
                                    phone     = cus.phone or phone or '0000000000',
                                    email     = dummy_email,
                                    address   = 'N/A',  
                                    Userlogin = request.user.username,
                                )
                            except customer_table.DoesNotExist:

                                ven = vendor_table.objects.using(db).create(
                                    name      = vendor_name,
                                    phone     = phone or '0000000000',
                                    email     = dummy_email,
                                    address   = 'N/A',
                                    Userlogin = request.user.username,
                                )

                        DebitPayable(request, db, ven, date, narration, "Transfer", account.account_id, amount_paid)
                        CreditPayable(request, db, ven, date, narration, "Transfer", account.account_id, total_debit)

                    CreateLog(db, account, amount_paid)
                    messages.success(request, "New Journal Entry was created successfully")
                    message_displayed = True
            else:
                return form
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
