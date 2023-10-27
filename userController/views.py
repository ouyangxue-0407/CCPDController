import jwt
import json
from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, timedelta
from bson.objectid import ObjectId
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword, checkBody
from CCPDController.permissions import IsQAPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status
from rest_framework.response import Response
from userController.models import User
 
# pymongo
db = get_db_client()
collection = db['User']

# login any user and issue jwt
# _id: xxx
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    body = decodeJSON(request.body)

    # sanitize
    email = sanitizeEmail(body['email'])
    password = sanitizePassword(body['password'])
    if email == False or password == False:
        return Response('Invalid Login Information', status.HTTP_400_BAD_REQUEST)
    
    # check if user exist
    # only retrive user status and role
    user = collection.find_one({
        'email': email,
        'password': password
    }, { 'userActive': 1, 'role': 1 })
    
    # check user status
    if user == None:
        return Response('Login Failed', status.HTTP_404_NOT_FOUND)
    if user['userActive'] == False:
        return Response('User Inactive', status.HTTP_401_UNAUTHORIZED)

    # construct payload
    payload = {
        'id': str(ObjectId(user['_id'])),
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    
    # construct tokent and return it
    token = jwt.encode(payload, settings.SECRET_KEY)
    return Response(token, status.HTTP_200_OK)

# get user information without password
# _id: xxx
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def getUserById(request):
    body = decodeJSON(request.body)
    
    try:
        # convert to BSON
        uid = ObjectId(body['_id'])
    except:
        return Response('User ID Invalid:', status.HTTP_401_UNAUTHORIZED)
    
    # query db for user
    res = collection.find_one(
        { '_id': uid }, 
        { 'name': 1, 'email': 1, 'role': 1, 'registrationDate': 1, 'userActive': 1 }
    )
    if not res or not res['userActive']:
        return Response('User Not Found', status.HTTP_404_NOT_FOUND)

    # construct user object
    resUser = User(
        name=res['name'],
        email=res['email'],
        role=res['role'],
        password=None,
        registrationDate=res['registrationDate'],
        userActive=res['userActive']
    )
    
    # return as json object
    return Response(resUser.__dict__, status=status.HTTP_200_OK)

# user registration
# name: xxx
# email: xxx
# password: xxx
# inviationCode: xxx
@csrf_exempt
@api_view(['POST'])
def registerUser(request):
    body = decodeJSON(request.body)
    checkBody(body) # sanitization
    
    # prevent user_agent that is not mobile or tablet from registration
    # print(request.user_agent.is_mobile)
    # print(request.user_agent.is_tablet)
    # print(request.user_agent.is_touch_capable)
    # print(request.user_agent.is_pc)
    # print(request.user_agent)
    
    # check if email exist in database
    res = collection.find_one({ 'email': body['email'] })
    if res:
        return Response('Email already existed!', status.HTTP_400_BAD_REQUEST)
    
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

    if res:
        return Response('Registration Successful', status.HTTP_200_OK)
    return Response('Registration Failed', status.HTTP_500_INTERNAL_SERVER_ERROR)


# QA personal change own password
# _id: xxx
# newPassword: xxxx
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def changeOwnPassword(request):
    body = decodeJSON(request.body)
    
    # convert to BSON
    try:
        uid = ObjectId(body['_id'])
        password = sanitizePassword(body['newPassword'])
    except:
        return Response('User ID or Password Invalid:', status.HTTP_401_UNAUTHORIZED)
    
    # query for uid and role to be QA personal and update
    res = collection.update_one(
        {
            '_id': uid,
            'role': 'QAPersonal'
        },
        { '$set': {'password': password} }
    )
    
    if res:
        return Response('Password Updated', status.HTTP_200_OK)
    return Response('Cannot Update Password', status.HTTP_500_INTERNAL_SERVER_ERROR)
    