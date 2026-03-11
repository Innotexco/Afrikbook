from rest_framework import serializers
from Stock.models import *
from customer.models import customer_table
from client.models import shipping_addr
from rest_framework import serializers
from customer.models import customer_table, customer_invoice, receivable, Vat
from vendor.models import vendor_table, Vendor_invoice
from account.models import chart_of_account, account_log
from Stock.models import Item, CreateStockIn
from settings.models import shipping_cost, shipping_method
from decimal import Decimal
from datetime import datetime
# from customer.functions.customer import AfrikBookDB, create_client_dtails
# from main import User


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = shipping_addr
        fields = ['addr_id', 'city', 'state', 'country', 'address']


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields =   ['name', 'value']


class ItemSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=True)
    class Meta:
        model = Item
        fields =  ['item_name', 'selling_price', 'retailer_price', 'purchase_price', 'wholesale_price',  'description', 'attribute', 'image', 'generated_code' ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = customer_table
        fields = ['id', 'name', 'phone', 'email', 'customer_code', 'category', 'invoice', ]
        read_only_fields = ['customer_code', 'company_name']


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendor model"""
    class Meta:
        model = vendor_table
        fields = ['id', 'custID', 'company_name', 'email', 'phone_number', 'address', 'invoices']


class ChartOfAccountSerializer(serializers.ModelSerializer):
    """Serializer for Chart of Account model"""
    class Meta:
        model = chart_of_account
        fields = ['account_id', 'account_bankname', 'account_type', 'actual_balance']


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Method model"""
    class Meta:
        model = shipping_method
        fields = ['id', 'method_name', 'description']


class SalesInvoiceItemSerializer(serializers.Serializer):
    """Serializer for individual invoice items"""
    itemcode = serializers.CharField(required=True)
    item_name = serializers.CharField(required=True)
    item_description = serializers.CharField(required=False, allow_blank=True, default='')
    qty = serializers.IntegerField(required=True, min_value=1)
    unit = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    discount = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, default=0)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    purchaseP = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    def validate_itemcode(self, value):
        """Validate that itemcode is not '0' or empty"""
        if not value or value == "0":
            raise serializers.ValidationError("Invalid item code")
        return value

    def validate_qty(self, value):
        """Ensure quantity is at least 1"""
        if value <= 0:
            return 1
        return value


class SalesInvoiceSerializer(serializers.Serializer):
    """Main serializer for Sales Invoice API"""
    
    # Customer/Vendor Information
    cusID = serializers.IntegerField(required=False, allow_null=True)
    venID = serializers.IntegerField(required=False, allow_null=True)
    accountType = serializers.ChoiceField(choices=['Customer', 'Vendor'], required=True)
    customer_name = serializers.CharField(required=True, max_length=255)
    
    # Invoice Details
    invoice_date = serializers.DateField(required=True)
    due_date = serializers.DateField(required=True)
    invoiceID = serializers.CharField(required=True, max_length=100)
    order_id = serializers.CharField(required=False, allow_blank=True, default='')
    Gdescription = serializers.CharField(required=False, allow_blank=True, default='')
    
    # Invoice State
    invoice_state = serializers.BooleanField(required=False, default=False)
    credit_sales = serializers.BooleanField(required=False, default=False)
    
    # Payment Information
    payment_method = serializers.ChoiceField(
        choices=['Cash', 'Transfer', 'Transfer and Cash', 'Cheque', 'POS'],
        required=False,
        default='Cash'
    )
    t_account = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transfer_amount = serializers.DecimalField(
        required=False, 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    cash_amount = serializers.DecimalField(
        required=False, 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Shipping Information
    shipping_method = serializers.CharField(required=False, allow_blank=True, default='')
    shipping_address = serializers.CharField(required=False, allow_blank=True, default='')
    shipping_cost = serializers.DecimalField(
        required=False, 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Financial Details
    vat = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, default=0)
    sub_total = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    total = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    
    # Items
    items = SalesInvoiceItemSerializer(many=True, required=True)

    def validate(self, data):
        """Validate the entire invoice data"""
        
        # Ensure either cusID or venID is provided
        if not data.get('cusID') and not data.get('venID'):
            raise serializers.ValidationError({
                'cusID': 'Either Customer ID or Vendor ID must be provided',
                'venID': 'Either Customer ID or Vendor ID must be provided'
            })
        
        # Validate items exist
        if not data.get('items') or len(data['items']) == 0:
            raise serializers.ValidationError({
                'items': 'At least one item is required'
            })
        
        # Validate invoice date is not in future
        if data['invoice_date'] > datetime.now().date():
            raise serializers.ValidationError({
                'invoice_date': 'Invoice date cannot be in the future'
            })
        
        # Validate due date is after invoice date
        if data['due_date'] < data['invoice_date']:
            raise serializers.ValidationError({
                'due_date': 'Due date must be after invoice date'
            })
        
        # Validate transfer and cash amounts if payment method is "Transfer and Cash"
        if data.get('payment_method') == 'Transfer and Cash':
            transfer = data.get('transfer_amount', 0)
            cash = data.get('cash_amount', 0)
            total = data.get('total', 0)
            
            if Decimal(transfer) + Decimal(cash) != Decimal(total):
                raise serializers.ValidationError({
                    'payment_method': 'Transfer amount + Cash amount must equal total amount'
                })
        
        return data


class SalesInvoiceResponseSerializer(serializers.Serializer):
    """Serializer for API response"""
    message = serializers.CharField()
    invoiceID = serializers.CharField()
    status = serializers.CharField()
    invoice_details = serializers.DictField(required=False)


class CustomerInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Customer Invoice model"""
    class Meta:
        model = customer_invoice
        fields = '__all__'





class InvoiceItemSerializer(serializers.Serializer):
    """Serializer for individual invoice line items"""
    id = serializers.IntegerField(read_only=True)
    itemcode = serializers.CharField()
    item_name = serializers.CharField()
    item_description = serializers.CharField(allow_blank=True)
    qty = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_p = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    purchaseP = serializers.DecimalField(max_digits=12, decimal_places=2)


class InvoiceDetailSerializer(serializers.Serializer):
    """Detailed serializer for a single invoice with all items"""
    invoiceID = serializers.CharField()
    cusID = serializers.CharField()
    customer_name = serializers.CharField()
    order_ID = serializers.CharField(allow_blank=True)
    Gdescription = serializers.CharField()
    invoice_date = serializers.DateTimeField()
    due_date = serializers.DateField()
    invoice_state = serializers.CharField()
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    amount_expected = serializers.DecimalField(max_digits=12, decimal_places=2)
    cancellation_status = serializers.CharField()
    status = serializers.CharField()
    outlet = serializers.CharField()
    Userlogin = serializers.CharField()
    payment_method = serializers.CharField(allow_blank=True)
    
    # Payment method flags
    Transfer = serializers.CharField()
    POS = serializers.CharField()
    Cash = serializers.CharField()
    Customer_account = serializers.CharField()
    Cheque = serializers.CharField()
    
    # Calculated fields
    items = InvoiceItemSerializer(many=True, read_only=True)
    sub_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    actual_payment_method = serializers.CharField(read_only=True)


class InvoiceListSerializer(serializers.Serializer):
    """Simplified serializer for invoice list"""
    invoiceID = serializers.CharField()
    customer_name = serializers.CharField()
    invoice_date = serializers.DateTimeField()
    invoice_state = serializers.CharField()
    amount_expected = serializers.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(read_only=True)


class InvoiceSummarySerializer(serializers.Serializer):
    """Serializer for invoice summary statistics"""
    total_invoices = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_invoices = serializers.IntegerField()
    supplied_invoices = serializers.IntegerField()