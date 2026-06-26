from main.models import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests, json
from django.db.models import F, Value


def shipping_address_api(request):
    company_id = request.GET.get('company_id')

    if not company_id:
        return JsonResponse({'ship': []})

    company_user_ids = User.objects.using('afrikbook_client').filter(
        company_id=company_id
    ).values_list('id', flat=True)

    ship = shipping_addr.objects.using('afrikbook_client').filter(
        addr_id_id__in=company_user_ids
    ).annotate(
        username=F('addr_id__username'),
        email=F('addr_id__email'),        
    ).values()

    return JsonResponse({'ship': list(ship)})


def get_shipping_address(request, customer_id):
    db = request.user.company_id.db_name
    if request.method == 'GET':
        data = shipping_addr.objects.using('afrikbook_client').filter(addr_id=customer_id).values() or []
  
    return JsonResponse({'data': list(data)}, safe=False)


@csrf_exempt
def create_new_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))

            username        = data.get('username')
            email           = data.get('email')
            password        = data.get('password')
            company_id      = data.get('company_id')
            company_name    = data.get('company_name')
            company_db      = data.get('company_db')
            company_db_pass = data.get('company_db_pass', '')
            company_db_user = data.get('company_db_user', 'root')
            phone           = data.get('phone')
            
            company_table.objects.using("afrikbook_client").get_or_create(
                id=company_id,
                defaults={
                    'company_name':    company_name,
                    'db_name':         company_db,
                    'phone':           phone,
                }
            )

            user = User(username=username, email=email)
            user.set_password(password)
            user.company_id_id = company_id
            user.save(using="afrikbook_client")

            company = client_companies.objects.using("afrikbook_client").create(
                company_id      = company_id,
                company_name    = company_name,
                company_db      = company_db,
                company_db_pass = company_db_pass,
                company_db_user = company_db_user,
                client_id       = user,
                phone           = phone,
                email           = email,
            )

            return JsonResponse({'user': username})

        except Exception as e:
            return JsonResponse({'user': False, 'error': str(e)})

    return JsonResponse({'user': False, 'error': 'Invalid request method'})


@csrf_exempt
def create_new_shippping_address(request):
    if request.method == "POST":
         data = json.loads(request.body.decode('utf-8'))
        
         id = data['id']
         addr_id = data['addr_id']
         city = data['city']
         state = data['state']
         country  = data['country']                  
         address  = data['address']
        

         customer = User.objects.using("afrikbook_client").get(id=addr_id)
         try:
            shipping_addr.objects.using("afrikbook_client").get(addr_id   = customer,city   = city, state  = state,  country = country,  address  = address)
            return JsonResponse({'customer': "Shipping address already exist"})
         except shipping_addr.DoesNotExist:
            if id:
                ship_add = shipping_addr.objects.using("afrikbook_client").filter(id=id).update(
                    addr_id   = customer,
                    city   = city,                  
                    state  = state,
                    country  = country,
                    address  = address
                )
                msg = "Shipping Address updated successfully"
            else:
                ship_add = shipping_addr.objects.using("afrikbook_client").create(
                    addr_id   = customer,
                    city   = city,                  
                    state  = state,
                    country  = country,
                    address  = address
                )
                msg = "Shipping Address created successfully"
                
            if ship_add:
                return JsonResponse({'customer': msg, })
            else:
                return JsonResponse({'customer': False})


def is_endpoint_available(url):
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200      
        except requests.RequestException:
            # messages.error(request, "Endpoint not available")
            return False