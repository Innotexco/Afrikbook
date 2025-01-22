
def OutletStockLevelReport(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)
    daily = request.GET.get('daily')
    db = AfrikBookDB(request)
    report = CreateStockInLog.objects.using(db).all()
    itemLog =[]
    itemLog2 =[]
    dateLog =[]
    dateLog2 =[]
    qtyLog =[]
    DayLog =[]
    total_qty =0.00
    for data in report:
        strDate = str(data.datetx)
        itemName = str(data.item)
        if itemName not in itemLog2:
            itemLog2.append(itemName)
            itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})


        if strDate not in dateLog:
            dateLog.append(strDate)

    
    for date_ in dateLog:
        fetchQty = CreateStockInLog.objects.using(db).filter(datetx=date_)
        for i in fetchQty:
            strDate = str(i.datetx)
            if strDate not in dateLog2:
                qtyLog.append({'qty':i.quantity, 'item':i.item, 'date':strDate,})
                dateLog2.append(strDate)
            else:
                total_qty = float(total_qty) + float(i.quantity)
                for index, item in enumerate(qtyLog):
                    if item.get('date') == strDate:
                        item['qty'] = total_qty
                        # print(item['qty'], data.quantity, "item['qty']item['qty']item['qty']")
        if daily == 'daily':
            date_obj = datetime.strptime(date_, '%Y-%m-%d')
            day_of_week_name = date_obj.strftime('%A')
            DayLog.append(day_of_week_name)
        else:
            DayLog.append(date_)
    currentDate = date.today()
    context = {
        'itemLog': itemLog,
        'dateLog': DayLog,
        'qtyLog': qtyLog,
        'currentDate': currentDate,
    }


    print(itemLog, 'dateLogdateLog')
    print(qtyLog, 'dateLogdateLog' )





    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            
            from_time = time(14, 0)
            to_time = time(16, 0)
            print( fromdate, todate,)
            DayLog =[]
            dateLog =[]
            warehouseArray =[]
            all_qty_sent_to_warehouse =0.00
            all_qty_sent_from_warehouse =0.00
            all_qty_sent_within_warehouse_table =0.00
            # get_item_transfered_to_warehouse =None
            # report = CreateStockInLog.objects.using(db).all()
            get_item_transfered_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)) )
            for quality in get_item_transfered_to_warehouse:
                strDate = str(quality.datetx)

                

                # make sure item of same store are not looped again
                if strDate not in dateLog:
                    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(Q(outlet=quality.outlet) & Q(datetx=strDate))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_warehouse_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse=quality.outlet) & Q(datetx=strDate))
                    for warehouse_qty_in_outlet in get_item_transfered_from_warehouse_to_outlet:
                        all_qty_sent_from_warehouse = float(all_qty_sent_from_warehouse) + float(warehouse_qty_in_outlet.quantity)
                    

                    get_item_transfered_from_outlet_to_outlet = CreateStockInLog.objects.using(db).filter(Q(warehouse=quality.outlet) & Q(datetx=strDate))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_warehouse_table = float(all_qty_sent_within_warehouse_table) + float(outlet_qty_in_outlet.quantity)

                    warehouseArray.append(quality.outlet)
                print(all_qty_sent_to_warehouse, all_qty_sent_from_warehouse, all_qty_sent_within_warehouse_table, 'all_qty_sent_within_warehouse_table')

                total_qty = all_qty_sent_to_warehouse - all_qty_sent_from_warehouse + all_qty_sent_within_warehouse_table
                
                if strDate not in dateLog:
                    dateLog.append(strDate)
                    date_obj = datetime.strptime(str(quality.datetx), '%Y-%m-%d')
                    day_of_week_name = date_obj.strftime('%A')
                    DayLog.append({'date':strDate, 'days':day_of_week_name, 'qty':quality.quantity, 'item':quality.item})
                else:
                    for index, item in enumerate(DayLog):
                        if item.get('date') == strDate:
                            item['qty'] = total_qty
                            # print(item['qty'], data.quantity, "item['qty']item['qty']item['qty']")





            print(all_qty_sent_to_warehouse, all_qty_sent_from_warehouse,'qtyqtyqtyqtyqty')


            print(DayLog, 'dateLogdateLogdateLogdateLog')


            if DayLog is not None:
                stockLevel = DayLog
                return JsonResponse({'data': stockLevel})
        

    return render(request, 'report/OutletStockLevelReport.html', context)







    # for data in report:

    #     # get_item_transfered_to_outlet = CreateStockInLog.objects.using(db).filter(Q(outlet=data.outlet) & Q(item_code=data.item_code) & Q(datetx__range=(fromDate, toDate)))
    #     # for quality in get_item_transfered_to_outlet:
    #     #     qty = float(qty) + float(quality.quantity) 
    #     #     print(quality.quantity, 'qualityqualityquality.quantity')


    #     strDate = str(data.datetx)
        
    #     if strDate not in dateLog:
    #         dateLog.append(strDate)
    #         date_obj = datetime.strptime(str(data.datetx), '%Y-%m-%d')
    #         day_of_week_name = date_obj.strftime('%A')
    #         DayLog.append({'date':strDate, 'days':day_of_week_name, 'qty':data.quantity})
    #     else:
    #         for index, item in enumerate(DayLog):
    #             if item.get('date') == strDate:
    #                 item['qty'] = item['qty'] + data.quantity
    #                 # print(item['qty'], data.quantity, "item['qty']item['qty']item['qty']")
    #                 # item['qty'] = ''

        


def OutletStockLevelReport_Daily(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)


    db = AfrikBookDB(request)

    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            report = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)))

            itemLog =[]
            non_dict_item_log =[]
            dateLog =[]
            dateLog2 =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_warehouse =0.00
            all_qty_sent_from_warehouse =0.00
            all_qty_sent_within_warehouse_table =0.00
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)
                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})
                # all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(data.quantity)
                if strDate not in dateLog:
                    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(~Q(outlet=None) & Q(datetx=strDate))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_warehouse_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(datetx=strDate))
                    for warehouse_qty_in_outlet in get_item_transfered_from_warehouse_to_outlet:
                        all_qty_sent_from_warehouse = float(all_qty_sent_from_warehouse) + float(warehouse_qty_in_outlet.quantity)
                    

                    get_item_transfered_from_outlet_to_outlet = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(datetx=strDate))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_warehouse_table = float(all_qty_sent_within_warehouse_table) + float(outlet_qty_in_outlet.quantity)


                    total_qty = all_qty_sent_to_warehouse - all_qty_sent_from_warehouse + all_qty_sent_within_warehouse_table
                    dateLog.append(strDate)

                    qtyLog.append({'qty':total_qty, 'item':data.item, 'date':strDate,})
                    if daily == 'daily':
                        date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                        day_of_week_name = date_obj.strftime('%A')
                        DayLog.append(day_of_week_name)
                    else:
                        DayLog.append(strDate)
                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == strDate:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        
            print(itemLog, 'dateLogdateLog')
            print(qtyLog, 'dateLogdateLog' )

   
    # context = {
    #     'itemLog': itemLog,
    #     'dateLog': DayLog,
    #     'qtyLog': qtyLog,
    #     'currentDate': currentDate,
    # }

    date_obj = datetime.strptime('2024-07-30', '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')
    print(year, month, 'monthmonthmonthmonth')



    return render(request, 'report/OutletStockLevelReport.html')





def OutletStockLevelReport_Monthly(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)


    db = AfrikBookDB(request)

    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            report = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)))

            itemLog =[]
            non_dict_year_log =[]
            non_dict_month_log =[]
            non_dict_item_log =[]
            dateLog =[]
            dateLog2 =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_warehouse =0.00
            all_qty_sent_from_warehouse =0.00
            all_qty_sent_within_warehouse_table =0.00
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)

                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%m')
                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})


                # all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(data.quantity)
                if  month not in non_dict_month_log:
                    print(month, 'monthmonthmonthmonthmonth')
                    # non_dict_year_log.append(year)
                    non_dict_month_log.append(month)
                    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(~Q(outlet=None) & Q(datetx__year=year) & Q(datetx__month=month))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_warehouse_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(datetx__year=year) & Q(datetx__month=month))
                    for warehouse_qty_in_outlet in get_item_transfered_from_warehouse_to_outlet:
                        all_qty_sent_from_warehouse = float(all_qty_sent_from_warehouse) + float(warehouse_qty_in_outlet.quantity)
                    

                    get_item_transfered_from_outlet_to_outlet = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(datetx__year=year) & Q(datetx__month=month))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_warehouse_table = float(all_qty_sent_within_warehouse_table) + float(outlet_qty_in_outlet.quantity)

                    add_deductions = float(all_qty_sent_from_warehouse) + float(all_qty_sent_within_warehouse_table)
                    total_qty = float(all_qty_sent_to_warehouse) - float(add_deductions)
                    non_dict_year_log.append(year)
                    non_dict_month_log.append(month)
                    print(all_qty_sent_to_warehouse, add_deductions, total_qty)
                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    if daily != 'daily':
                        # DayLog.append(month+'_'+year)
                        fullmonthName = date_obj.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    else:
                        pass
                        # DayLog.append(strDate)
                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('month') == month:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        
            print(itemLog, 'dateLogdateLog')
            print(qtyLog, 'dateLogdateLog')

   
    # context = {
    #     'itemLog': itemLog,
    #     'dateLog': DayLog,
    #     'qtyLog': qtyLog,
    #     'currentDate': currentDate,
    # }

    date_obj = datetime.strptime('2024-07-30', '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')

        

    return render(request, 'report/OutletStockLevelReport.html')






def OutletStockLevelReport_Yearly(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)


    db = AfrikBookDB(request)

    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            report = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)))

            itemLog =[]
            non_dict_year_log =[]
            non_dict_month_log =[]
            non_dict_item_log =[]
            dateLog =[]
            dateLog2 =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_warehouse =0.00
            all_qty_sent_from_warehouse =0.00
            all_qty_sent_within_warehouse_table =0.00
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)

                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%m')
                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})
                # all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(data.quantity)
                if  year not in non_dict_year_log:
                    print(year, 'monthmonthmonthmonthmonth')
                    # non_dict_year_log.append(year)
                    non_dict_year_log.append(year)
                    all_qty_sent_to_warehouse_for_that_day = CreateStockInLog.objects.using(db).filter(~Q(outlet=None) & Q(datetx__year=year))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_warehouse = float(all_qty_sent_to_warehouse) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_warehouse_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(datetx__year=year))
                    for warehouse_qty_in_outlet in get_item_transfered_from_warehouse_to_outlet:
                        all_qty_sent_from_warehouse = float(all_qty_sent_from_warehouse) + float(warehouse_qty_in_outlet.quantity)
                    

                    get_item_transfered_from_outlet_to_outlet = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='warehouse') & Q(datetx__year=year))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_warehouse_table = float(all_qty_sent_within_warehouse_table) + float(outlet_qty_in_outlet.quantity)

                    add_deductions = float(all_qty_sent_from_warehouse) + float(all_qty_sent_within_warehouse_table)
                    total_qty = float(all_qty_sent_to_warehouse) - float(add_deductions)
                    non_dict_year_log.append(year)
                    non_dict_month_log.append(month)
                    print(all_qty_sent_to_warehouse, add_deductions, total_qty)
                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    if daily != 'daily':
                        DayLog.append('{year}'.format( year=year))
                    else:
                        pass
                        # DayLog.append(strDate)
                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == year:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        
            print(itemLog, 'dateLogdateLog')
            print(qtyLog, 'dateLogdateLog')

   
    # context = {
    #     'itemLog': itemLog,
    #     'dateLog': DayLog,
    #     'qtyLog': qtyLog,
    #     'currentDate': currentDate,
    # }

    date_obj = datetime.strptime('2024-07-30', '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')



    return render(request, 'report/OutletStockLevelReport.html')






       


def OutletStockLevelReport_OutleYearly(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)


    db = AfrikBookDB(request)

    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            report = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)))

            itemLog =[]
            non_dict_year_log =[]
            non_dict_month_log =[]
            non_dict_item_log =[]
            dateLog =[]
            dateLog2 =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_outlet =0.00
            all_qty_sent_within_outlet_table =0.00
            all_qty_sold_from_outlet =0.00
            all_qty_sent_from_outlet =0.00
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)

                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%m')
                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})

                # all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(data.quantity)

                if  year not in non_dict_year_log:
                    print(year, 'monthmonthmonthmonthmonth')
                    # non_dict_year_log.append(year)
                    non_dict_year_log.append(year)
                    all_qty_sent_to_warehouse_for_that_day = CreateOutletStockInLog.objects.using(db).filter(~Q(outlet=None) & Q(datetx__year=year))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_outlet_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop')  &  Q(datetx__year=year))
                    for outlet_qty_in_warehouse in get_item_transfered_from_outlet_to_warehouse:
                        all_qty_sent_from_outlet = float(all_qty_sent_from_outlet) + float(outlet_qty_in_warehouse.quantity)
                    
                    get_item_transfered_from_outlet_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop') &  Q(datetx__year=year))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_outlet_table = float(all_qty_sent_within_outlet_table) + float(outlet_qty_in_outlet.quantity)

                    get_item_sold_from_outlet = customer_invoice.objects.using(db).filter(Q(invoice_date__year=year) & ~Q(cancellation_status=1))
                    for warehouse_qty_in_outlet in get_item_sold_from_outlet:
                        all_qty_sold_from_outlet = float(all_qty_sold_from_outlet) + float(warehouse_qty_in_outlet.qty)

                    add_deductions = float(all_qty_sent_from_outlet) + float(all_qty_sold_from_outlet) + float(all_qty_sent_within_outlet_table)
                    total_qty = float(all_qty_sent_to_outlet) - float(add_deductions)

                    non_dict_year_log.append(year)
                    non_dict_month_log.append(month)
                    print(all_qty_sent_to_outlet, add_deductions, total_qty)
                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    if daily != 'daily':
                        DayLog.append('{year}'.format( year=year))
                    else:
                        pass
                        # DayLog.append(strDate)
                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == year:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        
            print(itemLog, 'dateLogdateLog')
            print(qtyLog, 'dateLogdateLog')

   
    # context = {
    #     'itemLog': itemLog,
    #     'dateLog': DayLog,
    #     'qtyLog': qtyLog,
    #     'currentDate': currentDate,
    # }

    date_obj = datetime.strptime('2024-07-30', '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')

    return render(request, 'report/OutletStockLevelReport.html')

    


def OutletStockLevelReport_Outlemonthly(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)


    db = AfrikBookDB(request)

    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            report = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)))

            itemLog =[]
            non_dict_year_log =[]
            non_dict_month_log =[]
            non_dict_item_log =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_outlet =0.00
            all_qty_sent_within_outlet_table =0.00
            all_qty_sold_from_outlet =0.00
            all_qty_sent_from_outlet =0.00
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)

                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%m')
                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})

                # all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(data.quantity)

                if  month not in non_dict_month_log:
                    print(month, 'monthmonthmonthmonthmonth')
                    # non_dict_year_log.append(year)
                    non_dict_month_log.append(month)
                    all_qty_sent_to_warehouse_for_that_day = CreateOutletStockInLog.objects.using(db).filter(~Q(outlet=None) &  Q(datetx__year=year) & Q(datetx__month=month))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_outlet_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop')  &   Q(datetx__year=year) & Q(datetx__month=month))
                    for outlet_qty_in_warehouse in get_item_transfered_from_outlet_to_warehouse:
                        all_qty_sent_from_outlet = float(all_qty_sent_from_outlet) + float(outlet_qty_in_warehouse.quantity)
                    
                    get_item_transfered_from_outlet_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop') &   Q(datetx__year=year) & Q(datetx__month=month))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_outlet_table = float(all_qty_sent_within_outlet_table) + float(outlet_qty_in_outlet.quantity)

                    get_item_sold_from_outlet = customer_invoice.objects.using(db).filter(Q(invoice_date__year=year) & Q(invoice_date__month=month) & ~Q(cancellation_status=1))
                    for warehouse_qty_in_outlet in get_item_sold_from_outlet:
                        all_qty_sold_from_outlet = float(all_qty_sold_from_outlet) + float(warehouse_qty_in_outlet.qty)

                    add_deductions = float(all_qty_sent_from_outlet) + float(all_qty_sold_from_outlet) + float(all_qty_sent_within_outlet_table)
                    total_qty = float(all_qty_sent_to_outlet) - float(add_deductions)

                    # non_dict_year_log.append(year)
                    # non_dict_month_log.append(month)

                    print(all_qty_sent_to_outlet, add_deductions, total_qty)
                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    if daily != 'daily':
                        fullmonthName = date_obj.strftime('%B')
                        DayLog.append('{month}_{year}'.format(month=fullmonthName, year=year))
                    else:
                        pass
                        # DayLog.append(strDate)
                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == year:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        
            print(itemLog, 'dateLogdateLog')
            print(qtyLog, 'dateLogdateLog')

   
    # context = {
    #     'itemLog': itemLog,
    #     'dateLog': DayLog,
    #     'qtyLog': qtyLog,
    #     'currentDate': currentDate,
    # }

    date_obj = datetime.strptime('2024-07-30', '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')



        

    return render(request, 'report/OutletStockLevelReport.html')




def OutletStockLevelReport_OutleYearly(request):
    # date_obj = datetime.strptime('2024-07-03', '%Y-%m-%d')
    # day_of_week_num = date_obj.weekday()
    # day_of_week_name = date_obj.strftime('%A')
    # print(date_obj, 'NOD',day_of_week_num, day_of_week_name)


    db = AfrikBookDB(request)

    if request.method == 'GET':
        begin = request.GET.get('begin')
        end = request.GET.get('end')
        daily = request.GET.get('daily')
        fromdate    = request.GET.get('fromdate')
        todate      = request.GET.get('todate')
        if fromdate and todate is not None:
            from_date, to_date = getdateReport(fromdate, todate)
            report = CreateStockInLog.objects.using(db).filter(Q(datetx__range=(from_date, to_date)))

            itemLog =[]
            non_dict_year_log =[]
            non_dict_month_log =[]
            non_dict_item_log =[]
            qtyLog =[]
            DayLog =[]
            total_qty =0.00
            all_qty_sent_to_outlet =0.00
            all_qty_sent_within_outlet_table =0.00
            all_qty_sold_from_outlet =0.00
            all_qty_sent_from_outlet =0.00
            for data in report:
                strDate = str(data.datetx)
                itemName = str(data.item)

                date_obj = datetime.strptime(strDate, '%Y-%m-%d')
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%m')
                if itemName not in non_dict_item_log:
                    non_dict_item_log.append(itemName)
                    itemLog.append({'date':strDate,  'qty':data.quantity, 'item':data.item})

                # all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(data.quantity)

                if  year not in non_dict_year_log:
                    print(year, 'yearyearyearyearyear')
                    # non_dict_year_log.append(year)
                    non_dict_year_log.append(year)
                    all_qty_sent_to_warehouse_for_that_day = CreateOutletStockInLog.objects.using(db).filter(~Q(outlet=None) &  Q(datetx__year=year))
                    for warehouse_qty_sent_to_warehouse in all_qty_sent_to_warehouse_for_that_day:
                        all_qty_sent_to_outlet = float(all_qty_sent_to_outlet) + float(warehouse_qty_sent_to_warehouse.quantity)

                    get_item_transfered_from_outlet_to_warehouse = CreateStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop')  &   Q(datetx__year=year))
                    for outlet_qty_in_warehouse in get_item_transfered_from_outlet_to_warehouse:
                        all_qty_sent_from_outlet = float(all_qty_sent_from_outlet) + float(outlet_qty_in_warehouse.quantity)
                    
                    get_item_transfered_from_outlet_to_outlet = CreateOutletStockInLog.objects.using(db).filter(Q(warehouse__icontains='shop') &   Q(datetx__year=year))
                    for outlet_qty_in_outlet in get_item_transfered_from_outlet_to_outlet:
                        all_qty_sent_within_outlet_table = float(all_qty_sent_within_outlet_table) + float(outlet_qty_in_outlet.quantity)

                    get_item_sold_from_outlet = customer_invoice.objects.using(db).filter(Q(invoice_date__year=year) & ~Q(cancellation_status=1))
                    for warehouse_qty_in_outlet in get_item_sold_from_outlet:
                        all_qty_sold_from_outlet = float(all_qty_sold_from_outlet) + float(warehouse_qty_in_outlet.qty)

                    add_deductions = float(all_qty_sent_from_outlet) + float(all_qty_sold_from_outlet) + float(all_qty_sent_within_outlet_table)
                    total_qty = float(all_qty_sent_to_outlet) - float(add_deductions)

                    # non_dict_year_log.append(year)
                    # non_dict_month_log.append(month)

                    print(all_qty_sent_to_outlet, add_deductions, total_qty)
                    qtyLog.append({'qty':total_qty, 'item':data.item, 'month':month, 'date':year})
                    if daily != 'daily':
                        fullmonthName = date_obj.strftime('%B')
                        DayLog.append('{year}'.format(year=year))
                    else:
                        pass
                        # DayLog.append(strDate)
                else:
                    pass
                    # for index, item in enumerate(qtyLog):
                    #     if item.get('date') == year:
                    #         item['qty'] = total_qty

                


            currentDate = date.today()

            if DayLog is not None:
                return JsonResponse({'dateLog': DayLog, 'itemLog': itemLog, 'qtyLog': qtyLog, 'currentDate': currentDate})
        
            print(itemLog, 'dateLogdateLog')
            print(qtyLog, 'dateLogdateLog')

   
    # context = {
    #     'itemLog': itemLog,
    #     'dateLog': DayLog,
    #     'qtyLog': qtyLog,
    #     'currentDate': currentDate,
    # }

    date_obj = datetime.strptime('2024-07-30', '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')

    
        

    return render(request, 'report/OutletStockLevelReport.html')






        
