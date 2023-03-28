import string
import random
import MySQLdb


def alphanumeric():
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return x


def mysql_connect():
    connection = MySQLdb.connect(
        host='localhost',
        user='admin',
        passwd='bergindatabase1',
        db='mydb'
    )
    return connection
