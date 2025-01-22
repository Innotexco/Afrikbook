from settings.models import SetItemNotification
from Stock.models import CreateStockInLog

from datetime import datetime, timezone, date



def getData(items, db):
    today = date.today()
    
    for i in items:
        i.rdays = (i.expiry_date - today).days
       
        try:
            item1 = SetItemNotification.objects.using(db).get(item__generated_code=i.item_code)
            i.notify_me = item1.notification_days

            
            
        except SetItemNotification.DoesNotExist:
             i.notify_me = "not set"
        try:
            log = CreateStockInLog.objects.using(db).get(invoice_no=i.invoice_no, item_code=i.item_code)
            
            if log.status != "Sold":

                if i.rdays > 1 and log.status != "Unverified":
                    log.status = "Unverified"
                    log.save()
                
                if i.rdays < 1 and log.status != "Expired":
                    log.status = "Expired"
                    log.save()

            i.n_status = log.notification_status
            i.status = log.status
        
            
        except CreateStockInLog.DoesNotExist:
            i.n_status = "0"
            i.status = "Unverified"
