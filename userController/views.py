import jwt
from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.middleware.csrf import get_token
from datetime import date, datetime, timedelta
from bson.objectid import ObjectId
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword, checkBody, convertToTime
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from userController.models import User

# pymongo
db = get_db_client()
collection = db['User']
inv_collection = db['Invitations']

# jwt token expiring time
expire_days = 14

# will be called every time on open app
@csrf_protect
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def checkToken(request):
    # get token
    token = request.COOKIES.get('token')
    if not token:
        raise AuthenticationFailed('Token Not Found')
    
    # decode and return user id
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except jwt.DecodeError or UnicodeError:
        raise AuthenticationFailed('Invalid token')
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('No Token')

    # check user status
    user = collection.find_one({'_id': ObjectId(payload['id'])}, {'name': 1, 'role': 1, 'userActive': 1})
    if not user:
        raise AuthenticationFailed('User Not Found')
    if user['userActive'] == False:
        return AuthenticationFailed('User Inactive')
    
    # return user information
    return Response({ 'id': str(ObjectId(user['_id'])), 'name': user['name'] }, status.HTTP_200_OK)

# login any user and issue jwt
# _id: xxx
@csrf_protect
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
    }, { 'userActive': 1, 'role': 1, 'name': 1 })
    
    # check user status
    if user == None:
        return Response('Login Failed', status.HTTP_404_NOT_FOUND)
    if bool(user['userActive']) == False:
        return Response('User Inactive', status.HTTP_401_UNAUTHORIZED)

    try:
        # construct payload
        payload = {
            'id': str(ObjectId(user['_id'])),
            'exp': datetime.utcnow() + timedelta(days=expire_days),
            'iat': datetime.utcnow()
        }
        
        # construct tokent and return it
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    except:
        return Response('Failed to Generate Token', status.HTTP_500_INTERNAL_SERVER_ERROR)

    # return the id and name with token in http only cookie
    info = {
        'id': str(ObjectId(user['_id'])),
        'name': user['name']
    }

    # construct response store jwt token in http only cookie
    response = Response(info, status.HTTP_200_OK)
    response.set_cookie('token', token, httponly=True)
    response.set_cookie('csrftoken', get_token(request), httponly=True)
    return response

# get user information without password
# _id: xxx
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def getUserById(request):
    try:
        # convert to BSON
        body = decodeJSON(request.body)
        uid = ObjectId(body['_id'])
    except:
        return Response('Invalid User ID', status.HTTP_401_UNAUTHORIZED)
    
    # query db for user
    res = collection.find_one(
        { '_id': uid }, 
        { 'name': 1, 'email': 1, 'role': 1, 'registrationDate': 1, 'userActive': 1 }
    )
    if not res or not bool(res['userActive']):
        return Response('User Not Found', status.HTTP_404_NOT_FOUND)

    # construct user object
    resUser = User(
        name=res['name'],
        email=res['email'],
        role=res['role'],
        password=None,
        registrationDate=res['registrationDate'],
        userActive=bool(res['userActive'])
    )
    
    # return as json object
    return Response(resUser.__dict__, status=status.HTTP_200_OK)

# user registration
# name: xxx
# email: xxx
# password: xxx
# inviationCode: xxx (pending)
@csrf_protect
@api_view(['POST'])
def registerUser(request):
    try:
        # sanitize
        body = checkBody(decodeJSON(request.body))
        email = sanitizeEmail(body['email'])
        pwd = sanitizePassword(body['password'])
        invCode = body['code']
        # check if email exist in database
        res = collection.find_one({ 'email': body['email'] })
        if res:
            return Response('Email already existed!', status.HTTP_409_CONFLICT)
    except:
        return Response('Invalid Registration Info', status.HTTP_400_BAD_REQUEST)
    
    if email == False or pwd == False:
        return Response('Invalid Email Or Password', status.HTTP_400_BAD_REQUEST)
    
    # check if admin issues such code
    code = inv_collection.find_one({'code': invCode})
    if not code:
        return Response('Invitation Code Not Found', status.HTTP_404_NOT_FOUND)
    
    # check if token expired
    expTime = convertToTime(body['exp'])
    if ((expTime - datetime.now()).total_seconds() < 0):
        return Response('Invitation Code Expired', status.HTTP_406_NOT_ACCEPTABLE)
        
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
# newPassword: xxx
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def changeOwnPassword(request):
    try:
        # convert to BSON
        body = decodeJSON(request.body)
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

@csrf_protect
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission | IsQAPermission])
def logout(request):
    # construct response
    response = Response('User Logout', status.HTTP_200_OK)
    try:
        # delete jwt token and csrf token
        response.delete_cookie('token')
        response.delete_cookie('csrftoken')
    except:
        return Response('Token Not Found', status.HTTP_404_NOT_FOUND)
    return response