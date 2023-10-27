import os
import json
import jwt
from django.conf import settings
from django.shortcuts import HttpResponse
from rest_framework import exceptions
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# get pymongo client obj
def get_db_client():
    client = MongoClient(os.getenv('DATABASE_URL'), maxPoolSize=2)
    db_handle = client[os.getenv('DB_NAME')]
    return db_handle

# decode body from json to object
decodeJSON = lambda body : json.loads(body.decode('utf-8'))\

# limit variables
max_name = 40
min_name = 3
max_email = 45
min_email = 6
max_password = 70
min_password = 8
min_sku = 4
max_sku = 7

# check if body contains valid user information
def checkBody(body):
    if inRange(body['name'], min_name, min_email):
        return HttpResponse('Invalid Name')
    elif len(body['email']) < min_email or len(body['email']) > max_email or '@' not in body['email']:
        return HttpResponse('Invalid Email')
    elif len(body['password']) < min_password or len(body['password']) > max_password:
        return HttpResponse('Invalid Password')

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
    input.replace('.', '')
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

# shelf location sanitize
def sanitizeShelfLocation(shelfLocation):
    if not isinstance(shelfLocation, str):
        return False
