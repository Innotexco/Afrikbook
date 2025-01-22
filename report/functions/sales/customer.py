from customer.models import customer_invoice, customer_table
from main.models import User
from datetime import datetime, timedelta, time, date
from django.db.models import Sum, Count
from django.db.models.functions import Trunc, Extract
from decimal import Decimal

def customer_hourly_sales_func(request, start_date, end_date):
    db = request.user.company_id.db_name
    
    # Example date range (you can modify as per your requirements)
    # start_date = datetime(2024, 1, 1).date()
    # end_date = datetime(2024, 1, 7).date()
    # Initialize data list to store hourly sales data
    hourly_sales_data = []
    
    # Iterate through each day in the date range
    current_date = start_date
    while current_date <= end_date:
        # Define start and end times for the current day (from 6:00 AM to 5:59 PM)
        start_time = datetime.combine(current_date, time(hour=6))
        end_time = datetime.combine(current_date, time(hour=17, minute=59, second=59))
        
        # Initialize list to store hourly sales data for the current day
        daily_sales_data = []
        
        # Iterate through each hour of the day
        current_hour = start_time
        while current_hour <= end_time:
            next_hour = current_hour + timedelta(hours=1)
            

            
            # Query sales data for the current hour
            sales_data = customer_invoice.objects.using(db).filter(
                invoice_date__range=(current_hour, next_hour)
            ).aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
            
            item_data = customer_invoice.objects.using(db).filter(
                invoice_date__range=(current_hour, next_hour)
            ).aggregate(total_sales=Sum('qty'))['total_sales'] or 0.0
            
            sales = customer_invoice.objects.using(db).filter(
                invoice_date__range=(current_hour, next_hour)
            ).values("invoiceID").distinct().count() or 0.0
            
             # Format hour in 12-hour format with AM/PM
            hour_start = current_hour.strftime('%I %p')  # Format as hh:mm AM/PM
            hour_end = next_hour.strftime('%I %p')  # Format as hh:mm AM/PM
            
            if sales_data != 0:
                avg = sales_data // item_data
            else:
                avg = "0.0"
            
            # Append the fetched data to daily_sales_data
            hourly_sales_data.append({
                'hour_start': hour_start,  # Format hour as HH:MM
                'hour_end': hour_end,  # Format hour as HH:MM
                'total_sales': sales_data,
                'qty': item_data,
                'sales': sales,
                'avg': avg
            })
            # Move to the next hour
            current_hour = next_hour
        
        # Append daily_sales_data to hourly_sales_data
        # hourly_sales_data.append({
        #     'date': current_date.strftime('%Y-%m-%d'),
        #     'sales_per_hour': daily_sales_data
        # })
        
        # Move to the next day
        current_date += timedelta(days=1)
        
    sales =  customer_invoice.objects.using(db).filter(
            invoice_date=start_time)#.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
    total_sales = sales.values("invoiceID").distinct().count()
    total_qty = sales.aggregate(total_qty=Sum('qty'))['total_qty'] or 0.0
    
   
    return hourly_sales_data, total_sales, total_qty
        


def customer_daily_sales_report(request, start, end, customer, tb):
    db = request.user.company_id.db_name
    
    # Example date range (you can modify as per your requirements)
    start_date = start
    if end is not None:
        end_date = end
    else:
        end_date = start_date + timedelta(days=7)
    
    
    items = []
    # Initialize data list to store daily sales data
    daily_sales_data = []
    
    # Query sales data for each day in the date range
    current_date = start_date
    for item in items:
        
        cus = []
        while current_date <= end_date:
            # Define start and end times for the current day (from 00:00:00 to 23:59:59)
            start_time = datetime.combine(current_date, datetime.min.time())
            end_time = datetime.combine(current_date, datetime.max.time())
            
            for i in customer:
                name, code, f_kwargs = check_db_table(item, tb)
                # Query sales data for the current day
                daily_sales = customer_invoice.objects.using(db).filter(
                    invoice_date__range=(start_time, end_time), **f_kwargs
                ).aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
                
                sales = customer_invoice.objects.using(db).filter(
                    invoice_date__range=(start_time, end_time)
                )
                new_entry = {
                    'name': name,
                    'date': current_date.date,
                    'total_sales': total_sales
                }
                if not any(
                entry['name'] == new_entry['name'] and 
                entry['date'] == new_entry['date']  
                for entry in cus
                ):
                    cus.append(new_entry)
        if not any(
            record['name'] == name and 
            record['date'] == current_date.date 
            for record in daily_sales_data
        ):    
            # Append the fetched data to daily_sales_data
            daily_sales_data.append({
                'name':item,
                'data': cus,
                'date': current_date.strftime('%Y-%m-%d'),
                'total_sales': daily_sales,
                'sales': sales
            })
            
            # Move to the next day
            current_date += timedelta(days=1)
    sales = daily_sales = customer_invoice.objects.using(db).filter(
            invoice_date__range=(start_time, end_time)
        )#.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
    total_sales = sales.values("invoiceID").distinct().count()
    total_qty = sales.aggregate(total_qty=Sum('qty'))['total_qty'] or 0.0
    
   
        
    return daily_sales_data, total_sales, total_qty




def customer_monthly_sales_report(request, start, end, customer, tb):
    db = request.user.company_id.db_name
    
    start_date = start
    if end is not None:
        end_date = end
    else:
        end_date = start_date 
    
    # Initialize data list to store monthly sales data 
    monthly_sales_data = []
    # Query sales data for each month in the date range
    current_date = start_date.replace(day=1)
   
    # cus = []
                
    for i in customer:
       
        name, code, f_kwargs = check_db_table(i, tb)
        # Initialize the `cus` list for each customer
        cus = []
        current_date = start_date.replace(day=1)
        monthly_total = customer_invoice.objects.using(db).filter(
                invoice_date__date__range=(current_date, end_date),
                **f_kwargs   
            ).values("invoiceID").distinct().aggregate(total=Sum('amount_expected'))['total'] or 0.0
        
        rate, color = monthly_rating(monthly_total, db, current_date.month, end_date.month)

        while current_date <= end_date:
            # Determine the end of the current month
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
            end_of_month = datetime(next_year, next_month, 1) - timedelta(days=1)

            # Query sales data for the current month
            monthly_sales = customer_invoice.objects.using(db).filter(
                invoice_date__year=current_date.year,
                invoice_date__month=current_date.month,
                **f_kwargs   
            )
            
            # Calculate total sales for the current month
            total_sales = monthly_sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0

            # Create a new entry for `cus`
            new_entry = {
                'name': name,
                'year': current_date.year,
                'month': current_date.strftime('%b'),
                'total_sales': total_sales,
                'rate': rate,
                'color': color
            }
            
            # Check if the entry already exists in `cus`
            if not any(
                entry['name'] == new_entry['name'] and 
                entry['year'] == new_entry['year'] and 
                entry['month'] == new_entry['month'] 
                for entry in cus
            ):
                cus.append(new_entry)
            
            # Move to the next month
            current_date = end_of_month + timedelta(days=1)
        
        # Reset current_date for the next customer's data
        current_date = start_date.replace(day=1)

        # Check if the record for this customer already exists in `monthly_sales_data`
        if not any(
            record['cus'] == name and 
            record['year'] == current_date.year and 
            record['month'] == current_date.strftime('%b')
            for record in monthly_sales_data
        ):
            monthly_sales_data.append({
                'cus': name,
                'customer': cus,
                'year': current_date.year,
                'month': current_date.strftime('%b'),  # Full month name (e.g., January)
                'sales': monthly_sales,
                'monthly_total': monthly_total,
                'total_sales': monthly_sales.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0,
                'rate': rate,
                'color': color
            })   
            
        
 
     
    sales = customer_invoice.objects.using(db).filter(
        invoice_date__month__range=(start_date.month, end_date.month))
        
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_qty = sales.aggregate(total_sales=Sum('qty'))['total_sales'] or 0.0
    
  
       
    return monthly_sales_data, total_sales, total_qty
    
  
def customer_quaterly_sales_report(request, start, customer, tb):
    db = request.user.company_id.db_name
    
    start_date = start
    
    end_date = start_date.replace(month=12, day=31)
    
    # Initialize data list to store monthly sales data
    quarterly_sales_data = []
    
    
    # Query sales data for each month in the date range
    current_date = start_date.replace(month=1, day=1)  # Start from the first day of the start month
    
    for i in customer:
        name, code, f_kwargs = check_db_table(i, tb)
        
        # Query sales data for the current month
        cus = []
        quarterly_total = customer_invoice.objects.using(db).filter(
            invoice_date__year=current_date.year,
            **f_kwargs
        ).values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
        rate, color = rating(quarterly_total, db, current_date.year,current_date.year)
        while current_date <= end_date:
    
            # Determine the end of the current quarter
            next_month = current_date.month + 3
            next_year = current_date.year
            if next_month > 12:
                next_month -= 12
                next_year += 1
            end_of_quarter = datetime(next_year, next_month, 1) - timedelta(days=1)
            
            # Query sales data for the current quarter
            quarterly_sales = customer_invoice.objects.using(db).filter(
                invoice_date__year=current_date.year,
                invoice_date__month__gte=current_date.month,
                invoice_date__month__lte=end_of_quarter.month,
                **f_kwargs
            ).values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
            
        
            new_entry = {
                'name': name,
                'quarter_start': current_date.strftime('%B %Y'),  # Start month and year of the quarter
                'quarter_end': end_of_quarter.strftime('%B %Y'),
                'total_sales': quarterly_sales
            }
            
             
            
            # Check if the entry already exists in `cus`
            if not any(
                entry['name'] == new_entry['name'] and 
                entry['quarter_start'] == new_entry['quarter_start'] and 
                entry['quarter_end'] == new_entry['quarter_end'] 
                for entry in cus
            ):
                cus.append(new_entry)
            # Move to the next quarter
            current_date = end_of_quarter + timedelta(days=1)  
            
        current_date = start_date.replace(month=1, day=1) 
        
        if not any(
            record['cus'] == name and 
            record['quarter_start'] == current_date.year and 
            record['quarter_end'] == end_of_quarter.strftime('%B %Y')
            for record in quarterly_sales_data
        ):
            # Append the fetched data to quarterly_sales_data
            quarterly_sales_data.append({
                'cus':name,
                'customer': cus,
                'quarter_start': current_date.strftime('%B %Y'),  # Start month and year of the quarter
                'quarter_end': end_of_quarter.strftime('%B %Y'),  # End month and year of the quarter
                'quarterly_total': quarterly_total,
                'rate': rate,
                'color': color
            })
   
        
    
    sales = customer_invoice.objects.using(db).filter(
            invoice_date__year=start_date.year)
        
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_qty = sales.aggregate(total_sales=Sum('qty'))['total_sales'] or 0.0
    
        
    return quarterly_sales_data, total_sales, total_qty
    
    
    


def customer_yearly_sales_report(request, start, end, customer, tb):
    db = request.user.company_id.db_name
    
    # Example date range (you can modify as per your requirements)
    start_date = start
    
    if end is not None:
        end_date = end
    else:
        end_date = start_date 
        
    
    # Initialize data list to store yearly sales data
    yearly_sales_data = []
    
    # Query sales data for each year in the date range
    current_year = start_date.year
    for i in customer:
        name, code, f_kwargs = check_db_table(i, tb)
        cus = []
        # Query sales data for the current year
        yearly_sales = customer_invoice.objects.using(db).filter(
                invoice_date__year__range=(current_year, end_date.year), **f_kwargs
        ).values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.00
        rate, color = rating(yearly_sales, db, current_year, end_date.year)    
        while current_year <= end_date.year:
            # Query sales data for the current year
            yearly_sales = customer_invoice.objects.using(db).filter(
                invoice_date__year=current_year, **f_kwargs
            ).values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
            
            # Append the fetched data to yearly_sales_data
            new_entry = {
                'name': name,
                'year': current_year,
                'total_sales': yearly_sales
            }
            if not any(
                entry['name'] == new_entry['name'] and 
                entry['year'] == new_entry['year']
                for entry in cus
            ):
                cus.append(new_entry)
            # Move to the next year
            current_year += 1
       
        current_year = start_date.year
        if not any(
            record['cus'] == name and 
            record['year'] == current_year
            for record in yearly_sales_data
        ):
            yearly_sales_data.append({
                'cus':name,
                'customer': cus,
                'year': current_year,
                'total_sales': yearly_sales,
                'rate': rate,
                'color': color
            })
   

    
    sales = customer_invoice.objects.using(db).filter(invoice_date__year__range=(start_date.year, end_date.year))
        
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_qty = sales.aggregate(total_sales=Sum('qty'))['total_sales'] or 0.0
    
   
    return yearly_sales_data, total_sales, total_qty
    
    
    
def check_db_table(i, tb):
        if tb == 1:
            name = i.name
            code = i.customer_code
            field = "cusID"
            f_kwargs = {f"{field}": code}
        else:
            name = i['Userlogin']
            code = i['Userlogin']
            field = "Userlogin"
            f_kwargs = {f"{field}": code}
            
        return name, code, f_kwargs    
            

def rating(sales, db, start, end):
        total = customer_invoice.objects.using(db).filter(
                invoice_date__year__range=(start, end)
        ).values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.00
        
        salesInt = int(sales)
        totalInt = int(total)
       
        if salesInt < 1:
            rate = 0
        else:
            rate =  salesInt/ totalInt * 100

        if rate  <= 20:
            color = 'text-red-500'
        elif rate <= 40:
            color = 'text-orange-500'
        elif rate <= 60:
            color = 'text-yellow-500'
        elif rate <= 80:
            color = 'text-green-500'
        else:
            color = 'text-blue-500'
            
        format_rate = format(rate, ".3f")
        
        return  format_rate, color

def monthly_rating(sales, db, start, end):
        total = customer_invoice.objects.using(db).filter(
                invoice_date__month__range=(start, end)
        ).values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.00
        
        salesInt = int(sales)
        totalInt = int(total)
       
        if salesInt < 1:
            rate = 0
        else:
            rate =  salesInt/ totalInt * 100

        if rate  <= 20:
            color = 'text-red-500'
        elif rate <= 40:
            color = 'text-orange-500'
        elif rate <= 60:
            color = 'text-yellow-500'
        elif rate <= 80:
            color = 'text-green-500'
        else:
            color = 'text-blue-500'
            
        format_rate = format(rate, ".3f")
        
        return  format_rate, color