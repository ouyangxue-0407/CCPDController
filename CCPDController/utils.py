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
    
# check if obj is type t
def checkT(obj, t):
    if type(obj) is not t:
        return False

# check input length
def checkLen(input, minLen, maxLen):
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
    if checkT(sku, int):
        return False
    
    # len check
    if not checkLen(sku, 4, 7):
        return False
    return sku

# name can be from 3 chars to 40 chars
def sanitizeName(name):
    # type check
    if checkT(name, str):
        return False
    
    # remove danger chars
    clean_name = removeStr(name)
    
    # len check
    if len(clean_name) < 3 or len(clean_name) > 40:
        return False
    return clean_name

# email can be from 7 chars to 40 chars
def sanitizeEmail(email):
    # type and format check
    if checkT(email, str) or '@' not in email:
        return False
    
    # len check
    if len(email) < 7 or len(email) > 40:
        return False
    return email

# password can be from 8 chars to 40 chars
def sanitizePassword(password):
    if checkT(password, str):
        return False
    if len(password) < 8 or len(password) > 40:
        return False
    return password

# platfrom can only be these
def sanitizePlatform(platform):
    if platform not in ['Amazon', 'eBay', 'Official Website', 'Other']:
        return False
    
# shelf location sanitize
def sanitizeShelfLocation(shelfLocation):
    if type(shelfLocation) is not str:
        return False
