import jwt
import uuid
import json
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from bson.objectid import ObjectId
from datetime import date, datetime, timedelta
from .models import InvitationCode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import AuthenticationFailed
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword

# pymongo
db = get_db_client()
user_collection = db['User']
inventory_collection = db['Inventory']
inv_collection = db['Invitations']

# admin jwt token expiring time
admin_expire_days = 90

@csrf_protect
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def checkAdminToken(request):
    # get token
    token = request.COOKIES.get('token')
    
    # decode and return user id
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except jwt.DecodeError or UnicodeError:
        raise AuthenticationFailed('Invalid token')
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')

    if token:
        user = user_collection.find_one({'_id': ObjectId(payload['id'])}, {'name': 1, 'role': 1})
        if user:
            return Response({ 'id': str(ObjectId(user['_id'])), 'name': user['name']}, status.HTTP_200_OK)
    return Response('Token Not Found, Please Login Again', status.HTTP_100_CONTINUE)

# login any user and issue jwt
@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
def adminLogin(request):
    body = decodeJSON(request.body)

    # sanitize
    email = sanitizeEmail(body['email'])
    password = sanitizePassword(body['password'])
    if email == False or password == False:
        return Response('Invalid Login Information', status.HTTP_400_BAD_REQUEST)
    
    # check if user exist
    # only retrive user status and role
    user = user_collection.find_one({
        'email': email,
        'password': password
    }, { 'userActive': 1, 'role': 1, 'name': 1 })
    
    # check user status
    if not user:
        return Response('Login Failed', status.HTTP_404_NOT_FOUND)
    if bool(user['userActive']) == False:
        return Response('User Inactive', status.HTTP_401_UNAUTHORIZED)
    if (user['role'] != 'Admin'):
        return Response('Permission Denied', status.HTTP_403_FORBIDDEN)

    try:
        # construct payload
        payload = {
            'id': str(ObjectId(user['_id'])),
            'exp': datetime.utcnow() + timedelta(days=admin_expire_days),
            'iat': datetime.utcnow()
        }
        
        # construct tokent and return it
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    except:
        return Response('Failed to Generate Token', status.HTTP_500_INTERNAL_SERVER_ERROR)

    # return the id and name
    info = {
        'id': str(ObjectId(user['_id'])),
        'name': user['name']
    }

    # construct response store jwt token in http only cookie
    response = Response(info, status.HTTP_200_OK)
    response.set_cookie('token', token, httponly=True)
    response.set_cookie('csrftoken', get_token(request), httponly=True)
    return response

@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
def registerAdmin(request):
    return Response('Registration Success')

# delete user by id
# _id: string
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def deleteUserById(request):
    try:
        # convert to BSON
        body = decodeJSON(request.body)
        uid = ObjectId(body['_id'])
    except:
        return Response('Invalid User ID', status.HTTP_400_BAD_REQUEST)
    
    # query db for user
    res = user_collection.find_one({'_id': uid})
    
    # if found, delete it
    if res :
        user_collection.delete_one({'_id': uid})
        return Response('User Deleted', status.HTTP_200_OK)
    return Response('User Not Found', status.HTTP_404_NOT_FOUND)

#  set any user status to be active or disabled
# _id: string,
# password: string
# userActive: bool
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def setUserActive(request):
    try:
        # convert to BSON
        body = decodeJSON(request.body)
        uid = ObjectId(body['_id'])
    except:
        return Response('Invalid User ID', status.HTTP_400_BAD_REQUEST)
    
    # query db for user
    res = user_collection.find_one({'_id': uid})
    
    # if found, switch user active to false
    if res :
        res = user_collection.update_one(
            { '_id': uid }, 
            { '$set': {'userActive': body['userActive']} }
        )
        if res:
            return Response('Updated User Activation Status', status.HTTP_200_OK)
    return Response('User Not Found')

# admin generate invitation code for newly hired QA personal to join
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def issueInvitationCode(request):
    
    
    # generate a uuid for invitation code
    inviteCode = uuid.uuid4()
    print(inviteCode)
    
    expireTime = datetime.now() 
    
    
    newCode = InvitationCode(
        code = inviteCode,
        available = True,
        exp = '',
    )
    
    try:
        inv_collection.insert_one(newCode)
    except:
        return Response('Database Error', status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response('Invitation Code Created: '.join(inviteCode), status.HTTP_200_OK)

# update anyones password by id
# _id: string
# newpassword: string
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def updatePasswordById(request):
    try:
        # if failed to convert to BSON response 401
        body = decodeJSON(request.body)
        uid = ObjectId(body['_id'])
    except:
        return Response('User ID Invalid:', status.HTTP_400_BAD_REQUEST)
    
    # query db for user
    res = user_collection.find_one({ '_id': uid })
    
    # check if password is valid
    if not sanitizePassword(body['password']):
        return Response('Invalid Password', status.HTTP_400_BAD_REQUEST)
    
    # if found, change its pass word
    if res:
        user_collection.update_one(
            { '_id': uid }, 
            { '$set': {'password': body['password']} }
        )
        return Response('Password Updated', status.HTTP_200_OK)
    return Response('User Not Found', status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllInventory(request): 
    inv = []
    for item in inventory_collection.find({}, {'_id': 0}):
        inv.append(item)
    
    return Response(inv, status.HTTP_200_OK)