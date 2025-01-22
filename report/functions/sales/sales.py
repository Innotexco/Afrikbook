from customer.models import customer_invoice
from account.models import Expenses_account
from datetime import datetime, timedelta, time, date
from django.db.models import Sum, Count
from django.db.models.functions import Trunc, Extract
from vendor.models import Vendor_invoice
from decimal import Decimal

def hourly_sales_func(request, start_date, end_date):
    db = request.user.company_id.db_name
   
    # Initialize data list to store hourly sales data
    hourly_sales_data = []
  
    # Iterate through each day in the date range
    current_date = start_date
    while current_date <= end_date:
        # Define start and end times for the current day (from 6:00 AM to 5:59 PM)
        start_time = datetime.combine(current_date, time(hour=6))
        
        # end_time = datetime.combine(current_date, time(hour=23, minute=59, second=59))
        end_time = datetime.combine(current_date + timedelta(days=1), time(hour=5))
        
       
        # Iterate through each hour of the day
        current_hour = start_time
        
        while current_hour <= end_time:
            next_hour = current_hour + timedelta(hours=1)
            
            # If current_hour is midnight, adjust to 12:00 AM for comparison
            if current_hour.time() == time(hour=0):
                current_hour = current_hour.replace(hour=12, minute=0, second=0)
            else:
                current_hour = current_hour
            
            sales_data = customer_invoice.objects.using(db).filter(
                invoice_date__time__range=(current_hour, next_hour), invoice_date__date=current_date
            ).values()
            
            item_data = customer_invoice.objects.using(db).filter(
                invoice_date__range=(current_hour, next_hour)
            ).aggregate(total_sales=Sum('qty'))['total_sales'] or 0.0
            
            sales = customer_invoice.objects.using(db).filter(
                invoice_date__time__range=(current_hour, next_hour), invoice_date__date=current_date
            ).values("invoiceID").distinct().count() or 0.0
            
             # Format hour in 12-hour format with AM/PM
            hour_start = current_hour.strftime('%I %p')  # Format as hh:mm AM/PM
            hour_end = next_hour.strftime('%I %p')  # Format as hh:mm AM/PM
            
            total_sales = sales_data.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
            qty = sales_data.aggregate(total_sales=Sum('qty'))['total_sales'] or 0.0
                
            if qty != 0.0:
                avg = total_sales // qty
            else:
                avg = "0.0"
           
            # Append the fetched data to daily_sales_data
            hourly_sales_data.append({
                'hour_start': hour_start,  # Format hour as HH:MM
                'hour_end': hour_end,  # Format hour as HH:MM
                'sales': sales_data,
                'total_sales': total_sales,
                'qty': qty,
                'sales_count': sales,
                'avg': avg
            })
            
            # Move to the next hour
            current_hour = next_hour
       
        # Move to the next day
        current_date += timedelta(days=1)
      
    sales =  customer_invoice.objects.using(db).filter(invoice_date__date=start_date)
    
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_qty = sales.aggregate(total_qty=Sum('qty'))['total_qty'] or 0.0
   
   
    return hourly_sales_data, total_sales, total_qty
        


def daily_sales_report(request, start, end):
    db = request.user.company_id.db_name
    
    # Example date range (you can modify as per your requirements)
    start_date = start
    if end is not None:
        end_date = end
    else:
        end_date = start_date #+ timedelta(days=7)
        
    
    # Initialize data list to store daily sales data
    daily_sales_data = []
    
    # Query sales data for each day in the date range
    current_date = start_date
    while current_date <= end_date:
        # Define start and end times for the current day (from 00:00:00 to 23:59:59)
        start_time = datetime.combine(current_date, datetime.min.time())
        end_time = datetime.combine(current_date, datetime.max.time())
        
        sales = customer_invoice.objects.using(db).filter(
            invoice_date__range=(start_time, end_time)
        )
        purchase = Expenses_account.objects.using(db).filter(
            created_at__range=(start_time, end_time)
        )
        
        total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.00
        total_purchase = purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.00
        
        # Append the fetched data to daily_sales_data
        daily_sales_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total_sales': total_sales,
            'sales': sales,
            'purchase': purchase,
            'total_purchase': total_purchase,
            'total': Decimal(total_sales) - Decimal(total_purchase)
        })
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    sales_ = customer_invoice.objects.using(db).filter(
            invoice_date__date__range=(start_date, end_date))
    purchase_ = Expenses_account.objects.using(db).filter(
            created_at__date__range=(start_date, end_date))
    
    total_sales = sales_.values("invoiceID").distinct().aggregate(total_qty=Sum('amount_expected'))['total_qty'] or 0.0
    # total_s_price = sales_.aggregate(total_qty=Sum('amount'))['total_qty'] or 0.0
    
    total_purchase = purchase_.aggregate(total_qty=Sum('amount'))['total_qty'] or 0.00
    # total_p_price = purchase_.aggregate(total_qty=Sum('amount'))['total_qty'] or 0.0
    
    total = Decimal(total_sales) - Decimal(total_purchase)
    
    
        
    return daily_sales_data, total_sales, total_purchase, total




def monthly_sales_report(request, start, end):
    db = request.user.company_id.db_name
    
    start_date = start
    if end is not None:
        end_date = end
    else:
        end_date = start_date 
    
    # Initialize data list to store monthly sales data
    monthly_sales_data = []
    
    
    
    # Query sales data for each month in the date range
    current_date = start_date.replace(day=1)  # Start from the first day of the start month
    while current_date <= end_date:
        # Determine the end of the current month
        next_month = current_date.month + 1 if current_date.month < 12 else 1
        next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
        end_of_month = datetime(next_year, next_month, 1) - timedelta(days=1)
        
        # Query sales data for the current month
        monthly_sales = customer_invoice.objects.using(db).filter(
            invoice_date__year=current_date.year,
            invoice_date__month=current_date.month
        )
        
        purchase = Expenses_account.objects.using(db).filter(
            created_at__year=current_date.year,
            created_at__month=current_date.month
        )
        
        total_sales = monthly_sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
        total_purchase = purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
        
        
        # Append the fetched data to monthly_sales_data
        monthly_sales_data.append({
            'year': current_date.year,
            'month': current_date.strftime('%b'),  # Full month name (e.g., January),
            'sales': monthly_sales,
            'total_sales': total_sales,
            'purchase': purchase,
            'total_purchase': total_purchase,
            'total': Decimal(total_sales) - Decimal(total_purchase)
        })
        
        # Move to the next month
        current_date = end_of_month + timedelta(days=1)
    
    sales = customer_invoice.objects.using(db).filter(invoice_date__month__range=(start_date.month, end_date.month))

    purchase = Expenses_account.objects.using(db).filter(created_at__month__range=(start_date.month, end_date.month))
        
        
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_purchase = purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
    
    total = Decimal(total_sales) - Decimal(total_purchase)
    
        
    return monthly_sales_data, total_sales, total_purchase, total
    
  
def quaterly_sales_report(request, start):
    db = request.user.company_id.db_name
    
    start_date = start
    
    end_date = start_date.replace(month=12, day=31)
    
    # Initialize data list to store monthly sales data
    quarterly_sales_data = []
    
    
    # Query sales data for each month in the date range
    current_date = start_date.replace(month=1, day=1)  # Start from the first day of the start month
    
    
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
            invoice_date__month__lte=end_of_quarter.month
        )
        
        quarterly_purchase = Expenses_account.objects.using(db).filter(
            created_at__year=current_date.year,
            created_at__month__gte=current_date.month,
            created_at__month__lte=end_of_quarter.month
        )
        total_sales = quarterly_sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
        total_purchase = quarterly_purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
        
        # Append the fetched data to quarterly_sales_data
        quarterly_sales_data.append({
            'quarter_start': current_date.strftime('%B %Y'),  # Start month and year of the quarter
            'quarter_end': end_of_quarter.strftime('%B %Y'),  # End month and year of the quarter
            'sales': quarterly_sales,
            'total_sales': total_sales,
            'purchase': quarterly_purchase,
            'total_purchase': total_purchase,
            'total': Decimal(total_sales) - Decimal(total_purchase)
        })
        
        # Move to the next quarter
        current_date = end_of_quarter + timedelta(days=1)
    
    sales = customer_invoice.objects.using(db).filter(invoice_date__year=start.year)
    purchase = Expenses_account.objects.using(db).filter(created_at__year=start.year)
        
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_purchase = purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
   
    total = Decimal(total_sales) - Decimal(total_purchase)
    
        
    return quarterly_sales_data, total_sales, total_purchase, total
    
  
    


def yearly_sales_report(request, start, end):
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
    while current_year <= end_date.year:
        # Query sales data for the current year
        yearly_sales = customer_invoice.objects.using(db).filter(
            invoice_date__year=current_year
        )
        yearly_purchase = Expenses_account.objects.using(db).filter(
            created_at__year=current_year
        )
        total_sales = yearly_sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
        total_purchase = yearly_purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
        # Append the fetched data to yearly_sales_data
      
        entry = {
            'year': current_year,
            'sales': yearly_sales,
            'total_sales': total_sales,
            'purchase': yearly_purchase,
            'total_purchase': total_purchase,
            'total': Decimal(total_sales) - Decimal(total_purchase)
        }
        if not any(record['year'] == entry['year']  for record in yearly_sales_data):
        # for i in entry['sales']:
        #     for item in yearly_sales_data:
        #         for obj in  item['sales']:
        #            
        #             if not obj.invoiceID == i.invoiceID:
        #                 pass
             yearly_sales_data.append(entry)
                

        # Move to the next year
        current_year += 1
   

    sales = customer_invoice.objects.using(db).filter(invoice_date__year__range=(start_date.year, end_date.year))
    purchase = Expenses_account.objects.using(db).filter(created_at__year__range=(start_date.year, end_date.year))
        
    total_sales = sales.values("invoiceID").distinct().aggregate(total_sales=Sum('amount_expected'))['total_sales'] or 0.0
    total_purchase = purchase.aggregate(total_sales=Sum('amount'))['total_sales'] or 0.0
    
    total = Decimal(total_sales) - Decimal(total_purchase)
    
   
    return yearly_sales_data, total_sales, total_purchase, total
    
    