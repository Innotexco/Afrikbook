import json
import re
from datetime import date, datetime

from Stock.models import Item
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Re-export money helpers for convenient imports: from main.utils import parse_money, format_money
from main.money import parse_money, clean_decimal, format_money, strip_money_commas  # noqa: F401

# Default page size for server-side list pagination
DEFAULT_PAGE_SIZE = 25


def paginate_queryset(request, queryset, per_page=DEFAULT_PAGE_SIZE):
    """
    Paginate a queryset or sequence using ?page= from the request.

    Returns a Django Page object (usable in templates as page_obj / iterable).
    """
    try:
        per_page = int(request.GET.get('per_page', per_page) or per_page)
    except (TypeError, ValueError):
        per_page = DEFAULT_PAGE_SIZE
    per_page = max(5, min(per_page, 200))

    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


_UNSAFE_FILENAME = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')


def document_pdf_filename(party_name, doc_date, invoice_type="Invoice"):
    """
    PDF / email attachment name: nameofcustomer_date_invoice type.pdf
    Example: Acme Ltd_21-10-2026_Invoice.pdf
    """
    def clean(part, fallback):
        text = _UNSAFE_FILENAME.sub(" ", str(part or "")).strip()
        text = re.sub(r"\s+", " ", text)
        return text or fallback

    name = clean(party_name, "Customer")
    kind = clean(invoice_type, "Invoice")
    date_str = _pdf_filename_date(doc_date)
    return f"{name}_{date_str}_{kind}.pdf"


def _pdf_filename_date(doc_date):
    if hasattr(doc_date, "strftime"):
        try:
            return doc_date.strftime("%d-%m-%Y")
        except Exception:
            pass

    raw = str(doc_date or "").strip()
    if not raw:
        return date.today().strftime("%d-%m-%Y")

    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", raw)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"

    match = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})", raw)
    if match:
        return f"{int(match.group(1)):02d}-{int(match.group(2)):02d}-{match.group(3)}"

    try:
        return datetime.fromisoformat(raw.replace("Z", "")[:19]).strftime("%d-%m-%Y")
    except Exception:
        return date.today().strftime("%d-%m-%Y")


def pagination_meta(page_obj):
    """JSON-safe pager fields for AJAX list endpoints."""
    if not page_obj:
        return {
            'page': 1,
            'num_pages': 1,
            'count': 0,
            'start_index': 0,
            'end_index': 0,
            'has_previous': False,
            'has_next': False,
            'previous_page': None,
            'next_page': None,
        }
    count = page_obj.paginator.count
    return {
        'page': page_obj.number,
        'num_pages': page_obj.paginator.num_pages,
        'count': count,
        'start_index': page_obj.start_index() if count else 0,
        'end_index': page_obj.end_index() if count else 0,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    }


def cookieCart(request):

	#Create empty cart for now for non-logged in user
	try:
		cart = json.loads(request.COOKIES['cart'])
	except:
		cart = {}

	items = []
	order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	cartItems = order['get_cart_items']

	for i in cart:
		#We use try block to prevent items in cart that may have been removed from causing error
		try:	
			if(cart[i]['quantity']>0): #items with negative quantity = lot of freebies  
				cartItems += cart[i]['quantity']

				product = Item.objects.get(id=i)
				total = (product.price * cart[i]['quantity'])

				order['get_cart_total'] += total
				order['get_cart_items'] += cart[i]['quantity']

				item = {
				'id':product.id,
				'product':{'id':product.id,'name':product.name, 'price':product.price, 
				'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
				'digital':product.digital,'get_total':total,
				}
				items.append(item)

				if product.digital == False:
					order['shipping'] = True
		except:
			pass
			
	return {'cartItems':cartItems ,'order':order, 'items':items}

def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']

	return {'cartItems':cartItems ,'order':order, 'items':items}

	
def guestOrder(request, data):
	name = data['form']['name']
	email = data['form']['email']

	cookieData = cookieCart(request)
	items = cookieData['items']

	customer, created = Customer.objects.get_or_create(
			email=email,
			)
	customer.name = name
	customer.save()

	order = Order.objects.create(
		customer=customer,
		complete=False,
		)

	for item in items:
		product = Product.objects.get(id=item['id'])
		orderItem = OrderItem.objects.create(
			product=product,
			order=order,
			quantity=(item['quantity'] if item['quantity']>0 else -1*item['quantity']), # negative quantity = freebies
		)
	return customer, order


def pagenation(request, obj, first, limit):
	  # for pagination
    page = request.GET.get('page', first)

    paginator = Paginator(obj, limit)
    try:
        obj = paginator.page(page)
    except PageNotAnInteger:
        obj = paginator.page(first)
    except EmptyPage:
        obj = paginator.page(paginator.num_pages)
    return obj