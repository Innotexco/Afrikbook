import string, random

def generate_staff_id(length=3):
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for i in range(length))
    return unique_id