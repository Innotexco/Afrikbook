from Stock.models import  CreateStockInLog, CreateStockIn, CreateOutletStockIn, CreateOutletStockInLog;
from django.db.models import Q
from django.http import HttpResponse, JsonResponse,Http404;
from Stock.functions. functionHub.functionHub import *
from datetime import date
from decimal import Decimal, InvalidOperation


def to_decimal(value, default="0.00"):
    """Coerce POST values to Decimal; empty/invalid strings become default (not '')."""
    if value is None:
        return Decimal(default)
    cleaned = str(value).replace(",", "").replace(" ", "").strip()
    if cleaned == "" or cleaned.lower() in ("none", "null", "nan"):
        return Decimal(default)
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def list_val(seq, index, default=""):
    """Safe list index for parallel POST getlist arrays."""
    try:
        return seq[index]
    except (IndexError, TypeError):
        return default


def resolve_selling_price(db, item_code, posted_price):
    """
    Prefer posted price; if blank, fall back to Item.selling_price, else 0.
    Never return empty string (breaks DecimalField).
    """
    if posted_price not in (None, ""):
        cleaned = str(posted_price).replace(",", "").replace(" ", "").strip()
        if cleaned and cleaned.lower() not in ("none", "null", "nan"):
            try:
                return Decimal(cleaned)
            except (InvalidOperation, ValueError, TypeError):
                pass
    try:
        from Stock.models import Item
        item = Item.objects.using(db).filter(generated_code=item_code).first()
        if item and item.selling_price is not None and str(item.selling_price).strip() != "":
            return to_decimal(item.selling_price)
    except Exception:
        pass
    return Decimal("0.00")


def Warehouse_warehouse(request, context, db):
    warehouse         = request.POST.get('warehouse')
    outlet            = request.POST.get('outlet')
    item_code         = request.POST.getlist('item_code[]')
    item_decription   = request.POST.getlist('item_decription[]')
    quantity          = request.POST.getlist('quantity[]')
    selling_price     = request.POST.getlist('selling_price[]')
    item              = request.POST.getlist('item[]')
    itemlen           = len(item_code)
    # itemlen             = len(item_code)
    description       = request.POST.get('description')
    token_id          = request.POST.get('token_id')
    Userlogin         = request.POST.get('Userlogin')
    supplier          = request.POST.get('supplier')
    source            = request.POST.get('source')
    ref_no            = request.POST.get('ref_no')
    INT = request.session.get('INT', 'Yes')

    datetx = request.POST.get('datetx')  
    if not datetx:
        datetx = date.today()  
    
    if warehouse == outlet:
        message = 'You cannot select the same Warehouse'
        return JsonResponse({'message': message})
        


    allgood = False
    iftrue = False
    i=0
    if warehouse != outlet:
        while i < itemlen:
            if item_code[i] != '_ _Choose an Option_ _':

                try:
                    checkexist = CreateStockIn.objects.using(db).get(Q(warehouse=warehouse), Q(item_code=item_code[i]))
                    # this will be a function under function Hub ctrl left click to view*********************
                    iftrue = DoSomething(checkexist, quantity, item, i, context, INT, db)
                

                except CreateStockIn.DoesNotExist:
                    iftrue = DoSomethingElse(context, item, i, warehouse)
        
                if iftrue:
                    qty_dec = to_decimal(list_val(quantity, i, 0))
                    price_dec = resolve_selling_price(db, item_code[i], list_val(selling_price, i, ""))
                    desc_i = list_val(item_decription, i, "")
                    name_i = list_val(item, i, "")
                    try:
                        updateQTYto = CreateStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(warehouse=outlet))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2 or 0) + float(qty_dec)
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()

                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, source= source, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_dec, transfer="W_W", datetx=datetx)
                        if savedata:
                            allgood = True
                    except CreateStockIn.DoesNotExist:
                        QTY = qty_dec if INT == 'Yes' else Decimal('0.00')
                        
                        CreateStockIn.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description, warehouse= outlet, item_decription=desc_i, item=name_i, quantity = QTY, item_code= item_code[i], main=False)

                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, source= source, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_dec, transfer="W_W", datetx=datetx)

                        if savedata:
                            allgood = True
            i = i+1
        itemlen -= 1
        
        try:
            itemlen == 0
            if allgood:
                if INT == 'Yes':
                    getD =  CreateStockInLog.objects.using(db).filter(token_id=token_id)
                    for i in getD:
                        i.status = 'Verified'
                        i.save()
                context["success_message"] =  'Item Successfully Transfered'
        except:
            context["error_message"] =  'Item Transfer failed'
    else:
        context["error_message"] = 'You cannot select the same Warehouse'




def Warehouse_outlet(request, context, db):
    warehouse         = request.POST.get('warehouse')
    outlet            = request.POST.get('outlet')
    item_code         = request.POST.getlist('item_code[]')
    item_decription   = request.POST.getlist('item_decription[]')
    quantity          = request.POST.getlist('quantity[]')
    selling_price     = request.POST.getlist('selling_price[]')
    wholesale_price     = request.POST.getlist('wholesale_price[]')
    item              = request.POST.getlist('item[]')
    itemlen           = len(item_code)
    description       = request.POST.get('description')
    token_id          = request.POST.get('token_id')
    Userlogin         = request.POST.get('Userlogin')
    supplier          = request.POST.get('supplier')
    ref_no            = request.POST.get('ref_no')
    INT = request.session.get('INT', 'Yes')
    datetx = request.POST.get('datetx')   
    if not datetx:
        datetx = date.today()
    today = date.today()
    allgood = False
    iftrue = False
    i=0
    if warehouse != outlet:
        while i < itemlen:
            if item_code[i] != '_ _Choose an Option_ _':
                
                try:
                    checkexist = CreateStockIn.objects.using(db).get(Q(warehouse=warehouse), Q(item_code=item_code[i]))
                    iftrue = DoSomething(checkexist, quantity, item, i, context, INT, db)

                except CreateStockIn.DoesNotExist:
                    iftrue = DoSomethingElse(context, item, i, warehouse)

                if iftrue:
                    qty_dec = to_decimal(list_val(quantity, i, 0))
                    price_dec = resolve_selling_price(db, item_code[i], list_val(selling_price, i, ""))
                    wholesale_dec = to_decimal(list_val(wholesale_price, i, 0))
                    desc_i = list_val(item_decription, i, "")
                    name_i = list_val(item, i, "")
                    try:
                        updateQTYto = CreateOutletStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(outlet=outlet))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2 or 0) + float(qty_dec)
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()
                        savedata = CreateOutletStockInLog.objects.using(db).create(datetx= datetx, token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_dec, wholesale_price=wholesale_dec, transfer="W_O")
                        if savedata:
                            allgood = True
                    except CreateOutletStockIn.DoesNotExist:
                        QTY = qty_dec if INT == 'Yes' else Decimal('0.00')
                        CreateOutletStockIn.objects.using(db).create(datetx= datetx, token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description,  outlet=outlet, item_decription=desc_i, item=name_i, selling_price=price_dec, wholesale_price=wholesale_dec, quantity= QTY, item_code= item_code[i], main=False)
                        savedata = CreateOutletStockInLog.objects.using(db).create(datetx= datetx, token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_dec, wholesale_price=wholesale_dec, transfer="W_O")
                        if savedata:
                            allgood = True
            i = i+1
        itemlen -= 1
        try:
            itemlen == 0
            if allgood:
                if INT == 'Yes':
                    getD =  CreateOutletStockInLog.objects.using(db).filter(token_id=token_id)
                    for i in getD:
                        i.status = 'Verified'
                        i.save()
                context["success_message"] =  'Item Successfully Transfered' 
        except:
            context["error_message"] =  'Item Transfer failed'
    else:
        context["error_message"] = 'You cannot select the same Warehouse'




def outlet_Warehouse(request, context, db):
    warehouse         = request.POST.get('warehouse')
    outlet            = request.POST.get('outlet')
    item_code         = request.POST.getlist('item_code[]')
    item_decription   = request.POST.getlist('item_decription[]')
    quantity          = request.POST.getlist('quantity[]')
    selling_price     = request.POST.getlist('selling_price[]')
    item              = request.POST.getlist('item[]')
    itemlen           = len(item_code)
    # itemlen             = len(item_code)
    description       = request.POST.get('description')
    token_id          = request.POST.get('token_id')
    Userlogin         = request.POST.get('Userlogin')
    supplier          = request.POST.get('supplier')
    ref_no            = request.POST.get('ref_no')
    INT = request.session.get('INT', 'Yes')
    
    datetx = request.POST.get('datetx')
    if not datetx:
        datetx = date.today()

    allgood = False
    iftrue = False
    i=0
    if warehouse != outlet:
        while i < itemlen:
            # for item in item_code:
            if item_code[i] != '_ _Choose an Option_ _':
                try:
                    checkexist = CreateOutletStockIn.objects.using(db).get(Q(outlet=outlet), Q(item_code=item_code[i]))
                    iftrue = DoSomething(checkexist, quantity, item, i, context, INT, db)
                except CreateOutletStockIn.DoesNotExist:
                    iftrue = DoSomethingElse(context, item, i, outlet)

                if iftrue:
                    qty_dec = to_decimal(list_val(quantity, i, 0))
                    price_dec = resolve_selling_price(db, item_code[i], list_val(selling_price, i, ""))
                    desc_i = list_val(item_decription, i, "")
                    name_i = list_val(item, i, "")
                    try:
                        updateQTYto = CreateStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(warehouse=warehouse))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2 or 0) + float(qty_dec)
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()
                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= outlet, outlet=warehouse, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_dec, transfer="O_W", datetx=datetx)
                        if savedata:
                            allgood = True

                    except CreateStockIn.DoesNotExist:
                        QTY = qty_dec if INT == 'Yes' else Decimal('0.00')
                        CreateStockIn.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description, warehouse= warehouse,  item_decription=desc_i, item=name_i, quantity= QTY, item_code= item_code[i], main=False)
                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= outlet, outlet=warehouse, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_dec, transfer="O_W", datetx=datetx)
                        if savedata:
                            allgood = True
            i = i+1
        itemlen -= 1
        try:
            itemlen == 0
            if allgood:
                if INT == 'Yes':
                    getD =  CreateStockInLog.objects.using(db).filter(token_id=token_id)
                    for i in getD:
                        i.status = 'Verified'
                        i.save()
                context["success_message"] =  'Item Successfully Transfered'
        except:
            context["error_message"] =  'Item Transfer failed'
    else:
        context["error_message"] = 'You cannot select the same Warehouse'




def outlet_outlet(request, context, db):
    warehouse         = request.POST.get('warehouse')
    outlet            = request.POST.get('outlet')
    item_code         = request.POST.getlist('item_code[]')
    item_decription   = request.POST.getlist('item_decription[]')
    quantity          = request.POST.getlist('quantity[]')
    selling_price     = request.POST.getlist('selling_price[]')
    item              = request.POST.getlist('item[]')
    itemlen           = len(item_code)
    # itemlen             = len(item_code)
    description       = request.POST.get('description')
    token_id          = request.POST.get('token_id')
    Userlogin         = request.POST.get('Userlogin')
    supplier          = request.POST.get('supplier')
    ref_no            = request.POST.get('ref_no')
    INT = request.session.get('INT', 'Yes')
    
    datetx = request.POST.get('datetx')
    if not datetx:
        datetx = date.today()

    allgood = False
    iftrue = False
    i=0
    if warehouse != outlet:
        while i < itemlen:
            # for item in item_code:
            if item_code[i] != '_ _Choose an Option_ _':
                try:
                    checkexist = CreateOutletStockIn.objects.using(db).get(Q(outlet=warehouse), Q(item_code=item_code[i]))
                    iftrue = DoSomething(checkexist, quantity, item, i, context, INT, db)
                except CreateOutletStockIn.DoesNotExist:
                    iftrue = DoSomethingElse(context, item, i, warehouse)
                if iftrue:
                    qty_dec = to_decimal(list_val(quantity, i, 0))
                    price_dec = resolve_selling_price(db, item_code[i], list_val(selling_price, i, ""))
                    desc_i = list_val(item_decription, i, "")
                    name_i = list_val(item, i, "")
                    # CreateOutletStockInLog.selling_price is CharField — store as string
                    price_str = str(price_dec)
                    try:
                        updateQTYto = CreateOutletStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(outlet=outlet))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2 or 0) + float(qty_dec)
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()
                        savedata = CreateOutletStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_str, transfer="O_O", datetx=datetx)
                        if savedata:
                            allgood = True
                    except CreateOutletStockIn.DoesNotExist:
                        QTY = qty_dec if INT == 'Yes' else Decimal('0.00')
                        CreateOutletStockIn.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description, outlet= outlet, item_decription=desc_i, selling_price=price_str, item=name_i, quantity= QTY, item_code= item_code[i], main=False)
                        savedata = CreateOutletStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier,  ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=desc_i, item=name_i, quantity=qty_dec, item_code= item_code[i], selling_price=price_str, transfer="O_O", datetx=datetx)
                        if savedata:
                            allgood = True

            i = i+1
        itemlen -= 1
        try:
            itemlen == 0
            if allgood:
                if INT == 'Yes':
                    getD =  CreateOutletStockInLog.objects.using(db).filter(token_id=token_id)
                    for i in getD:
                        i.status = 'Verified'
                        i.save()
                context["success_message"] =  'Item Successfully Transfered'
        except:
            context["error_message"] =  'Item Transfer failed'
    else:
        context["error_message"] = 'You cannot select the same outlet'





# def DoSomething(checkexist, quantity, item, i, context, INT, db):
#     oldQty = checkexist.quantity
   
#     if oldQty < int(quantity[i]):
#         context["error_message"] = f"We only have {oldQty} {item[i]} left"
        
#     # ELSE USE A JS ALERT TO TRANSFER ANYWAY
#     else:
#       if INT == 'Yes':
#          newQty = float(oldQty) - float(quantity[i])
#          checkexist.quantity = newQty
#          checkexist.save(using=db)
#       return True

from decimal import Decimal

def DoSomething(checkexist, quantity, item, i, context, INT, db):

    # if not quantity[i] or str(quantity[i]).strip() == "":
    #     context["error_message"] = f"Quantity missing for {item[i]}"
    #     return False

    try:
        req_qty = Decimal(quantity[i])
    except:
        context["error_message"] = f"Invalid quantity for {item[i]}"
        return False

    oldQty = Decimal(checkexist.quantity)

    if oldQty < req_qty:
        context["error_message"] = f"We only have {oldQty} {item[i]} left"
        return False

    if INT == 'Yes':
        checkexist.quantity = oldQty - req_qty
        checkexist.save(using=db)

    return True

def DoSomethingElse(context,item, i, store):
    context["error_message"] =  item[i] +' Item not found in '+ store 
    return False