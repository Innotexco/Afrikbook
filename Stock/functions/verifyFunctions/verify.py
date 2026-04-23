from Stock.models import  CreateStockInLog, CreateStockIn, CreateOutletStockIn, CreateOutletStockInLog;
from django.db.models import Q
from django.http import HttpResponse, JsonResponse,Http404;

def VerifyStockTransfer(request, context):
    itemID = request.POST.get('itemID')
    outlet = request.POST.get('outlet')
    warehouse = request.POST.get('warehouse')
    whichtrans = request.POST.get('whichtrans') 
    quantity = request.POST.get('quantity') 
    item_code = request.POST.get('item_code') 
    buttonName = request.POST.get('buttonName') 
    # if  verify btn was click
    if 'verify' in request.POST or buttonName != '' :
        allgood = False

        if  whichtrans == 'W_W' or  whichtrans == 'W_O' or  whichtrans == 'O_W' or  whichtrans == 'O_O':
            # To avoid repetetion
            # for warehouse ********************************
            private_To_W = CreateStockIn.objects.get(item_code=item_code, warehouse=outlet)
            private_From_W =  CreateStockIn.objects.get(item_code=item_code, warehouse=warehouse)
            # for warehouse ********************************

            # for OUTLET ********************************
            private_To_O =  CreateOutletStockIn.objects.get(item_code=item_code, outlet=outlet)
            private_From_O =  CreateOutletStockIn.objects.get(item_code=item_code, outlet=warehouse)
            # for OUTLET ********************************


            if whichtrans == 'W_W':
                updateQTYfrom = private_From_W
                updateQTYto   = private_To_W
                if updateQTYfrom and updateQTYto:
                    allgood = True

            elif whichtrans == 'W_O':
                updateQTYfrom = private_From_W
                updateQTYto = private_To_O
                if updateQTYfrom and updateQTYto:
                    allgood = True

            elif whichtrans == 'O_W':
                updateQTYfrom = private_From_O
                updateQTYto   = private_To_W
                if updateQTYfrom and updateQTYto:
                    allgood = True



            elif whichtrans == 'O_O':
                updateQTYfrom = private_From_O
                updateQTYto = private_To_O
                if updateQTYfrom and updateQTYto:
                    allgood = True


        if allgood :
            oldQty = updateQTYfrom.quantity
            newQty = float(oldQty) - float(quantity)
            updateQTYfrom.quantity = newQty
            updateQTYfrom.save()


            oldQty2 = updateQTYto.quantity
            newQty2 = float(oldQty2) + float(quantity)
            updateQTYto.quantity = newQty2
            updateQTYto.save()

            if updateQTYfrom and updateQTYto :
                StockInLog = None
                if whichtrans == 'W_W' or  whichtrans == 'O_W':
                    StockInLog = CreateStockInLog
                elif whichtrans == 'W_O' or whichtrans == 'O_O':
                    StockInLog = CreateOutletStockInLog

                if StockInLog is not None:
                    updateStatus = StockInLog.objects.get(id=itemID)
                    updateStatus.status = 'Verified'
                    updateStatus.save()
                    if updateStatus:
                        if buttonName != None:
                          getUnverified = StockInLog.objects.filter(status='Unverified', transfer=whichtrans).values()
                          return list(getUnverified)

                        context["success_message"] =  'Transer verified'

                    else:
                        context["error_message"] =  'Verification Failed'

    # if  delete btn was click
    deleteID = request.POST.get('deleteID')
                        
    if 'delete_btn' in request.POST or deleteID:
        
        if deleteID:
            itemID = deleteID
            whichtrans = request.POST.get('transtype')

        StockInLog = None
        if whichtrans == 'W_W' or whichtrans == 'O_W':
            StockInLog = CreateStockInLog
        elif whichtrans == 'W_O' or  whichtrans == 'O_O':
            StockInLog = CreateOutletStockInLog

        if StockInLog is not None:
            updateStatus = StockInLog.objects.get(id=itemID)
            updateStatus.delete()
            if updateStatus:
                if deleteID:
                    response_data = {'message': 'Transfer successfully deleted'}
                    return  response_data 
                context["success_message"] =  'Transfer successfully deleted'
            else:
                if deleteID:
                    response_data = {'error': 'Deletion Failed'}
                    return  response_data 
                context["error_message"] =  'Deletion Failed'

        # *****************************************************************************************************

        