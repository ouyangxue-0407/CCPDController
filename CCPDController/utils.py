from datetime import datetime
import os
import json
from django.conf import settings
from rest_framework.response import Response
from rest_framework import exceptions
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# construct mongoDB client
# ssl hand shake error because ip not whitelisted
client = MongoClient(
    os.getenv('DATABASE_URL'), 
    maxPoolSize=1
)
db_handle = client[os.getenv('DB_NAME')]
def get_db_client():
    return db_handle

# decode body from json to object
decodeJSON = lambda body : json.loads(body.decode('utf-8'))

# get client ip address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# limit variables
max_name = 50
min_name = 3
max_email = 45
min_email = 6
max_password = 70
min_password = 8
max_sku = 7
min_sku = 4
max_inv_code = 100
min_inv_code = 10
max_role = 12
min_role = 4

# user registration date format
user_time_format = "%b %-d %Y"
# time_format = "%a %b %d %H:%M:%S %Y"

# inventory time format
# time format should match moment.js (MMM DD YYYY HH:mm:ss)
time_format = "%b %d %Y %H:%M:%S"

filter_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

# convert from string to datetime
# example: Thu Oct 12 18:48:49 2023
def convertToTime(time_str):
    return datetime.strptime(time_str, time_format)

# check if body contains valid user registration information
def checkBody(body):
    if not inRange(body['name'], min_name, max_name):
        return False
    elif not inRange(body['email'], min_email, max_email) or '@' not in body['email']:
        return False
    elif not inRange(body['password'], min_password, max_password):
        return False
    return body

# check input length
# if input is in range return true else return false
def inRange(input, minLen, maxLen):
    if len(str(input)) < minLen or len(str(input)) > maxLen:
        return False
    else: 
        return True

# sanitize mongodb strings
def removeStr(input):
    input.replace('$', '')
    return input

# skuy can be from 3 chars to 40 chars
def sanitizeSku(sku):
    # type check
    if not isinstance(sku, int):
        return False
    
    # len check
    if not inRange(sku, min_sku, max_sku):
        return False
    return sku

# name can be from 3 chars to 40 chars
def sanitizeName(name):
    # type check
    if not isinstance(name, str):
        return False
    
    # remove danger chars
    clean_name = removeStr(name)
    
    # len check
    if not inRange(clean_name, min_name, max_name):
        return False
    return clean_name

# role length from 4 to 12
def sanitizeRole(role):
    if not isinstance(role, str):
        return False
    if not inRange(role, min_role, max_role):
        return False
    return role

# email can be from 7 chars to 40 chars
def sanitizeEmail(email):
    # type and format check
    if not isinstance(email, str) or '@' not in email:
        return False
    
    # len check
    if not inRange(email, min_email, max_email):
        return False
    return email

# password can be from 8 chars to 40 chars
def sanitizePassword(password):
    if not isinstance(password, str):
        return False
    if not inRange(password, min_password, max_password):
        return False
    return password

# platfrom can only be these
def sanitizePlatform(platform):
    if platform not in ['Amazon', 'eBay', 'Official Website', 'Other']:
        return False
    return platform

# shelf location sanitize
def sanitizeShelfLocation(shelfLocation):
    if not isinstance(shelfLocation, str):
        return False
    return shelfLocation

# invitation code should be a string
def sanitizeInvitationCode(code):
    if not isinstance(code, str):
        return False
    if not inRange(code, min_inv_code, max_inv_code):
        return False
    return code


# these below will raise type error instead of returning false
# make sure string is type str and no $ included 
def sanitizeString(field):
    if not isinstance(field, str):
        raise TypeError('Invalid Information')
    return field.replace('$', '')

# makesure number is int and no $
def sanitizeNumber(num):
    if not isinstance(num, int):
        raise TypeError('Invalid Information')

# sanitize all field in user info body
# make sure user is active and remove $
def sanitizeUserInfoBody(body):
    for attr, value in body.items():
        # if hit user active field set the field to bool type
        # if not sanitize string and remove '$'
        if attr == 'userActive':
            body[attr] = bool(value == 'true')
        else:
            body[attr] = sanitizeString(value)