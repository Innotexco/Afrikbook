from Stock.models import  CreateStockInLog, CreateStockIn, CreateOutletStockIn, CreateOutletStockInLog;
from django.db.models import Q
from django.http import HttpResponse, JsonResponse,Http404;
from Stock.functions. functionHub.functionHub import *
from datetime import date


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
                    try:
                        updateQTYto = CreateStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(warehouse=outlet))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2) + float(quantity[i])
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()

                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, source= source, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], transfer="W_W")
                        if savedata:
                            allgood = True
                    except CreateStockIn.DoesNotExist:
                        QTY = quantity[i] if INT == 'Yes' else 0.00
                        
                        CreateStockIn.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description, warehouse= outlet, item_decription=item_decription[i], item=item[i], quantity = QTY, item_code= item_code[i], main=False)

                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, source= source, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], transfer="W_W")

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
                    try:
                        updateQTYto = CreateOutletStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(outlet=outlet))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2) + float(quantity[i])
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()
                        savedata = CreateOutletStockInLog.objects.using(db).create(datetx= today,token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], wholesale_price=wholesale_price[i], transfer="W_O")
                        if savedata:
                            allgood = True
                    except CreateOutletStockIn.DoesNotExist:
                        QTY = quantity[i] if INT == 'Yes' else 0.00
                        CreateOutletStockIn.objects.using(db).create(datetx= today, token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description,  outlet=outlet, item_decription=item_decription[i], item=item[i], selling_price=selling_price[i], wholesale_price=wholesale_price[i], quantity= QTY, item_code= item_code[i], main=False)
                        savedata = CreateOutletStockInLog.objects.using(db).create(datetx= today, token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], wholesale_price=wholesale_price[i], transfer="W_O")
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
    itemlen             = len(item_code)
    description       = request.POST.get('description')
    token_id          = request.POST.get('token_id')
    Userlogin         = request.POST.get('Userlogin')
    supplier          = request.POST.get('supplier')
    ref_no            = request.POST.get('ref_no')
    INT = request.session.get('INT', 'Yes')

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
                    try:
                        updateQTYto = CreateStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(warehouse=warehouse))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2) + float(quantity[i])
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()
                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= outlet, outlet=warehouse, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], transfer="O_W")
                        if savedata:
                            allgood = True

                    except CreateStockIn.DoesNotExist:
                        QTY = quantity[i] if INT == 'Yes' else 0.00
                        CreateStockIn.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description, warehouse= warehouse,  item_decription=item_decription[i], item=item[i], quantity= QTY, item_code= item_code[i], main=False)
                        savedata = CreateStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= outlet, outlet=warehouse, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], transfer="O_W")
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
    itemlen             = len(item_code)
    description       = request.POST.get('description')
    token_id          = request.POST.get('token_id')
    Userlogin         = request.POST.get('Userlogin')
    supplier          = request.POST.get('supplier')
    ref_no            = request.POST.get('ref_no')
    INT = request.session.get('INT', 'Yes')

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
                    try:
                        updateQTYto = CreateOutletStockIn.objects.using(db).get(Q(item_code= item_code[i]), Q(outlet=outlet))
                        if INT == 'Yes':
                            oldQty2 = updateQTYto.quantity
                            newQty2 = float(oldQty2) + float(quantity[i])
                            updateQTYto.quantity = newQty2
                            updateQTYto.save()
                        savedata = CreateOutletStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], transfer="O_O")
                        if savedata:
                            allgood = True
                    except CreateOutletStockIn.DoesNotExist:
                        QTY = quantity[i] if INT == 'Yes' else 0.00
                        CreateOutletStockIn.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier, description=description, outlet= outlet, item_decription=item_decription[i], selling_price=selling_price[i], item=item[i], quantity= QTY, item_code= item_code[i], main=False)
                        savedata = CreateOutletStockInLog.objects.using(db).create(token_id=token_id, Userlogin=Userlogin, supplier=supplier,  ref_no=ref_no, description=description, warehouse= warehouse, outlet=outlet, item_decription=item_decription[i], item=item[i], quantity= quantity[i], item_code= item_code[i], selling_price=selling_price[i], transfer="O_O")
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





def DoSomething(checkexist, quantity, item, i, context, INT, db):
    oldQty = checkexist.quantity
   
    if oldQty < int(quantity[i]):
        context["error_message"] = f"We only have {oldQty} {item[i]} left"
        
    # ELSE USE A JS ALERT TO TRANSFER ANYWAY
    else:
      if INT == 'Yes':
         newQty = float(oldQty) - float(quantity[i])
         checkexist.quantity = newQty
         checkexist.save(using=db)
      return True


def DoSomethingElse(context,item, i, store):
    context["error_message"] =  item[i] +' Item not found in '+ store 
    return False