from Stock.models import *
from django.db.models import Q
from django.http import HttpResponse, JsonResponse,Http404;

from decimal import Decimal

def reverse_transfer(log_entry, db):
    """
    Reverses a stock transfer by reading the log entry's transfer type
    and undoing exactly what the original transfer did.
    """
    transfer_type = log_entry.transfer
    item_code     = log_entry.item_code
    quantity      = Decimal(log_entry.quantity)
    warehouse     = log_entry.warehouse
    outlet        = log_entry.outlet

    try:
        if transfer_type == "W_W":
            # Original: deducted from CreateStockIn(warehouse), added to CreateStockIn(outlet)
            # Reverse:  add back to CreateStockIn(warehouse), deduct from CreateStockIn(outlet)

            source = CreateStockIn.objects.using(db).get(
                Q(warehouse=warehouse) & Q(item_code=item_code)
            )
            source.quantity = Decimal(source.quantity) + quantity
            source.save(using=db)

            destination = CreateStockIn.objects.using(db).get(
                Q(warehouse=outlet) & Q(item_code=item_code)
            )
            destination.quantity = Decimal(destination.quantity) - quantity
            destination.save(using=db)

        elif transfer_type == "W_O":
            # Original: deducted from CreateStockIn(warehouse), added to CreateOutletStockIn(outlet)
            # Reverse:  add back to CreateStockIn(warehouse), deduct from CreateOutletStockIn(outlet)

            source = CreateStockIn.objects.using(db).get(
                Q(warehouse=warehouse) & Q(item_code=item_code)
            )
            source.quantity = Decimal(source.quantity) + quantity
            source.save(using=db)

            destination = CreateOutletStockIn.objects.using(db).get(
                Q(outlet=outlet) & Q(item_code=item_code)
            )
            destination.quantity = Decimal(destination.quantity) - quantity
            destination.save(using=db)

        elif transfer_type == "O_W":
            # Original: deducted from CreateOutletStockIn(outlet), added to CreateStockIn(warehouse)
            # Reverse:  add back to CreateOutletStockIn(outlet), deduct from CreateStockIn(warehouse)
            # NOTE: in outlet_Warehouse(), warehouse field = outlet, outlet field = warehouse
            # so log.warehouse = the outlet that sent, log.outlet = the warehouse that received

            source = CreateOutletStockIn.objects.using(db).get(
                Q(outlet=warehouse) & Q(item_code=item_code)   # warehouse col holds the sender outlet
            )
            source.quantity = Decimal(source.quantity) + quantity
            source.save(using=db)

            destination = CreateStockIn.objects.using(db).get(
                Q(warehouse=outlet) & Q(item_code=item_code)   # outlet col holds the receiving warehouse
            )
            destination.quantity = Decimal(destination.quantity) - quantity
            destination.save(using=db)

        elif transfer_type == "O_O":
            # Original: deducted from CreateOutletStockIn(warehouse), added to CreateOutletStockIn(outlet)
            # Reverse:  add back to CreateOutletStockIn(warehouse), deduct from CreateOutletStockIn(outlet)

            source = CreateOutletStockIn.objects.using(db).get(
                Q(outlet=warehouse) & Q(item_code=item_code)
            )
            source.quantity = Decimal(source.quantity) + quantity
            source.save(using=db)

            destination = CreateOutletStockIn.objects.using(db).get(
                Q(outlet=outlet) & Q(item_code=item_code)
            )
            destination.quantity = Decimal(destination.quantity) - quantity
            destination.save(using=db)

        else:
            return False, f"Unknown transfer type: {transfer_type}"

        return True, "Transfer reversed successfully"

    except (CreateStockIn.DoesNotExist, CreateOutletStockIn.DoesNotExist) as e:
        return False, f"Stock record not found during reversal: {str(e)}"
    except Exception as e:
        return False, f"Reversal failed: {str(e)}"


def deleteDate(deletedata, db):
    """Delete a log entry and reverse its stock effect."""

    success, message = reverse_transfer(deletedata, db)
    if not success:
        return JsonResponse({'error': message}, status=400)

    deletedata.delete()
    return JsonResponse({'message': 'Transfer reversed and deleted successfully'})
