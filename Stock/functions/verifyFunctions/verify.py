from datetime import date, datetime

from Stock.models import  CreateStockInLog, CreateStockIn, CreateOutletStockIn, CreateOutletStockInLog;
from django.db.models import Q
from django.http import HttpResponse, JsonResponse,Http404;
from Stock.functions.verifyFunctions.reverse import *


def parse_change_date(value):
    """Parse optional Change Date (YYYY-MM-DD). Empty keeps the original datetx.

    Returns a date, or None if the field was left blank.
    Raises ValueError if a non-empty value is not a valid date.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    return datetime.strptime(text, '%Y-%m-%d').date()


def VerifyStockTransfer(request, context, db):
    itemID     = request.POST.get('itemID')
    outlet     = request.POST.get('outlet')
    warehouse  = request.POST.get('warehouse')
    whichtrans = request.POST.get('whichtrans')
    quantity   = request.POST.get('quantity')
    item_code  = request.POST.get('item_code')
    buttonName = request.POST.get('buttonName')

    # ── DELETE ────────────────────────────────────────────────
    deleteID = request.POST.get('deleteID')
    if 'delete_btn' in request.POST or deleteID:
        if deleteID:
            itemID     = deleteID
            whichtrans = request.POST.get('transtype')

        # Pick the right log table
        if whichtrans in ('W_W', 'O_W'):
            LogModel = CreateStockInLog
        elif whichtrans in ('W_O', 'O_O'):
            LogModel = CreateOutletStockInLog
        else:
            return {'error': 'Unknown transfer type'}

        try:
            log_entry = LogModel.objects.using(db).get(id=itemID)
        except LogModel.DoesNotExist:
            return {'error': 'Transfer record not found'}

        # Reverse the stock movement before deleting
        success, message = reverse_transfer(log_entry, db)
        if not success:
            return {'error': message}

        log_entry.delete()

        if deleteID:
            return {'message': 'Transfer reversed and deleted successfully'}
        context["success_message"] = 'Transfer reversed and deleted successfully'
        return None

    # ── VERIFY ────────────────────────────────────────────────
    if 'Verify' not in request.POST and buttonName != 'verify2':
        return None

    try:
        parsed_date = parse_change_date(request.POST.get('date'))
    except ValueError:
        context["error_message"] = 'Invalid change date'
        return None

    allgood       = False
    updateQTYfrom = None
    updateQTYto   = None

    try:
        if whichtrans == 'W_W':
            updateQTYfrom = CreateStockIn.objects.using(db).get(
                item_code=item_code, warehouse=warehouse
            )
            updateQTYto = CreateStockIn.objects.using(db).get(
                item_code=item_code, warehouse=outlet
            )
            allgood = True

        elif whichtrans == 'W_O':
            updateQTYfrom = CreateStockIn.objects.using(db).get(
                item_code=item_code, warehouse=warehouse
            )
            updateQTYto = CreateOutletStockIn.objects.using(db).get(
                item_code=item_code, outlet=outlet
            )
            allgood = True

        elif whichtrans == 'O_W':
            updateQTYfrom = CreateOutletStockIn.objects.using(db).get(
                item_code=item_code, outlet=warehouse
            )
            updateQTYto = CreateStockIn.objects.using(db).get(
                item_code=item_code, warehouse=outlet
            )
            allgood = True

        elif whichtrans == 'O_O':
            updateQTYfrom = CreateOutletStockIn.objects.using(db).get(
                item_code=item_code, outlet=warehouse
            )
            updateQTYto = CreateOutletStockIn.objects.using(db).get(
                item_code=item_code, outlet=outlet
            )
            allgood = True

    except (CreateStockIn.DoesNotExist, CreateOutletStockIn.DoesNotExist) as e:
        context["error_message"] = f"Stock record not found: {str(e)}"
        return None

    if allgood:
        updateQTYfrom.quantity = float(updateQTYfrom.quantity) - float(quantity)
        updateQTYfrom.save()

        updateQTYto.quantity = float(updateQTYto.quantity) + float(quantity)
        updateQTYto.save()

        if whichtrans in ('W_W', 'O_W'):
            LogModel = CreateStockInLog
        else:
            LogModel = CreateOutletStockInLog

        try:
            updateStatus = LogModel.objects.using(db).get(id=itemID)
            updateStatus.status = 'Verified'
            if parsed_date is not None:
                updateStatus.datetx = parsed_date
            updateStatus.save()
        except LogModel.DoesNotExist:
            context["error_message"] = 'Verification Failed — log not found'
            return None

        if buttonName == 'verify2':
            getUnverified = LogModel.objects.using(db).filter(
                status='Unverified', transfer=whichtrans
            ).values()
            return list(getUnverified)

        context["success_message"] = 'Transfer verified'

    return None

        # *****************************************************************************************************

        