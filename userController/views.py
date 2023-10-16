import os
import json
from django.shortcuts import render, HttpResponse
from pymongo import MongoClient
from time import time, ctime
from datetime import date
from userController.models import User
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

# pymongo client
client = MongoClient(os.getenv('DATABASE_URL'), maxPoolSize=1)
db = client['CCPD']
collection = db['User']

# check if body contains valid user information
def checkBody(body):
    if len(body['name']) < 3 or len(body['name']) > 40:
        return HttpResponse('Invalid Name')
    elif len(body['email']) < 6 or len(body['email']) > 45 or '@' not in body['email']:
        return HttpResponse('Invalid Email')
    elif len(body['password']) < 8 or len(body['password']) > 45:
        return HttpResponse('Invalid Password')

# decode json to object function
decodeJSON = lambda body : json.loads(body.decode('utf-8'))

def getUserById(request):
    if request.method == 'GET':
        body = decodeJSON(request.body)
        
        # convert to BSON
        uid = ObjectId(body['_id'])
        
        # query db for user
        res = collection.find_one({'_id': uid})
        print(res)
        resUser = User(
            name=res['name'],
            email=res['email'],
            password=len(res['password']) * '*',
            role=res['role'],
            registrationDate=res['registrationDate'],
            userActive=res['userActive']
        )
        
        # return as json object
        return HttpResponse(json.dumps(resUser.__dict__))

@csrf_exempt
def validateUser(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        
        # query database for user
        res = collection.find_one({
            'email': body['email'],
            'password': body['password']
        })
        
        # check if user is active
        if res['userActive']:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
        
@csrf_exempt
def registerUser(request):
    if request.method == 'POST':
        body = decodeJSON(request.body)
          
        # check if body is valid
        checkBody(body)
        
        # check if email exist in database
        res = collection.find_one({ 'email': body['email'] })
        
        # check for existing email
        if res:
            return HttpResponse('Email already existed!')
        
        # construct user
        newUser = User(
            name=body['name'],
            email=body['email'],
            password=body['password'],
            role='QAPersonal',
            registrationDate=date.today().isoformat(),
            userActive=True
        )
        
        # insert user into db
        res = collection.insert_one(newUser.__dict__)

        # return the registration result
        if res:
            return HttpResponse(True)
        else:
            return HttpResponse(False)

# delete user by id
@csrf_exempt
def deleteUserById(request):
    if request.method == 'DELETE':
        body = decodeJSON(request.body)
        
        # convert to BSON
        uid = ObjectId(body['_id'])
        
        # query db for user
        res = collection.find_one({'_id': uid})
        
        # if found, delete it
        if res :
            res = collection.delete_one({'_id': uid})
            return HttpResponse('User Deleted')
        else:
            return HttpResponse('User Not Found')
            
# update user password
# qa personals can update their own password
def updatePasswordById(request):
    if request.method == 'PUT':
        body = decodeJSON(request.body)
        
        # convert to BSON
        uid = ObjectId(body['_id'])
        
        # query db for user
        res = collection.find_one({'_id': uid})
        
        # if found, change its pass word
        if res :
            res = collection.update_one(
                {'_id': uid}, 
                {'$set': {'password': body['password']}}
            )
            return HttpResponse('Password Updated')
        else:
            return HttpResponse('User Not Found')