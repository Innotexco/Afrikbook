import random;
import string;

def random_string_generator(size=5, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


available_numbers = [x for x in range (10)] # number 0 to 9
size = 7 # Customer Id size : 7 digits


def generate_item_code():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str

def generate_order_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str

def generate_company_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(4)]
    new_number_str = "".join(new_number_list)
    return new_number_str

import string

def generate_unique_id(length=10):
    characters = 'STOCK-Rqv_' + string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for i in range(length))
    return unique_id