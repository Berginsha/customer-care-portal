import string,random

def alphanumeric():
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    print(x)