import os
import json
from django.shortcuts import render, HttpResponse
from pymongo import MongoClient
from time import time, ctime
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

# pymongo client
client = MongoClient(os.getenv('DATABASE_URL'), maxPoolSize=1)
db = client['CCPD']
collection = db['User']

# decode json to object function
decodeJSON = lambda body : json.loads(body.decode('utf-8'))

def getUserNameById(request):
    if request.method == "GET":
        body = decodeJSON(request.body)
        print(body)
        
        # find it in db and return
        res = collection.find_one({ "email": body.email }).name
        return HttpResponse(res)
        

def getIfEmailExist(request):
    if request.method == "GET":
        print('get if email exist')

@csrf_exempt
def validateUser(request):
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        
        # query database for user
        res = collection.find_one({
            "email": body['email'],
            "password": body['password']
        })
        
        if res:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
            
        
        
        

def registerUser(request):
    if request.method == "POST":
        body = decodeJSON(request.body)
        print(body)

# delete user by id
def deleteUserById(request):
    if request.method == "DELETE":
        print(request)

def changePasswordById(request):
    if request.method == "PUT":
        print(request)