import random;
import string;
from .setCurrentUsers import get_current_user

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

import string

def generate_unique_id(length=10):
    characters = 'STOCK-Rqv_' + string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for i in range(length))
    return unique_id



from django.utils.text import slugify

def random_string_generator2(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
 
def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.item_name)

    Klass = instance.__class__
    user= get_current_user()
    db= user.company_id.db_name
    qs_exists = Klass.objects.using(db).filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator2(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
 
