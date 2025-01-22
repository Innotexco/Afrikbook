from django.shortcuts import  redirect
from Stock.models import *
from django.db.models import Q
from datetime import datetime


# for outletstockinreport
def ForOutletStockinReport(request, context, db):
    if request.method == 'GET':
        fromdate = request.GET.get('fromdate')
        todate = request.GET.get('todate')
        searchoutlet = request.GET.get('searchoutlet')
        searchitem = request.GET.get('searchitem')
        from_date = None
        to_date = None
        if fromdate and todate:
            from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
            to_date = datetime.strptime(todate, '%Y-%m-%d').date()
        getstock = CreateOutletStockIn.objects.using(db).filter(Q(outlet=searchoutlet) | Q(item=searchitem) | Q(datetx__range=(from_date, to_date)))
        if getstock:
            context['stock'] = getstock
            total_quantity = sum(item.quantity for item in getstock)
            context['qty'] = total_quantity
            return redirect('/outlet-stockin-report')


# for stockinreport
def ForStockInReport(request, context, db):
   if request.method == 'GET':
        fromdate = request.GET.get('fromdate')
        todate = request.GET.get('todate')
        searchwarehouse = request.GET.get('sortbyWareHh')
        searchitem = request.GET.get('sortbyItem')
        from_date = None
        to_date = None
        if searchwarehouse or searchitem or fromdate and todate:
            if fromdate and todate is not None:
                from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                to_date = datetime.strptime(todate, '%Y-%m-%d').date()
            getstock = CreateStockIn.objects.using(db).filter(Q(warehouse=searchwarehouse) | Q(item=searchitem) | Q(datetx__range=(from_date, to_date)))
            if getstock:
                # context['stock'] = getstock
                stockReport = [{
                    'item':report.item,
                    'quantity':report.quantity,
                    'datetx':report.datetx,
                    'invoice_no':report.invoice_no,
                    'description':report.description,
                    'warehouse':report.warehouse,
                } for report in getstock];

                qty = sum(item.quantity for item in getstock)
                return  stockReport, qty
            else:
                return {'error_message':'Data not found'}