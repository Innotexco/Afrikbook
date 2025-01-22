from Stock.models import *
from django.db.models import Q
from datetime import datetime

# this will be in general function file
def Encountered(any,item):
   encountered_any = set()
   for i in any:
      # val = i.item
      val = getattr(i, item, None)
      if val not in encountered_any:
         encountered_any.add(val)
   return encountered_any





