import requests
from django.contrib import messages


def create_shipping_address(request, csrftoken, id, addr_id, city, state, country, address):
    ship_address = {
                    'id': id,
                    'addr_id': addr_id,
                    'city'   : city,
                    'state': state, 
                    'country'   : country, 
                    'address'  : address,
                }

               
    
    # Define headers with CSRF token
    headers = {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
        }
    # Send the POST request
    
    try:
        response = requests.post('https://console.afrikbook.com/create_new_shippping_address', json=ship_address, headers=headers)
        
    except requests.RequestException:
        pass
  
    # Check response status
    if response.status_code == 200:
        data = response.json()
        messages.success(request, data['customer'])
    else:
        messages.error(request, "Error creating shipping address")
