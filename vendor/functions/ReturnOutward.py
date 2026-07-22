from vendor.models import *
from vendor.forms import VendorReturnForm
from django.contrib import messages
from django.db.models import Q
from customer.functions.generalFunction import *
from customer.functions.newsalesfunc import *
from account.models import *
from Stock.models import CreateStockIn
import decimal


def _safe_reduce_warehouse_stock(db, warehouse, itemcode, qty):
    """Reduce warehouse stock for a returned line; no-op if row missing."""
    try:
        ReduceStockinItemQuantity(db, warehouse, itemcode, qty)
    except Exception:
        # Fall back: try update if helper fails on missing stock
        stock = CreateStockIn.objects.using(db).filter(
            Q(warehouse=warehouse) | Q(outlet=warehouse),
            item_code=itemcode,
        ).first()
        if stock is None:
            return
        stock.quantity = decimal.Decimal(stock.quantity or 0) - decimal.Decimal(str(qty))
        stock.save(using=db)


def add_return_item(request, db):
    """
    Process a return outward (goods returned to supplier).
    Saves Vendor_Return lines, reduces warehouse stock once, updates
    invoice line cancellation, GL, and VAT reverse.
    """
    refund_date = request.POST.get('refund_date')
    invoiceID = (request.POST.get('invoiceID') or '').strip()
    reference_ID = (request.POST.get('reference_ID') or request.POST.get('itemcode') or '').strip()
    Gdescription = request.POST.get('Gdescription', '')
    warehouse = request.POST.get('warehouse', '')
    genby = request.POST.get('genby', '')  # vendor custID from select
    account = request.POST.get('account') or request.POST.get('return_account')
    item_name = request.POST.getlist('item_name')
    itemcode = request.POST.getlist('item[]')
    item_description = request.POST.getlist('desc[]')
    quantities = request.POST.getlist('qty[]')
    unit = request.POST.getlist('unit[]')
    discount = request.POST.getlist('discount[]')
    amount = request.POST.getlist('amount[]')
    total = request.POST.get('total') or '0'
    vat = request.POST.get('vat') or '0'
    initial_total = request.POST.get('initial_total') or total
    p_method = request.POST.get('p_method', 'Cash')

    if not invoiceID:
        messages.error(request, "Invoice number is required")
        return None

    if not genby:
        messages.error(request, "Vendor is required")
        return None

    try:
        vendor = vendor_table.objects.using(db).get(custID=genby)
    except vendor_table.DoesNotExist:
        messages.error(request, "Vendor not found")
        return None

    customer_id = vendor.custID
    customer_name = vendor.name

    invoice2 = Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).first()
    if invoice2 is None:
        messages.error(request, "Invoice ID not found")
        return None

    # Resolve return account (template may still send legacy name="amount")
    if not account:
        account = request.POST.get('amount')  # legacy select name
        # Avoid using a line amount if it was confused with account
        if account and not str(account).startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
            account = None

    try:
        if account:
            debtor_account = chart_of_account.objects.using(db).get(account_id=account)
        else:
            debtor_account = chart_of_account.objects.using(db).get(account_id='1001-ReturnOutward')
    except chart_of_account.MultipleObjectsReturned:
        debtor_account = chart_of_account.objects.using(db).filter(
            account_id='1001-ReturnOutward'
        ).first()
    except chart_of_account.DoesNotExist:
        try:
            debtor_account = chart_of_account.objects.using(db).get(account_id='1001-ReturnOutward')
        except chart_of_account.DoesNotExist:
            messages.error(request, "Return Outward account not found")
            return None

    saved_lines = 0
    returned_itemcodes = []

    for i in range(len(itemcode)):
        if str(itemcode[i]) == "0" or not itemcode[i]:
            continue

        qty = quantities[i] if i < len(quantities) and quantities[i] else '1'
        try:
            if int(float(qty)) == 0:
                qty = '1'
        except (TypeError, ValueError):
            qty = '1'

        name_i = item_name[i] if i < len(item_name) else ''
        desc_i = item_description[i] if i < len(item_description) else ''
        unit_i = unit[i] if i < len(unit) else '0'
        disc_i = discount[i] if i < len(discount) else '0'
        amt_i = amount[i] if i < len(amount) else '0'

        form_data = {
            'genby': customer_name,
            'cusID': customer_id,
            'invoiceID': invoiceID,
            'reference_ID': reference_ID or invoiceID,
            'Gdescription': Gdescription,
            'item_name': name_i,
            'itemcode': itemcode[i],
            'item_description': desc_i,
            'qty': qty,
            'unit_p': unit_i,
            'discount': disc_i,
            'amount': amt_i,
            'amount_paid': total,
            'amount_expected': initial_total,
        }

        form = VendorReturnForm(form_data)
        if not form.is_valid():
            messages.error(request, f"Invalid data on item {i + 1}: {form.errors}")
            continue

        form_i = form.save(commit=False)
        form_i.Userlogin = request.user.username
        form_i.genby = customer_name
        form_i.cusID = customer_id
        form_i.amount_paid = decimal.Decimal(str(total or 0))
        form_i.amount_expected = decimal.Decimal(str(initial_total or total or 0))
        form_i.save(using=db)

        # Apply user-selected refund date (model uses auto_now_add)
        if refund_date:
            Vendor_Return.objects.using(db).filter(pk=form_i.pk).update(refund_date=refund_date)

        # Goods leave stock once — from selected warehouse (purchase returns)
        if warehouse:
            _safe_reduce_warehouse_stock(db, warehouse, itemcode[i], qty)

        # Mark only this invoice line as cancelled/returned (partial-safe)
        Vendor_invoice.objects.using(db).filter(
            invoiceID=invoiceID,
            itemcode=itemcode[i],
        ).update(cancellation=1)

        returned_itemcodes.append(itemcode[i])
        saved_lines += 1

    if saved_lines == 0:
        messages.error(request, "Select at least one item to return")
        return None

    # If every line on the invoice is cancelled, rename invoice ID for history
    open_lines = Vendor_invoice.objects.using(db).filter(
        invoiceID=invoiceID, cancellation=0
    ).exists()
    if not open_lines:
        Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).update(
            invoiceID=invoiceID + "_returned",
            cancellation=1,
        )

    # Vendor refund counter
    try:
        ven = vendor_table.objects.using(db).get(custID=customer_id)
        ven.refundInvoice = (ven.refundInvoice or 0) + 1
        ven.save(using=db)
    except vendor_table.DoesNotExist:
        pass

    # GL posting
    try:
        total_dec = decimal.Decimal(str(total or 0))
    except (decimal.InvalidOperation, TypeError, ValueError):
        total_dec = decimal.Decimal('0')

    if total_dec and debtor_account:
        debtor_account.actual_balance = (
            decimal.Decimal(str(debtor_account.actual_balance or 0)) + total_dec
        )
        debtor_account.save(using=db)

        try:
            CreateLog(db, debtor_account, total_dec)
        except Exception:
            pass

        if invoice2.amount_paid is not None and invoice2.amount_expected is not None:
            if invoice2.amount_paid < invoice2.amount_expected:
                # Unpaid / partially paid purchase — expense/return account only
                acc_log = account_log(
                    transaction_source="Return outward",
                    amount=total_dec,
                    date=refund_date,
                    account=debtor_account.account_id,
                    account_type=debtor_account.account_type,
                    Userlogin=request.user.username,
                )
                acc_log.save(using=db)
            else:
                # Fully paid — credit payable / refund path
                try:
                    CreditPayable(
                        request, db, vendor, refund_date, Gdescription,
                        p_method, debtor_account.account_id, initial_total or total,
                    )
                except Exception:
                    pass
                acc_log = account_log(
                    transaction_source="Return outward",
                    amount=total_dec,
                    date=refund_date,
                    account=debtor_account.account_id,
                    account_type=debtor_account.account_type,
                    Userlogin=request.user.username,
                )
                acc_log.save(using=db)
        else:
            acc_log = account_log(
                transaction_source="Return outward",
                amount=total_dec,
                date=refund_date,
                account=debtor_account.account_id,
                account_type=debtor_account.account_type,
                Userlogin=request.user.username,
            )
            acc_log.save(using=db)

    # Reverse VAT against original invoice source (not renamed id)
    if vat and str(vat).strip() not in ('', '0', '0.0', '0.00'):
        try:
            create_minus_vat(db, invoiceID, vat)
        except Exception:
            pass

    messages.success(request, "Outward return completed successfully")
    return None
