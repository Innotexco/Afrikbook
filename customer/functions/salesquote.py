from customer.forms import SalesQuoteForm
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
import uuid
from datetime import datetime
from customer.models import sales_quote



def add_sales_quote(request, db):
    message_displayed = False
    
    quote_dates  = request.POST.get('quote_date', '')
    referenceID  = request.POST.get('referenceID', '').strip()
    Gdescription = request.POST.get('Gdescription', '')
    genby        = request.POST.get('genby', '')
    cusID        = request.POST.get('cusID', '')
    item_names        = request.POST.getlist('item_name')
    itemcodes         = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities        = request.POST.getlist('qty[]')
    units             = request.POST.getlist('unit[]')
    discounts         = request.POST.getlist('discount[]')
    amounts           = request.POST.getlist('amount[]')
    total             = request.POST.get('total', '0')

    # ── Auto‑generate unique referenceID if blank
    if not referenceID:
        # date_part = datetime.now().strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:6].upper()
        referenceID = f"Quote-{random_part}"

        while sales_quote.objects.using(db).filter(referenceID=referenceID).exists():
            random_part = uuid.uuid4().hex[:6].upper()
            referenceID = f"Quote-{random_part}"
    else:
        if sales_quote.objects.using(db).filter(referenceID=referenceID).exists():
            messages.error(request, "Reference ID already exists. Please use a different one.")
            return redirect('customer:salesquote')  # or return redirect('...')

    # ── Process each item row 
    for i in range(len(itemcodes)):
        if str(itemcodes[i]) != "0":
            qty = quantities[i] if quantities[i] else '1'
            if int(float(qty)) == 0:
                qty = '1'

            form_data = {
                'genby':            genby,
                'quote_date':       quote_dates,
                'referenceID':      referenceID,
                'Gdescription':     Gdescription,
                'item_name':        item_names[i] if i < len(item_names) else '',
                'itemcode':         itemcodes[i],
                'item_description': item_descriptions[i] if i < len(item_descriptions) else '',
                'qty':              qty,
                'unit_p':           units[i] if i < len(units) else '0',
                'discount':         discounts[i] if i < len(discounts) else '0',
                'amount':           amounts[i] if i < len(amounts) else '0',
                'total':            total,
                'custID':           cusID,
            }

            form = SalesQuoteForm(form_data)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.Userlogin = request.user.username
                instance.save(using=db)

                if not message_displayed:
                    messages.success(request, "Sales Quote was added successfully")
                    message_displayed = True
            else:
                return form
            
    if len(itemcodes) == 1 and itemcodes[0] == "0":
        messages.error(request, "Select at least one item")

    return None