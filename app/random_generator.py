import random
import string

def generate_otp():
    digits = '0123456789'
    otp = ''
    for i in range(6):
        otp += random.choice(digits)
    return otp

def alphanumeric():
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return x