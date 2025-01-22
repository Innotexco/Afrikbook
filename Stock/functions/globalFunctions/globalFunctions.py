from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,Http404;
from django.views.decorators.csrf import csrf_exempt;
import json
from datetime import datetime
from itertools import zip_longest
from decimal import Decimal


from Stock.models import *;
from  customer.models import *;
from Stock.Forms.forms import *
# from Stock.Forms.new_categoryForm import*;
from Stock.Forms.new_itemForm import*;
from Stock.Forms.stockTransferForm import*;
from Stock.Forms.StockoutForm import*;
from django.db.models import Count, F
from Stock.functions.functionHub.Stokinfunctions import *
from Stock.functions.verifyFunctions.verify import *
from Stock.utils import random_string_generator;


def Encountered(any,item):
   encountered_any = set()
   for i in any:
      # val = i.item
      val = getattr(i, item, None)
      if val not in encountered_any:
         encountered_any.add(val)
   return encountered_any

def getonedata(id, any, db):
   # get customer appear once
   
   getCusName = customer_invoice.objects.using(db).filter(invoiceID=id)
   encountered_cuzName = Encountered(getCusName, any)
   
   if encountered_cuzName:
      cusName = [({
            'data': data, 
            })
         for data in encountered_cuzName
      ]
      return cusName




# calculate ********************************************
def Calculate(id, vat_rate, db):
   getprice = customer_invoice.objects.using(db).filter(invoiceID=id);
   getsum = sum(price.amount for price in getprice)
   vat = getsum * (vat_rate / Decimal(100))
   return getsum, vat
# ***********************************************************************




# getCustomerPurchasedItems ********************************************
def getCustomerPurchasedItems(id, db):
   # get customer appear once
   getCusName = customer_invoice.objects.using(db).filter(invoiceID=id, status=0);
   if getCusName:
      items = [({
            'item_name': data.item_name, 
            'item_description': data.item_description ,
            'qty': data.qty, 
            'unit_p': data.unit_p, 
            'discount': data.discount, 
            'amount': data.amount, 
            })
         for data in getCusName
      ]
      return items
# ***********************************************************************
