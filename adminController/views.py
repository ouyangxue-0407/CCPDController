from django.shortcuts import render
from bson.objectid import ObjectId
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from CCPDController.permissions import IsQAPermission
from CCPDController.authentication import JWTAuthentication
from CCPDController.utils import decodeJSON, get_db_client, sanitizeEmail, sanitizePassword

# pymongo
db = get_db_client()
user_collection = db['User']

# delete user by id
@api_view(['DELETE'])
def deleteUserById(request):
    body = decodeJSON(request.body)
    
    # convert to BSON
    try:
        uid = ObjectId(body['_id'])
    except:
        return Response('Invalid User ID', status.HTTP_400_BAD_REQUEST)
    
    # query db for user
    res = user_collection.find_one({'_id': uid})
    
    # if found, delete it
    if res :
        user_collection.delete_one({'_id': uid})
        return Response('User Deleted', status.HTTP_200_OK)
    else:
        return Response('User Not Found', status.HTTP_404_NOT_FOUND)
 
@api_view(['POST'])
def setUserActive(request):
    body = decodeJSON(request.body)
    
    # convert to BSON
    try:
        uid = ObjectId(body['_id'])
    except:
        return Response('Invalid User ID')
    
    # query db for user
    res = user_collection.find_one({'_id': uid})
    
    # if found, switch user active to false
    if res :
        res = user_collection.update_one({'_id': uid})
        return Response('User Deleted')
    else:
        return Response('User Not Found')

