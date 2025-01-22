import random


available_numbers = [x for x in range (10)] # number 0 to 9
size = 7 # Customer Id size : 7 digits


def generate_customer_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str

def generate_order_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str

def generate_invoice_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str


import string

def generate_unique_id(length=10):
    characters = 'VENDOR-Rqv_' + string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for i in range(length))
    return unique_id


def user_login(request):
    user = request.user
    return user