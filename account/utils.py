import random

import random;
import string;
from Stock.setCurrentUsers import get_current_user


available_numbers = [x for x in range (10)] # number 0 to 9
size = 7 # Customer Id size : 7 digits


def generate_token_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str

def generate_order_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(size)]
    new_number_str = "".join(new_number_list)
    return new_number_str

import string

def generate_unique_id(length=10):
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for i in range(length))
    return unique_id



def generate_new_account_id():
    new_number_list = [str(random.choice(available_numbers)) for _ in range(3)]
    new_number_str = "".join(new_number_list)
    return new_number_str




def random_string_generator2(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
 


def unique_accountId_generator(Klass, db, new_account_id=None):
    # db= user.company_id.db_name
    qs_exists = Klass.objects.using(db).filter(account_id=new_account_id).exists()
    if qs_exists:
        new_account_id = "{new_account_id}_{randstr}".format(
                    new_account_id=new_account_id,
                    randstr=random_string_generator2(size=4)
                )
        return unique_accountId_generator(Klass, db, new_account_id=new_account_id)
    return new_account_id