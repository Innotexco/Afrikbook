from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from Stock.models import Item
from customer.models import customer_table
from .serializers import ItemSerializer, CustomerSerializer
from django.db.models import Q
from rest_framework.views import APIView
from customer.functions.customer import create_client_dtails
from rest_framework import status
from main.models import User
from django.conf import settings
import logging
import os
from Stock.models import *
from customer.views import Qty_State
from Stock.functions.functionHub.functionHub import *
import requests
import secrets
from client.models import shipping_addr
from django.db import transaction
import decimal
from customer.functions.generalFunction import *
from settings.models import shipping_cost
from customer.functions.newsalesfunc import *
from .serializers import *
from customer.models import customer_table, customer_invoice, receivable, Vat
from vendor.models import vendor_table, Vendor_invoice
from account.models import chart_of_account, account_log
from Stock.models import Item, CreateStockIn
from settings.models import shipping_cost, shipping_method
from customer.forms import CustomerSalesForm, ReceivableForm
from customer.functions.generalFunction import *
from customer.utils import generate_invoice_id
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO


DB_NAME = os.getenv("STOCK_DB_NAME")         
OUTLET_NAME = os.getenv("STOCK_OUTLET")




@api_view(['GET'])
def get_customer_invoices_api(request, customer_id):
    """
    GET endpoint to retrieve all invoices for a specific customer
    URL: /api/customers/<customer_id>/invoices/
    Query params:
        - status: filter by invoice_state (Pending, Supplied)
        - limit: number of records to return (default: all)
        - offset: pagination offset
    """
    db = DB_NAME
    
    try:
        # Get query parameters
        invoice_status = request.GET.get('status', None)
        limit = request.GET.get('limit', None)
        offset = int(request.GET.get('offset', 0))
        
        # Verify customer exists
        try:
            customer = customer_table.objects.using(db).get(id=customer_id)
            customer_code = customer.customer_code
        except customer_table.DoesNotExist:
            return Response({
                'error': 'Customer not found',
                'message': f'Customer with ID {customer_id} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all invoices for this customer (excluding returns)
        invoices_queryset = customer_invoice.objects.using(db).filter(
            cusID=customer_code
        ).exclude(
            invoiceID__icontains='returned'
        )
        
        # Filter by status if provided
        if invoice_status:
            invoices_queryset = invoices_queryset.filter(invoice_state=invoice_status)
        
        # Get unique invoice IDs
        unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
        # Order by date (newest first)
        invoices_queryset = invoices_queryset.order_by('-invoice_date')
        
        # Build response with unique invoices
        invoices_data = []
        processed_ids = set()
        
        for invoice_id in unique_invoice_ids:
            if invoice_id in processed_ids:
                continue
            
            # Get first record for this invoice (for main details)
            invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
            
            if not invoice:
                continue
            
            # Get all items for this invoice
            invoice_items = invoices_queryset.filter(invoiceID=invoice_id)
            items_count = invoice_items.count()
            
            # Determine payment method
            payment_method = get_payment_method(invoice)
            
            # Calculate balance
            balance = invoice.amount_expected - invoice.amount_paid
            is_paid = invoice.amount_paid >= invoice.amount_expected
            
            invoices_data.append({
                'invoiceID': invoice.invoiceID,
                'customer_name': invoice.customer_name,
                'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                'invoice_state': invoice.invoice_state,
                'amount_expected': str(invoice.amount_expected),
                'amount_paid': str(invoice.amount_paid),
                'balance': str(balance),
                'is_paid': is_paid,
                'items_count': items_count,
                'payment_method': payment_method,
            })
            
            processed_ids.add(invoice_id)
        
        # Apply pagination
        if limit:
            limit = int(limit)
            invoices_data = invoices_data[offset:offset + limit]
        
        return Response({
            'success': True,
            'count': len(invoices_data),
            'customer_id': customer_id,
            'customer_name': customer.name,
            'invoices': invoices_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve invoices'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_invoice_by_order_api(request, order_id):
    """
    GET endpoint to retrieve invoices for a specific order
    URL: /api/orders/<order_id>/invoices/
    """
    db = DB_NAME
    
    try:
        # Get all invoices for this order (excluding returns)
        invoices_queryset = customer_invoice.objects.using(db).filter(
            order_ID=order_id
        ).exclude(
            invoiceID__icontains='returned'
        )
        
        if not invoices_queryset.exists():
            return Response({
                'success': True,
                'count': 0,
                'invoices': []
            }, status=status.HTTP_200_OK)
        
        # Get unique invoice IDs
        unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
        # Build response
        invoices_data = []
        processed_ids = set()
        
        for invoice_id in unique_invoice_ids:
            if invoice_id in processed_ids:
                continue
            
            invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
            if not invoice:
                continue
            
            items_count = invoices_queryset.filter(invoiceID=invoice_id).count()
            payment_method = get_payment_method(invoice)
            balance = invoice.amount_expected - invoice.amount_paid
            is_paid = invoice.amount_paid >= invoice.amount_expected
            
            invoices_data.append({
                'invoiceID': invoice.invoiceID,
                'customer_name': invoice.customer_name,
                'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                'invoice_state': invoice.invoice_state,
                'amount_expected': str(invoice.amount_expected),
                'amount_paid': str(invoice.amount_paid),
                'balance': str(balance),
                'is_paid': is_paid,
                'items_count': items_count,
                'payment_method': payment_method,
            })
            
            processed_ids.add(invoice_id)
        
        return Response({
            'success': True,
            'count': len(invoices_data),
            'order_id': order_id,
            'invoices': invoices_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve invoices'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_invoice_detail_api(request, invoice_id):
    """
    GET endpoint to retrieve detailed information about a specific invoice
    URL: /api/invoices/<invoice_id>/
    No authentication required - anyone with invoice ID can view
    """
    db = DB_NAME
    
    try:
        # Get all items for this invoice
        invoice_items = customer_invoice.objects.using(db).filter(
            invoiceID=invoice_id
        ).exclude(
            invoiceID__icontains='returned'
        ).order_by('id')
        
        if not invoice_items.exists():
            return Response({
                'error': 'Invoice not found',
                'message': f'Invoice {invoice_id} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get first item for main invoice details
        invoice = invoice_items.first()
        
        # Calculate totals
        sub_total = sum(item.amount for item in invoice_items)
        total = invoice.amount_expected
        balance = invoice.amount_expected - invoice.amount_paid
        is_paid = invoice.amount_paid >= invoice.amount_expected
        
        # Determine payment method
        payment_method = get_payment_method(invoice)
        
        # Build invoice data
        invoice_data = {
            'invoiceID': invoice.invoiceID,
            'cusID': invoice.cusID,
            'customer_name': invoice.customer_name,
            'order_ID': invoice.order_ID,
            'Gdescription': invoice.Gdescription,
            'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'invoice_state': invoice.invoice_state,
            'amount_paid': str(invoice.amount_paid),
            'amount_expected': str(invoice.amount_expected),
            'cancellation_status': invoice.cancellation_status,
            'status': invoice.status,
            'outlet': invoice.outlet,
            'Userlogin': invoice.Userlogin,
            'payment_method': payment_method,
            'sub_total': str(sub_total),
            'vat_amount': '0.00',  # Calculate if you have VAT table
            'total_amount': str(total),
            'balance': str(balance),
            'is_paid': is_paid,
            'items': []
        }
        
        # Add items
        for item in invoice_items:
            invoice_data['items'].append({
                'id': item.id,
                'itemcode': item.itemcode,
                'item_name': item.item_name,
                'item_description': item.item_description or '',
                'qty': str(item.qty),
                'unit_p': str(item.unit_p),
                'discount': str(item.discount or 0),
                'amount': str(item.amount),
                'purchaseP': str(item.purchaseP)
            })
        
        return Response({
            'success': True,
            'invoice': invoice_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve invoice details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
def get_customer_invoice_summary_api(request, customer_id):
    """
    GET endpoint to retrieve invoice summary/statistics for a customer
    URL: /api/customers/<customer_id>/invoices/summary/
    """
    db = DB_NAME
    
    try:
        # Verify customer exists
        try:
            customer = customer_table.objects.using(db).get(id=customer_id)
            customer_code = customer.customer_code
        except customer_table.DoesNotExist:
            return Response({
                'error': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all invoices for customer (excluding returns)
        invoices_queryset = customer_invoice.objects.using(db).filter(
            cusID=customer_code
        ).exclude(
            invoiceID__icontains='returned'
        )
        
        # Get unique invoice IDs
        unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
        # Initialize counters
        total_invoices = len(unique_invoice_ids)
        total_amount = Decimal('0.00')
        paid_amount = Decimal('0.00')
        pending_count = 0
        supplied_count = 0
        
        # Process each unique invoice
        processed_ids = set()
        for invoice_id in unique_invoice_ids:
            if invoice_id in processed_ids:
                continue
            
            # Get first record for totals
            invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
            
            if invoice:
                total_amount += invoice.amount_expected
                paid_amount += invoice.amount_paid
                
                if invoice.invoice_state == 'Pending':
                    pending_count += 1
                elif invoice.invoice_state == 'Supplied':
                    supplied_count += 1
                
                processed_ids.add(invoice_id)
        
        outstanding_amount = total_amount - paid_amount
        
        summary = {
            'customer_id': customer_id,
            'customer_name': customer.name,
            'total_invoices': total_invoices,
            'total_amount': str(total_amount),
            'paid_amount': str(paid_amount),
            'outstanding_amount': str(outstanding_amount),
            'pending_invoices': pending_count,
            'supplied_invoices': supplied_count
        }
        
        return Response({
            'success': True,
            'summary': summary
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve invoice summary'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_invoice_api(request):
    """
    GET endpoint to search for invoices
    URL: /api/invoices/search/?q=<search_term>
    Query params:
        - q: search term (invoice ID, customer name, order ID)
    """
    db = DB_NAME
    
    try:
        search_term = request.GET.get('q', '').strip()
        
        if not search_term:
            return Response({
                'error': 'Search term required',
                'message': 'Please provide a search term using ?q=<search_term>'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in invoices (excluding returns)
        invoices_queryset = customer_invoice.objects.using(db).filter(
            Q(invoiceID__icontains=search_term) |
            Q(customer_name__icontains=search_term) |
            Q(order_ID__icontains=search_term)
        ).exclude(
            invoiceID__icontains='returned'
        ).order_by('-invoice_date')
        
        # Get unique invoice IDs
        unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
        # Build response
        invoices_data = []
        processed_ids = set()
        
        for invoice_id in unique_invoice_ids:
            if invoice_id in processed_ids:
                continue
            
            invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
            if not invoice:
                continue
            
            items_count = invoices_queryset.filter(invoiceID=invoice_id).count()
            payment_method = get_payment_method(invoice)
            balance = invoice.amount_expected - invoice.amount_paid
            is_paid = invoice.amount_paid >= invoice.amount_expected
            
            invoices_data.append({
                'invoiceID': invoice.invoiceID,
                'customer_name': invoice.customer_name,
                'order_ID': invoice.order_ID,
                'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                'invoice_state': invoice.invoice_state,
                'amount_expected': str(invoice.amount_expected),
                'amount_paid': str(invoice.amount_paid),
                'balance': str(balance),
                'is_paid': is_paid,
                'items_count': items_count,
                'payment_method': payment_method,
            })
            
            processed_ids.add(invoice_id)
        
        return Response({
            'success': True,
            'count': len(invoices_data),
            'search_term': search_term,
            'invoices': invoices_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to search invoices'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_payment_method(invoice):
    """
    Helper function to determine payment method from flags
    """
    if invoice.Transfer == "1":
        return "Transfer"
    elif invoice.POS == "1":
        return "POS"
    elif invoice.Cash == "1":
        return "Cash"
    elif invoice.Customer_account == "1":
        return "Customer Account"
    elif invoice.Cheque == "1":
        return "Cheque"
    elif invoice.payment_method:
        return invoice.payment_method
    return "Unknown"




# @api_view(['GET'])
# def get_customer_invoices_api(request, customer_id):
#     """
#     GET endpoint to retrieve all invoices for a specific customer
#     URL: /api/customers/<customer_id>/invoices/
#     Query params:
#         - status: filter by invoice_state (Pending, Supplied)
#         - limit: number of records to return (default: all)
#         - offset: pagination offset
#     """
#     db = DB_NAME
    
#     try:
#         # Get query parameters
#         invoice_status = request.GET.get('status', None)
#         limit = request.GET.get('limit', None)
#         offset = int(request.GET.get('offset', 0))
        
#         # Verify customer exists
#         try:
#             customer = customer_table.objects.using(db).get(id=customer_id)
#             customer_code = customer.customer_code
#         except customer_table.DoesNotExist:
#             return Response({
#                 'error': 'Customer not found',
#                 'message': f'Customer with ID {customer_id} does not exist'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         # Get all invoices for this customer (excluding returns)
#         invoices_queryset = customer_invoice.objects.using(db).filter(
#             cusID=customer_code
#         ).exclude(
#             invoiceID__icontains='returned'
#         )
        
#         # Filter by status if provided
#         if invoice_status:
#             invoices_queryset = invoices_queryset.filter(invoice_state=invoice_status)
        
#         # Get unique invoice IDs
#         unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
#         # Order by date (newest first)
#         invoices_queryset = invoices_queryset.order_by('-invoice_date')
        
#         # Build response with unique invoices
#         invoices_data = []
#         processed_ids = set()
        
#         for invoice_id in unique_invoice_ids:
#             if invoice_id in processed_ids:
#                 continue
            
#             # Get first record for this invoice (for main details)
#             invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
            
#             if not invoice:
#                 continue
            
#             # Get all items for this invoice
#             invoice_items = invoices_queryset.filter(invoiceID=invoice_id)
#             items_count = invoice_items.count()
            
#             # Determine payment method
#             payment_method = get_payment_method(invoice)
            
#             # Calculate balance
#             balance = invoice.amount_expected - invoice.amount_paid
#             is_paid = invoice.amount_paid >= invoice.amount_expected
            
#             invoices_data.append({
#                 'invoiceID': invoice.invoiceID,
#                 'customer_name': invoice.customer_name,
#                 'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
#                 'invoice_state': invoice.invoice_state,
#                 'amount_expected': str(invoice.amount_expected),
#                 'amount_paid': str(invoice.amount_paid),
#                 'balance': str(balance),
#                 'is_paid': is_paid,
#                 'items_count': items_count,
#                 'payment_method': payment_method,
#             })
            
#             processed_ids.add(invoice_id)
        
#         # Apply pagination
#         if limit:
#             limit = int(limit)
#             invoices_data = invoices_data[offset:offset + limit]
        
#         return Response({
#             'success': True,
#             'count': len(invoices_data),
#             'customer_id': customer_id,
#             'customer_name': customer.name,
#             'invoices': invoices_data
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         return Response({
#             'error': str(e),
#             'message': 'Failed to retrieve invoices'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def get_invoice_by_order_api(request, order_id):
#     """
#     GET endpoint to retrieve invoices for a specific order
#     URL: /api/orders/<order_id>/invoices/
#     """
#     db = DB_NAME
    
#     try:
#         # Get all invoices for this order (excluding returns)
#         invoices_queryset = customer_invoice.objects.using(db).filter(
#             order_ID=order_id
#         ).exclude(
#             invoiceID__icontains='returned'
#         )
        
#         if not invoices_queryset.exists():
#             return Response({
#                 'success': True,
#                 'count': 0,
#                 'invoices': []
#             }, status=status.HTTP_200_OK)
        
#         # Get unique invoice IDs
#         unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
#         # Build response
#         invoices_data = []
#         processed_ids = set()
        
#         for invoice_id in unique_invoice_ids:
#             if invoice_id in processed_ids:
#                 continue
            
#             invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
#             if not invoice:
#                 continue
            
#             items_count = invoices_queryset.filter(invoiceID=invoice_id).count()
#             payment_method = get_payment_method(invoice)
#             balance = invoice.amount_expected - invoice.amount_paid
#             is_paid = invoice.amount_paid >= invoice.amount_expected
            
#             invoices_data.append({
#                 'invoiceID': invoice.invoiceID,
#                 'customer_name': invoice.customer_name,
#                 'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
#                 'invoice_state': invoice.invoice_state,
#                 'amount_expected': str(invoice.amount_expected),
#                 'amount_paid': str(invoice.amount_paid),
#                 'balance': str(balance),
#                 'is_paid': is_paid,
#                 'items_count': items_count,
#                 'payment_method': payment_method,
#             })
            
#             processed_ids.add(invoice_id)
        
#         return Response({
#             'success': True,
#             'count': len(invoices_data),
#             'order_id': order_id,
#             'invoices': invoices_data
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         return Response({
#             'error': str(e),
#             'message': 'Failed to retrieve invoices'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def get_invoice_detail_api(request, invoice_id):
#     """
#     GET endpoint to retrieve detailed information about a specific invoice
#     URL: /api/invoices/<invoice_id>/
#     No authentication required - anyone with invoice ID can view
#     """
#     db = DB_NAME
    
#     try:
#         # Get all items for this invoice
#         invoice_items = customer_invoice.objects.using(db).filter(
#             invoiceID=invoice_id
#         ).exclude(
#             invoiceID__icontains='returned'
#         ).order_by('id')
        
#         if not invoice_items.exists():
#             return Response({
#                 'error': 'Invoice not found',
#                 'message': f'Invoice {invoice_id} does not exist'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         # Get first item for main invoice details
#         invoice = invoice_items.first()
        
#         # Calculate totals
#         sub_total = sum(item.amount for item in invoice_items)
#         total = invoice.amount_expected
#         balance = invoice.amount_expected - invoice.amount_paid
#         is_paid = invoice.amount_paid >= invoice.amount_expected
        
#         # Determine payment method
#         payment_method = get_payment_method(invoice)
        
#         # Build invoice data
#         invoice_data = {
#             'invoiceID': invoice.invoiceID,
#             'cusID': invoice.cusID,
#             'customer_name': invoice.customer_name,
#             'order_ID': invoice.order_ID,
#             'Gdescription': invoice.Gdescription,
#             'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
#             'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
#             'invoice_state': invoice.invoice_state,
#             'amount_paid': str(invoice.amount_paid),
#             'amount_expected': str(invoice.amount_expected),
#             'cancellation_status': invoice.cancellation_status,
#             'status': invoice.status,
#             'outlet': invoice.outlet,
#             'Userlogin': invoice.Userlogin,
#             'payment_method': payment_method,
#             'sub_total': str(sub_total),
#             'vat_amount': '0.00',  # Calculate if you have VAT table
#             'total_amount': str(total),
#             'balance': str(balance),
#             'is_paid': is_paid,
#             'items': []
#         }
        
#         # Add items
#         for item in invoice_items:
#             invoice_data['items'].append({
#                 'id': item.id,
#                 'itemcode': item.itemcode,
#                 'item_name': item.item_name,
#                 'item_description': item.item_description or '',
#                 'qty': str(item.qty),
#                 'unit_p': str(item.unit_p),
#                 'discount': str(item.discount or 0),
#                 'amount': str(item.amount),
#                 'purchaseP': str(item.purchaseP)
#             })
        
#         return Response({
#             'success': True,
#             'invoice': invoice_data
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         return Response({
#             'error': str(e),
#             'message': 'Failed to retrieve invoice details'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def get_customer_invoice_summary_api(request, customer_id):
#     """
#     GET endpoint to retrieve invoice summary/statistics for a customer
#     URL: /api/customers/<customer_id>/invoices/summary/
#     """
#     db = DB_NAME
    
#     try:
#         # Verify customer exists
#         try:
#             customer = customer_table.objects.using(db).get(id=customer_id)
#             customer_code = customer.customer_code
#         except customer_table.DoesNotExist:
#             return Response({
#                 'error': 'Customer not found'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         # Get all invoices for customer (excluding returns)
#         invoices_queryset = customer_invoice.objects.using(db).filter(
#             cusID=customer_code
#         ).exclude(
#             invoiceID__icontains='returned'
#         )
        
#         # Get unique invoice IDs
#         unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
#         # Initialize counters
#         total_invoices = len(unique_invoice_ids)
#         total_amount = Decimal('0.00')
#         paid_amount = Decimal('0.00')
#         pending_count = 0
#         supplied_count = 0
        
#         # Process each unique invoice
#         processed_ids = set()
#         for invoice_id in unique_invoice_ids:
#             if invoice_id in processed_ids:
#                 continue
            
#             # Get first record for totals
#             invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
            
#             if invoice:
#                 total_amount += invoice.amount_expected
#                 paid_amount += invoice.amount_paid
                
#                 if invoice.invoice_state == 'Pending':
#                     pending_count += 1
#                 elif invoice.invoice_state == 'Supplied':
#                     supplied_count += 1
                
#                 processed_ids.add(invoice_id)
        
#         outstanding_amount = total_amount - paid_amount
        
#         summary = {
#             'customer_id': customer_id,
#             'customer_name': customer.name,
#             'total_invoices': total_invoices,
#             'total_amount': str(total_amount),
#             'paid_amount': str(paid_amount),
#             'outstanding_amount': str(outstanding_amount),
#             'pending_invoices': pending_count,
#             'supplied_invoices': supplied_count
#         }
        
#         return Response({
#             'success': True,
#             'summary': summary
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         return Response({
#             'error': str(e),
#             'message': 'Failed to retrieve invoice summary'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# def search_invoice_api(request):
#     """
#     GET endpoint to search for invoices
#     URL: /api/invoices/search/?q=<search_term>
#     Query params:
#         - q: search term (invoice ID, customer name, order ID)
#     """
#     db = DB_NAME
    
#     try:
#         search_term = request.GET.get('q', '').strip()
        
#         if not search_term:
#             return Response({
#                 'error': 'Search term required',
#                 'message': 'Please provide a search term using ?q=<search_term>'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         # Search in invoices (excluding returns)
#         invoices_queryset = customer_invoice.objects.using(db).filter(
#             Q(invoiceID__icontains=search_term) |
#             Q(customer_name__icontains=search_term) |
#             Q(order_ID__icontains=search_term)
#         ).exclude(
#             invoiceID__icontains='returned'
#         ).order_by('-invoice_date')
        
#         # Get unique invoice IDs
#         unique_invoice_ids = list(invoices_queryset.values_list('invoiceID', flat=True).distinct())
        
#         # Build response
#         invoices_data = []
#         processed_ids = set()
        
#         for invoice_id in unique_invoice_ids:
#             if invoice_id in processed_ids:
#                 continue
            
#             invoice = invoices_queryset.filter(invoiceID=invoice_id).first()
#             if not invoice:
#                 continue
            
#             items_count = invoices_queryset.filter(invoiceID=invoice_id).count()
#             payment_method = get_payment_method(invoice)
#             balance = invoice.amount_expected - invoice.amount_paid
#             is_paid = invoice.amount_paid >= invoice.amount_expected
            
#             invoices_data.append({
#                 'invoiceID': invoice.invoiceID,
#                 'customer_name': invoice.customer_name,
#                 'order_ID': invoice.order_ID,
#                 'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
#                 'invoice_state': invoice.invoice_state,
#                 'amount_expected': str(invoice.amount_expected),
#                 'amount_paid': str(invoice.amount_paid),
#                 'balance': str(balance),
#                 'is_paid': is_paid,
#                 'items_count': items_count,
#                 'payment_method': payment_method,
#             })
            
#             processed_ids.add(invoice_id)
        
#         return Response({
#             'success': True,
#             'count': len(invoices_data),
#             'search_term': search_term,
#             'invoices': invoices_data
#         }, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         return Response({
#             'error': str(e),
#             'message': 'Failed to search invoices'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def get_payment_method(invoice):
#     """
#     Helper function to determine payment method from flags
#     """
#     if invoice.Transfer == "1":
#         return "Transfer"
#     elif invoice.POS == "1":
#         return "POS"
#     elif invoice.Cash == "1":
#         return "Cash"
#     elif invoice.Customer_account == "1":
#         return "Customer Account"
#     elif invoice.Cheque == "1":
#         return "Cheque"
#     elif invoice.payment_method:
#         return invoice.payment_method
#     return "Unknown"


@api_view(['GET'])
def download_invoice_pdf_api(request, invoice_id):
    """
    GET endpoint to generate and download a professional invoice as PDF
    No authentication required
    URL: /api/invoices/<invoice_id>/download/
    """
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.colors import HexColor
    from io import BytesIO
    from datetime import datetime
    
    db = DB_NAME
    
    try:
        # Get all items for this invoice
        invoice_items = customer_invoice.objects.using(db).filter(
            invoiceID=invoice_id
        ).exclude(
            invoiceID__icontains='returned'
        ).order_by('id')
        
        if not invoice_items.exists():
            return Response({
                'error': 'Invoice not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get first item for main invoice details
        invoice = invoice_items.first()
        
        # Calculate totals
        sub_total = sum(item.amount for item in invoice_items)
        balance = invoice.amount_expected - invoice.amount_paid
        is_paid = invoice.amount_paid >= invoice.amount_expected
        
        # Prepare PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Define colors
        primary_color = HexColor('#059669')  # Forest green
        dark_gray = HexColor('#374151')
        light_gray = HexColor('#f3f4f6')
        medium_gray = HexColor('#6b7280')
        success_color = HexColor('#10b981')
        danger_color = HexColor('#ef4444')
        
        # ==================== HEADER SECTION ====================
        y_position = height - 40
        
        # Top border accent
        p.setFillColor(primary_color)
        p.rect(0, height - 10, width, 10, fill=1, stroke=0)
        
        # Company name and logo area
        p.setFillColor(dark_gray)
        p.setFont("Helvetica-Bold", 24)
        p.drawString(40, y_position, "EMEM ENERGY")
        y_position -= 22
        p.setFont("Helvetica-Bold", 24)
        p.drawString(40, y_position, "TECH.")
        
        # Invoice label on the right
        p.setFillColor(primary_color)
        p.setFont("Helvetica-Bold", 32)
        p.drawRightString(width - 40, height - 50, "INVOICE")
        
        y_position -= 30
        
        # Company details
        p.setFillColor(medium_gray)
        p.setFont("Helvetica", 9)
        p.drawString(40, y_position, "14 Dennis Osadebe Way")
        y_position -= 12
        p.drawString(40, y_position, "Asaba, Delta State")
        y_position -= 12
        p.drawString(40, y_position, "Nigeria")
        y_position -= 12
        p.drawString(40, y_position, "contact@solarbattery.com")
        
        # Invoice number and status on right
        y_pos_right = height - 95
        p.setFillColor(dark_gray)
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(width - 40, y_pos_right, "Invoice Number")
        y_pos_right -= 15
        p.setFont("Helvetica", 11)
        p.drawRightString(width - 40, y_pos_right, invoice.invoiceID)
        
        y_pos_right -= 25
        
        # Status badge
        if is_paid:
            p.setFillColor(success_color)
            p.roundRect(width - 140, y_pos_right - 8, 100, 20, 4, fill=1, stroke=0)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 9)
            p.drawCentredString(width - 90, y_pos_right - 2, "PAID IN FULL")
        else:
            p.setFillColor(danger_color)
            p.roundRect(width - 160, y_pos_right - 8, 120, 20, 4, fill=1, stroke=0)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 9)
            p.drawCentredString(width - 100, y_pos_right - 2, "PAYMENT CANCELLED")
        
        y_position = height - 210
        
        # Divider line
        p.setStrokeColor(light_gray)
        p.setLineWidth(1)
        p.line(40, y_position, width - 40, y_position)
        y_position -= 30
        
        # ==================== BILL TO / INVOICE DETAILS ====================
        
        # Left section - Bill To
        left_col_x = 40
        p.setFillColor(medium_gray)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(left_col_x, y_position, "BILL TO")
        y_position -= 15
        
        p.setFillColor(dark_gray)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(left_col_x, y_position, invoice.customer_name or "N/A")
        y_position -= 14
        
        p.setFont("Helvetica", 9)
        p.setFillColor(medium_gray)
        p.drawString(left_col_x, y_position, f"Customer ID: {invoice.cusID}")
        y_position -= 12
        p.drawString(left_col_x, y_position, f"Order ID: {invoice.order_ID or 'N/A'}")
        
        if invoice.Gdescription:
            y_position -= 14
            p.setFont("Helvetica-Oblique", 8)
            # Wrap description if too long
            desc = invoice.Gdescription[:60] + "..." if len(invoice.Gdescription) > 60 else invoice.Gdescription
            p.drawString(left_col_x, y_position, desc)
        
        # Right section - Invoice Details
        right_col_x = width / 2 + 20
        y_pos_right = height - 240
        
        # Create details box
        box_width = width - right_col_x - 40
        box_height = 90
        p.setFillColor(light_gray)
        p.roundRect(right_col_x, y_pos_right - box_height, box_width, box_height, 6, fill=1, stroke=0)
        
        # Details content
        y_detail = y_pos_right - 20
        p.setFillColor(medium_gray)
        p.setFont("Helvetica-Bold", 8)
        
        # Invoice Date
        p.drawString(right_col_x + 15, y_detail, "INVOICE DATE")
        p.setFont("Helvetica", 9)
        p.setFillColor(dark_gray)
        p.drawString(right_col_x + 15, y_detail - 12, invoice.invoice_date.strftime('%b %d, %Y'))
        
        y_detail -= 30
        
        # Due Date
        p.setFillColor(medium_gray)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(right_col_x + 15, y_detail, "DUE DATE")
        p.setFont("Helvetica", 9)
        p.setFillColor(dark_gray)
        p.drawString(right_col_x + 15, y_detail - 12, invoice.due_date.strftime('%b %d, %Y'))
        
        y_detail -= 30
        
        # Outlet
        p.setFillColor(medium_gray)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(right_col_x + 15, y_detail, "OUTLET")
        p.setFont("Helvetica", 9)
        p.setFillColor(dark_gray)
        p.drawString(right_col_x + 15, y_detail - 12, invoice.outlet or "Main Store")
        
        y_position = y_pos_right - box_height - 30
        
        # ==================== ITEMS TABLE ====================
        
        p.setFillColor(dark_gray)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, y_position, "ITEMS & SERVICES")
        y_position -= 20
        
        # Prepare table data
        table_data = [
            ['Description', 'Qty', 'Unit Price', 'Discount', 'Amount']
        ]
        
        for item in invoice_items:
            item_name = item.item_name[:35] + "..." if len(item.item_name) > 35 else item.item_name
            discount_val = float(item.discount or 0)
            
            table_data.append([
                f"{item_name}\nCode: {item.itemcode}",
                str(int(float(item.qty))),
                f"₦{float(item.unit_p):,.2f}",
                f"₦{discount_val:,.2f}" if discount_val > 0 else "-",
                f"₦{float(item.amount):,.2f}"
            ])
        
        # Create and style table
        col_widths = [220, 50, 90, 80, 90]
        table = Table(table_data, colWidths=col_widths)
        
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            
            # Grid
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, HexColor('#e5e7eb')),
            ('LINEBELOW', (0, -1), (-1, -1), 1, primary_color),
            
            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f9fafb')]),
            
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        table.setStyle(table_style)
        
        # Draw table
        table_width, table_height = table.wrap(width - 80, height)
        table.drawOn(p, 40, y_position - table_height)
        y_position -= (table_height + 25)
        
        # ==================== TOTALS SECTION ====================
        
        # Totals box
        totals_x = width - 260
        totals_width = 220
        
        # Background box
        p.setFillColor(light_gray)
        p.roundRect(totals_x - 15, y_position - 135, totals_width, 130, 6, fill=1, stroke=0)
        
        y_position -= 20
        
        # Subtotal
        p.setFillColor(medium_gray)
        p.setFont("Helvetica", 9)
        p.drawString(totals_x, y_position, "Subtotal")
        p.setFillColor(dark_gray)
        p.drawRightString(width - 55, y_position, f"₦{sub_total:,.2f}")
        y_position -= 18
        
        # VAT
        p.setFillColor(medium_gray)
        p.drawString(totals_x, y_position, "VAT (7.5%)")
        p.setFillColor(dark_gray)
        p.drawRightString(width - 55, y_position, "₦0.00")
        y_position -= 18
        
        # Shipping
        p.setFillColor(medium_gray)
        p.drawString(totals_x, y_position, "Shipping")
        p.setFillColor(dark_gray)
        p.drawRightString(width - 55, y_position, "₦0.00")
        y_position -= 25
        
        # Divider
        p.setStrokeColor(medium_gray)
        p.setLineWidth(0.5)
        p.line(totals_x, y_position, width - 55, y_position)
        y_position -= 18
        
        # Total
        p.setFillColor(dark_gray)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(totals_x, y_position, "Total Amount")
        p.drawRightString(width - 55, y_position, f"₦{float(invoice.amount_expected):,.2f}")
        y_position -= 20
        
        # Amount Paid
        amount_paid = float(invoice.amount_paid)
        if amount_paid > 0:
            p.setFillColor(success_color)
            p.setFont("Helvetica", 9)
            p.drawString(totals_x, y_position, "Amount Paid")
            p.drawRightString(width - 55, y_position, f"₦{amount_paid:,.2f}")
            y_position -= 20
        
        # Balance Due
        if balance > 0:
            p.setFillColor(danger_color)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(totals_x, y_position, "Balance Due")
            p.drawRightString(width - 55, y_position, f"₦{balance:,.2f}")
        
        # ==================== FOOTER ====================
        
        # Move to footer area
        footer_y = 100
        
        # Divider
        p.setStrokeColor(light_gray)
        p.setLineWidth(0.5)
        p.line(40, footer_y + 40, width - 40, footer_y + 40)
        
        # Footer text
        p.setFillColor(medium_gray)
        p.setFont("Helvetica-Oblique", 8)
        p.drawCentredString(width / 2, footer_y + 20, "Thank you for your business!")
        
        p.setFont("Helvetica", 8)
        p.drawCentredString(width / 2, footer_y + 5, "For any inquiries, please contact us at contact@solarbattery.com")
        
        # Powered by
        p.setFont("Helvetica", 7)
        p.setFillColor(medium_gray)
        powered_text = "Powered by AFRIKBOOK"
        text_width = p.stringWidth(powered_text, "Helvetica", 7)
        x_centered = (width - text_width) / 2
        p.drawString(x_centered, footer_y - 15, powered_text)
        
        # Make it clickable
        p.linkURL("https://afrikbook.com", 
                  (x_centered, footer_y - 18, x_centered + text_width, footer_y - 10), 
                  relative=0)
        
        # Generation timestamp (bottom right)
        p.setFont("Helvetica", 6)
        p.setFillColor(HexColor('#9ca3af'))
        gen_timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        p.drawRightString(width - 40, 30, f"Generated: {gen_timestamp}")
        
        # Page number (bottom left)
        p.drawString(40, 30, "Page 1 of 1")
        
        # Finish PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        # Send PDF as downloadable response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        
        return response
    
    except Exception as e:
        import traceback
        print(f"Error generating PDF: {str(e)}")
        print(traceback.format_exc())
        return Response({
            'error': str(e),
            'message': 'Failed to generate PDF'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def billing_shipping_reference(db, invoice, cusID, shipping, method, cost):
    
    try:
        order_invoice_reference_address.objects.using(db).get(reference=invoice)
    except order_invoice_reference_address.DoesNotExist:
        order_invoice_reference_address.objects.using(db).create(source=method, reference=invoice, shipping_addr=shipping) 
   # order_invoice_billing_address.objects.using(db).create(source="", reference=invoice, billing_addr=billing) 
        
    try:
       shipping_cost.objects.using(db).get(invoiceID=invoice)
    except shipping_cost.DoesNotExist:
        shipping_cost.objects.using(db).create(invoiceID=invoice, amount=cost, custID=cusID)


@api_view(['GET'])
def sales_invoice_initial_data(request):
    """
    GET endpoint to retrieve initial data needed for sales invoice creation
    Returns customers, vendors, items, accounts, and shipping methods
    """
    db = DB_NAME
    
    try:
        # Get all required data
        customers = customer_table.objects.using(db).all()
        vendors = vendor_table.objects.using(db).all()
        items = Item.objects.using(db).all()
        accounts = chart_of_account.objects.using(db).all()
        methods = shipping_method.objects.using(db).all()
        
        # Generate new invoice ID
        invoice_id = generate_invoice_id()
        
        # Serialize data
        data = {
            'customers': CustomerSerializer(customers, many=True).data,
            'vendors': VendorSerializer(vendors, many=True).data,
            'items': ItemSerializer(items, many=True).data,
            'accounts': ChartOfAccountSerializer(accounts, many=True).data,
            'shipping_methods': ShippingMethodSerializer(methods, many=True).data,
            'generated_invoice_id': invoice_id,
            'company': {
                'name': request.user.company_id.company_name,
                'db_name': db
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve initial data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_sales_invoice_api(request):
    """
    POST endpoint to create a new sales invoice
    Validates data and processes invoice creation with stock reduction
    """
    db = DB_NAME
    
    # Check if user has outlet assigned
    if not OUTLET_NAME:
        return Response({
            'error': 'User has no outlet assigned',
            'message': 'Please assign an outlet to the logged-in user'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate input data
    serializer = SalesInvoiceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'error': 'Invalid input data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        with transaction.atomic():
            # Extract main invoice data
            cusID = validated_data.get('cusID')
            venID = validated_data.get('venID')
            accountType = validated_data['accountType']
            customer_name = validated_data['customer_name']
            invoice_date = validated_data['invoice_date']
            due_date = invoice_date
            invoiceID = validated_data['invoiceID']
            order_id = validated_data.get('order_id', '')
            Gdescription = validated_data.get('Gdescription', '')
            invoice_state_bool = validated_data.get('invoice_state', False)
            credit_sales = validated_data.get('credit_sales', False)
            payment_method = validated_data.get('payment_method', 'Cash')
            method = validated_data.get('shipping_method', '')
            shipping = validated_data.get('shipping_address', '')
            shipping_cost_value = validated_data.get('shipping_cost', Decimal('0'))
            vat = validated_data.get('vat', Decimal('0'))
            sub_total = validated_data['sub_total']
            total = validated_data['total']
            items = validated_data['items']
            account_ID = validated_data.get('t_account')
            transfer = validated_data.get('transfer_amount', Decimal('0'))
            cash_amount = validated_data.get('cash_amount', Decimal('0'))
            
            # Convert invoice_date to datetime
            current_time = datetime.now().time()
            date_time = datetime.combine(invoice_date, current_time)
            
            # Determine invoice state
            instant_stockout = request.session.get('IN_STOCKOUT', 'Yes')
            status_flag = 1 if instant_stockout == "Yes" else 0
            invoice_state = "Pending" if invoice_state_bool else "Supplied"
            
            # Determine amount paid
            if credit_sales:
                amount_paid = Decimal('0.00')
                amount_expected = total
            else:
                amount_paid = total
                amount_expected = total
            
            # Get customer or vendor
            if cusID:
                customer = customer_table.objects.using(db).get(id=cusID)
                customer_code = customer.customer_code
            elif venID:
                vendor = vendor_table.objects.using(db).get(id=venID)
                customer_code = vendor.custID
            else:
                return Response({
                    'error': 'Customer or Vendor ID required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate total purchase price
            total_purchaseP = sum(
                Decimal(item['purchaseP']) for item in items
            )
            
            # Process each item
            for item_data in items:
                itemcode = item_data['itemcode']
                qty = item_data['qty']
                
                # Skip invalid items
                if not itemcode or itemcode == "0":
                    continue
                
                # Ensure quantity is at least 1
                if qty <= 0:
                    qty = 1
                
                # Prepare form data
                form_data = {
                    'cusID': customer_code,
                    'customer_name': customer_name,
                    'invoice_date': date_time,
                    'due_date': due_date,
                    'invoiceID': invoiceID,
                    'order_ID': order_id,
                    'Gdescription': Gdescription,
                    'item_name': item_data['item_name'],
                    'itemcode': itemcode,
                    'item_description': item_data.get('item_description', ''),
                    'qty': qty,
                    'unit_p': item_data['unit'],
                    'discount': item_data.get('discount', 0),
                    'amount': item_data['amount'],
                    'amount_paid': amount_paid,
                    'amount_expected': amount_expected,
                    'cancellation_status': 0,
                    'status': status_flag,
                    'Transfer': 0,
                    'POS': 0,
                    'Cash': 0,
                    'Customer_account': 0,
                    'Cheque': 0,
                    'invoice_state': invoice_state,
                    'purchaseP': item_data['purchaseP'],
                    'total_purchaseP': total_purchaseP,
                    'outlet': OUTLET_NAME
                }
                
                # Create customer sales form
                cus_form = CustomerSalesForm(form_data)
                
                if not cus_form.is_valid():
                    return Response({
                        'error': 'Invalid form data',
                        'details': cus_form.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Save invoice item
                form = cus_form.save(commit=False)
                form.Userlogin = request.user.username
                form.save(using=db)
                
                # Reduce stock if invoice is supplied
                if invoice_state == "Supplied":
                    outlet = OUTLET_NAME
                    ReduceOutletStockinItemQuantity(db, outlet, itemcode, qty)
            
            # Update customer/vendor invoice count
            if accountType == "Customer":
                customer.invoice = customer.invoice + 1
                customer.save(using=db)
            elif accountType == "Vendor":
                vendor.invoices = int(vendor.invoices) + 1
                vendor.save(using=db)
            
            # Handle receivable/payable entries
            if not credit_sales:
                if account_ID:
                    account = chart_of_account.objects.using(db).get(account_id=account_ID)
                    
                    if accountType == "Customer":
                        DebitReceivable(request, db, customer, invoice_date, Gdescription, payment_method, account_ID, total)
                    elif accountType == "Vendor":
                        DebitPayable(request, db, vendor, invoice_date, Gdescription, payment_method, account_ID, total)
                    
                    if payment_method == "Transfer":
                        if accountType == "Customer":
                            CreditReceivable(request, db, customer, invoice_date, Gdescription, payment_method, account_ID, total)
                        elif accountType == "Vendor":
                            CreditPayable(request, db, vendor, invoice_date, Gdescription, payment_method, account_ID, total)
                        CreateLog(db, account, total)
                    
                    elif payment_method == "Transfer and Cash":
                        # Transfer
                        if accountType == "Customer":
                            CreditReceivable(request, db, customer, invoice_date, Gdescription, "Transfer", account_ID, transfer)
                        elif accountType == "Vendor":
                            CreditPayable(request, db, vendor, invoice_date, Gdescription, "Transfer", account_ID, transfer)
                        CreateLog(db, account, transfer)
                        
                        # Cash
                        cash_account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                        if accountType == "Customer":
                            CreditReceivable(request, db, customer, invoice_date, Gdescription, "Cash", cash_account.account_id, cash_amount)
                        elif accountType == "Vendor":
                            CreditPayable(request, db, vendor, invoice_date, Gdescription, "Cash", cash_account.account_id, cash_amount)
                        CreateLog(db, cash_account, cash_amount)
                    
                    elif payment_method == "Cheque":
                        account = chart_of_account.objects.using(db).get(account_bankname="Account Receivable")
                        CreateLog(db, account, total)
                    
                    else:
                        account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                        if accountType == "Customer":
                            CreditReceivable(request, db, customer, invoice_date, Gdescription, payment_method, account.account_id, total)
                        elif accountType == "Vendor":
                            CreditPayable(request, db, vendor, invoice_date, Gdescription, payment_method, account.account_id, total)
                        CreateLog(db, account, total)
                
                else:
                    account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                    if accountType == "Customer":
                        DebitReceivable(request, db, customer, invoice_date, Gdescription, payment_method, account.account_id, total)
                        CreditReceivable(request, db, customer, invoice_date, Gdescription, payment_method, account.account_id, total)
                    elif accountType == "Vendor":
                        DebitPayable(request, db, vendor, invoice_date, Gdescription, payment_method, account.account_id, total)
                        CreditPayable(request, db, vendor, invoice_date, Gdescription, payment_method, account.account_id, total)
                    CreateLog(db, account, total)
            
            else:
                # Credit sales
                if accountType == "Customer":
                    account = chart_of_account.objects.using(db).get(account_bankname="Sales Account")
                    account.actual_balance += Decimal(total)
                    DebitReceivable(request, db, customer, invoice_date, Gdescription, payment_method, account.account_id, total)
                elif accountType == "Vendor":
                    account = chart_of_account.objects.using(db).get(account_bankname="Purchase Account")
                    account.actual_balance += Decimal(total)
                    DebitPayable(request, db, vendor, invoice_date, Gdescription, payment_method, account.account_id, total)
                CreateLog(db, account, total)
            
            # Create account log
            acc_log = account_log(
                transaction_source="Sales",
                amount=total,
                date=invoice_date,
                account=account.account_id,
                account_type=account.account_type,
                Userlogin=request.user.username
            )
            acc_log.save(using=db)
            
            # Handle shipping/billing reference
            if shipping and method:
                billing_shipping_reference(db, invoiceID, cusID, shipping, method, shipping_cost_value)
            
            # Create VAT record
            create_add_vat(db, invoiceID, vat)
            
            # Prepare response
            response_data = {
                'message': 'Sales invoice created successfully',
                'invoiceID': invoiceID,
                'status': 'success',
                'invoice_details': {
                    'customer_name': customer_name,
                    'invoice_date': str(invoice_date),
                    'due_date': str(due_date),
                    'total_amount': str(total),
                    'items_count': len(items),
                    'invoice_state': invoice_state,
                    'payment_method': payment_method
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
    
    except customer_table.DoesNotExist:
        return Response({
            'error': 'Customer not found',
            'message': f'Customer with ID {cusID} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except vendor_table.DoesNotExist:
        return Response({
            'error': 'Vendor not found',
            'message': f'Vendor with ID {venID} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except chart_of_account.DoesNotExist:
        return Response({
            'error': 'Account not found',
            'message': 'Required chart of account entry does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'An error occurred while creating the invoice'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_invoice_exists(request, invoiceID):
    """
    GET endpoint to check if invoice ID already exists
    Returns True if exists, False otherwise
    """
    db = DB_NAME
    
    try:
        exists = (
            customer_invoice.objects.using(db).filter(invoiceID=invoiceID).exists() or
            Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).exists()
        )
        
        return Response({
            'exists': exists,
            'invoiceID': invoiceID
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def billing_shipping_reference(db, invoice, cusID, shipping, method, cost):
    """Helper function to create shipping reference"""
    try:
        order_invoice_reference_address.objects.using(db).get(reference=invoice)
    except order_invoice_reference_address.DoesNotExist:
        order_invoice_reference_address.objects.using(db).create(
            source=method, 
            reference=invoice, 
            shipping_addr=shipping
        )
    
    try:
        shipping_cost.objects.using(db).get(invoiceID=invoice)
    except shipping_cost.DoesNotExist:
        shipping_cost.objects.using(db).create(
            invoiceID=invoice, 
            amount=cost, 
            custID=cusID
        )


def create_add_vat(db, invoiceID, vat):
    """Helper function to create VAT record"""
    if vat:
        try:
            Vat.objects.using(db).get(source=invoiceID, amount=vat)
        except Vat.DoesNotExist:
            Vat.objects.using(db).create(source=invoiceID, amount=vat)
            vat_account = chart_of_account.objects.using(db).get(account_bankname="Vat Account")
            vat_account.actual_balance += Decimal(vat)
            vat_account.save(using=db)


@api_view(['GET'])
def item(request):
    objs = Item.objects.using(DB_NAME).all()
    serializer = ItemSerializer(objs, many=True)
    return Response(serializer.data)


logger = logging.getLogger(__name__)

class CreateCustomerThrottle(AnonRateThrottle):
    """Limit customer creation to 5 per hour per IP"""
    rate = '500/hour'


@api_view(['POST'])
@throttle_classes([CreateCustomerThrottle])
def create_customer_api(request):
    """
    Secure API endpoint to create a customer
    Requires API Key in Authorization header
    """
    # 1. VERIFY API KEY
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header.startswith('ApiKey '):
        logger.warning(f"Missing API key from IP: {request.META.get('REMOTE_ADDR')}")
        return Response(
            {"error": "Missing API key. Use 'Authorization: ApiKey YOUR_KEY'"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    api_key = auth_header.replace('ApiKey ', '').strip()
    
    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt from IP: {request.META.get('REMOTE_ADDR')}")
        return Response(
            {"error": "Invalid API key"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # 2. VALIDATE AND PROCESS REQUEST
    db = DB_NAME
    serializer = CustomerSerializer(data=request.data)

    if serializer.is_valid():
        name = serializer.validated_data.get('name')
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')

        # Check duplicates in local DB
        if customer_table.objects.using(db).filter(Q(phone=phone) | Q(email=email)).exists():
            logger.info(f"Duplicate customer attempt: {email}")
            return Response(
                {"error": "Customer with this phone or email already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already exists in global DB
        if User.objects.using("afrikbook_client").filter(Q(username=name) | Q(email=email)).exists():
            logger.info(f"User already exists: {email}")
            return Response(
                {"error": "User already exists in client database"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create remote client details
            fallback_token = secrets.token_hex(16)
            client = create_client_dtails(request, db, name, email, fallback_token)
            
            if client:
                customer = serializer.save()
                customer.save(using=db)
                
                logger.info(f"Customer created successfully: {email}")
                return Response(
                    {
                        "message": "Customer created successfully",
                        "customer_id": customer.id
                    }, 
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.error(f"Failed to create customer remotely: {email}")
                return Response(
                    {"error": "Failed to create customer remotely"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}", exc_info=True)
            return Response(
                {"error": "An error occurred while creating customer"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    else:
        logger.warning(f"Invalid data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_item_qty(request):
    """
    GET  /api/check-item-qty/?item_id=ABC123
    Returns: { "item_id": "...", "quantity": <int> }
    """
    item_id = request.GET.get("item_id")
    if not item_id:
        return Response({"error": "item_id is required"}, status=400)

    # ------------------------------------------------------------------
    # 2. Use the env-defined DB & outlet
    # ------------------------------------------------------------------
    db = DB_NAME
    outlet = OUTLET_NAME

    # ------------------------------------------------------------------
    # 3. Stock-level flag
    # ------------------------------------------------------------------
    try:
        stock_ = Check_StockLevel_By.objects.using(db).first()
        stock_level = stock_.level if stock_ is not None else "NO"
    except Check_StockLevel_By.DoesNotExist:
        stock_level = "NO"

    # ------------------------------------------------------------------
    # 4. Core quantity logic (unchanged)
    # ------------------------------------------------------------------
    state = Qty_State(db, item_id)

    if state:
        filter_sales_conditions = Q(outlet=outlet)

        if stock_level == "YES":
            qty = get_grand_total_from_outlet_stockin(
                item_id, CreateOutletStockIn, outlet, db, filter_sales_conditions
            )
        else:
            qty = get_grand_total_from_stock_log(
                item_id,
                CreateOutletStockInLog,
                CreateStockInLog,
                outlet,
                db,
                filter_sales_conditions,
                filter_sales_conditions,
            )
    else:
        qty = 100_000

    return Response({"item_id": item_id, "quantity": qty})