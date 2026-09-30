from django.shortcuts import  redirect
from Stock.models import *
from django.db.models import Q
from datetime import datetime


def _search_chosen(value):
    text = (value or '').strip()
    if not text:
        return ''
    if text.startswith('_ _Choose'):
        return ''
    return text


# for outletstockinreport
def ForOutletStockinReport(request, context, db):
    if request.method == 'GET':
        fromdate = request.GET.get('fromdate')
        todate = request.GET.get('todate')
        searchoutlet = _search_chosen(request.GET.get('searchoutlet'))
        searchitem = _search_chosen(request.GET.get('searchitem'))
        q = Q()
        applied = False
        if searchoutlet:
            q &= Q(outlet=searchoutlet)
            applied = True
        if searchitem:
            codes = list(
                Item.objects.using(db)
                .filter(item_name=searchitem)
                .values_list('generated_code', flat=True)
            )
            q &= Q(item=searchitem) | Q(item_code=searchitem) | Q(item_code__in=codes)
            applied = True
        if fromdate and todate:
            from_date = datetime.strptime(fromdate, '%Y-%m-%d').date()
            to_date = datetime.strptime(todate, '%Y-%m-%d').date()
            q &= Q(datetx__range=(from_date, to_date))
            applied = True
        if not applied:
            return
        getstock = CreateOutletStockIn.objects.using(db).filter(q)
        context['stock'] = getstock
        total_quantity = sum((item.quantity or 0) for item in getstock)
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