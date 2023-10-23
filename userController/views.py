import jwt
import json
from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, timedelta
from bson.objectid import ObjectId
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from CCPDController.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from userController.models import User

# check if body contains valid user information
def checkBody(body):
    if len(body['name']) < 3 or len(body['name']) > 40:
        return HttpResponse('Invalid Name')
    elif len(body['email']) < 6 or len(body['email']) > 45 or '@' not in body['email']:
        return HttpResponse('Invalid Email')
    elif len(body['password']) < 8 or len(body['password']) > 45:
        return HttpResponse('Invalid Password')
 
# pymongo
db = get_db_client()
collection = db['User']

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    body = decodeJSON(request.body)
    
    # sanitize
    email = sanitizeEmail(body['email'])
    password = sanitizePassword(body['password'])
    if email is False or password is False:
        return Response('Invalid Login Information', status=status.HTTP_400_BAD_REQUEST)
    
    # check if user exist
    user = collection.find_one({'email': email, 'password': password})
    if user is None:
        return Response('Login Failed', status=status.HTTP_404_NOT_FOUND)
    if user['userActive'] is False:
        return Response('User Inactive', status=status.HTTP_401_UNAUTHORIZED)
    
    # return jwt token to user
    payload = {
        'id': str(ObjectId(user['_id'])),
        'exp': datetime.utcnow() + timedelta(days=14),
        'iat': datetime.utcnow()
    }
    
    # construct tokent and return it
    token = jwt.encode(payload, settings.SECRET_KEY)
    return Response(token, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getUserById(request):
    body = decodeJSON(request.body)
    
    try:
        # convert to BSON
        uid = ObjectId(body['_id'])
    except:
        return Response('User ID Invalid:', status=status.HTTP_401_UNAUTHORIZED)
    
    # query db for user
    res = collection.find_one({'_id': uid})
    if not res:
        return Response('User Not Found', status=status.HTTP_404_NOT_FOUND)

    # construct user object
    resUser = User(
        name=res['name'],
        email=res['email'],
        password='***',
        role=res['role'],
        registrationDate=res['registrationDate'],
        userActive=res['userActive']
    )
    
    # return as json object
    return Response(resUser.__dict__, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def registerUser(request):
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
@api_view(['DELETE'])
def deleteUserById(request):
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
# admin password have to be set in mongo manually
@api_view(['PUT'])
@csrf_exempt
def updatePasswordById(request):
    body = decodeJSON(request.body)
    
    # convert to BSON
    uid = ObjectId(body['_id'])
    
    # query db for user
    res = collection.find_one({
        '_id': uid, 
        'role': 'QAPersonal'
    })
    
    # check if password is valid
    if len(body['password']) < 8 or len(body['password']) > 45:
        return HttpResponse('Invalid Password')
    
    # if found, change its pass word
    if res :
        collection.update_one(
            { '_id': uid }, 
            { '$set': {'password': body['password']} }
        )
        return HttpResponse('Password Updated')
    else:
        return HttpResponse('User Not Found')

