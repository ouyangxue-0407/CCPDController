import jwt
import uuid
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from userController.models import User
from .models import InvitationCode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.exceptions import AuthenticationFailed
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword, sanitizeName

# pymongo
db = get_db_client()
user_collection = db['User']
inventory_collection = db['Inventory']
inv_code_collection = db['Invitations']

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
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms='HS256')
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
    if user['role'] != 'Admin':
        return Response('Permission Denied', status.HTTP_403_FORBIDDEN)

    try:
        # construct payload
        expire = datetime.utcnow() + timedelta(days=admin_expire_days)
        payload = {
            'id': str(ObjectId(user['_id'])),
            'exp': expire,
            'iat': datetime.utcnow()
        }
        
        # construct tokent and return it
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    except:
        return Response('Failed to Generate Token', status.HTTP_500_INTERNAL_SERVER_ERROR)

    # return the id and name
    info = {
        'id': str(ObjectId(user['_id'])),
        'name': user['name']
    }

    # construct response store jwt token in http only cookie
    response = Response(info, status.HTTP_200_OK)
    response.set_cookie('token', token, httponly=True, expires=expire, samesite="None", secure=True)
    response.set_cookie('csrftoken', get_token(request), httponly=True, expires=expire, samesite="None", secure=True)
    return response

@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
def registerAdmin(request):
    return Response('Registration Success')

# delete user by id
# id: string
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def deleteUserById(request):
    try:
        # convert to BSON
        body = decodeJSON(request.body)
        uid = ObjectId(body['id'])
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
# id: string,
# userActive: bool
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def setUserActiveById(request):
    try:
        # convert to BSON
        body = decodeJSON(request.body)
        uid = ObjectId(body['id'])
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

# update anyones password by id
# id: string
# newpassword: string
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def updatePasswordById(request):
    try:
        # if failed to convert to BSON response 401
        body = decodeJSON(request.body)
        uid = ObjectId(body['id'])
    except:
        return Response('User ID Invalid:', status.HTTP_400_BAD_REQUEST)
    
    # query db for user
    res = user_collection.find_one({ 'id': uid })
    
    # check if password is valid
    if not sanitizePassword(body['password']):
        return Response('Invalid Password', status.HTTP_400_BAD_REQUEST)
    
    # if found, change its pass word
    if res:
        user_collection.update_one(
            { 'id': uid }, 
            { '$set': {'password': body['password']} }
        )
        return Response('Password Updated', status.HTTP_200_OK)
    return Response('User Not Found', status.HTTP_404_NOT_FOUND)


# update user information by id
# id: string
# body: UserDetail
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def updateUserById(request, uid):
    # try:
    # if failed to convert to BSON response 401
    body = decodeJSON(request.body)
    userId = ObjectId(uid)

    # if user not in db throw 404
    res = user_collection.find_one({ '_id': userId })
    if not res:
        return Response('User Not Found', status.HTTP_404_NOT_FOUND)
    
    # if password not passed in, use the old pass for the new object
    try:
        body['password'] = sanitizePassword(body['password'])
    except: 
        body['password'] = res['password']
    
    # remove all "$" and ensure no object {} passed in here
    body['email'] = sanitizeEmail(body['email'])
    body['name'] = sanitizeName(body['name'])

    print('user before modification:')
    print(res)
    print('req body:')
    print(body)
    
    print(body['email'])
    print(body['name'])
    
    if body['email'] == False or body['name'] == False or body['password'] == False:
        return Response('User Info Invalid', status.HTTP_400_BAD_REQUEST)
    
    # run new info through object relational mapping
    newUserInfo = User (
        name=body['name'],
        email=body['email'],
        role=body['role'],
        password=body['password'],
        registrationDate=res['registrationDate'],
        userActive=body['userActive']
    )
    # except:
    #     return Response('User Info Invalid:', status.HTTP_400_BAD_REQUEST)
    
    # try:
    # if found, update its info
    print(newUserInfo)
    
    user_collection.update_one(
        { 'id': userId }, 
        {
            '$set': {
                'name': newUserInfo.name,
                'email': newUserInfo.email,
                'role': newUserInfo.role,
                'password': newUserInfo.password,
                'registrationDate': newUserInfo.registrationDate,
                'userActive': newUserInfo.userActive
            }
        }
    )
    # except:
    #     return Response('Update User Info Failed', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response('Password Updated', status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllInventory(request): 
    inv = []
    for item in inventory_collection.find({}, {'_id': 0}):
        inv.append(item)
    return Response(inv, status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllUserInfo(request):
    userArr = []
    for item in user_collection.find({}, {'password': 0}):
        item['_id'] = str(item['_id'])
        userArr.append(item)
    return Response(userArr, status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllInvitationCode(request): 
    codeArr = []
    for item in inv_code_collection.find({}, {'_id': 0}):
        codeArr.append(item)
    return Response(codeArr, status.HTTP_200_OK)

# admin generate invitation code for newly hired QA personal to join
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def issueInvitationCode(request):
    # generate a uuid for invitation code
    inviteCode = uuid.uuid4()
    expireTime = (datetime.now() + timedelta(days=1)).timestamp()
    newCode = InvitationCode(
        code = str(inviteCode),
        exp = expireTime,
    )
    
    try:
        res = inv_code_collection.insert_one(newCode.__dict__)
    except:
        return Response('Server Error', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response('Invitation Code Created', status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def deleteInvitationCode(request):
    try:
        body = decodeJSON(request.body)
        code = body['code']
    except:
        return Response('Invalid Body: ', status.HTTP_400_BAD_REQUEST)
    
    try:
        res = inv_code_collection.delete_one({'code': code})
    except:
        return Response('Delete Failed', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response('Code Deleted!', status.HTTP_200_OK)