import uuid
from django.shortcuts import render
from bson.objectid import ObjectId
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword

# pymongo
db = get_db_client()
user_collection = db['User']

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
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def issueInvitationCode(request):
    
    # generate a uuid for invitation code
    inviteCode = uuid.uuid4()
    print(inviteCode)
    
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
