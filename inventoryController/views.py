from time import time, ctime
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from inventoryController.models import InventoryItem
from CCPDController.utils import decodeJSON, get_db_client, sanitizeSku, convertToTime, get_client_ip
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
import pymongo

# pymongo
db = get_db_client()
qa_collection = db['Inventory']
user_collection = db['User']

# query param sku for inventory db row
# sku: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    
    if not sku:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)

    # find the Q&A record
    res = qa_collection.find_one({'sku': sku}, {'_id': 0})
    if not res:
        return Response('Record Not Found', status.HTTP_400_BAD_REQUEST)
    
    # get user info
    user = user_collection.find_one({'_id': ObjectId(res['owner'])}, {'name': 1, 'userActive': 1, '_id': 0})
    if not user:
        return Response('Owner Not Found', status.HTTP_404_NOT_FOUND)
    
    # replace owner field in response
    res['owner'] = user
    return Response(res, status.HTTP_200_OK)
        
# get all inventory by QA personal
# id: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryByOwnerId(request, page):
    try:
        body = decodeJSON(request.body)
        ownerId = str(ObjectId(body['id']))
        
        # TODO: make limit a path parameter
        # get targeted page
        limit = 10
        skip = page * limit
    except:
        return Response('Invalid Id', status.HTTP_400_BAD_REQUEST)
     
    # return all inventory from owner in array
    arr = []
    skip = page * limit
    for inventory in qa_collection.find({ 'owner': ownerId }).sort('sku', pymongo.DESCENDING).skip(skip).limit(limit):
        inventory['_id'] = str(inventory['_id'])
        arr.append(inventory)
    
    return Response(arr, status.HTTP_200_OK)


# 
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def getInventoryInfoByOwnerId(request):
    try:
        body = decodeJSON(request.body)
        ownerId = str(ObjectId(body['id']))
    except:
        return Response('Invalid Id', status.HTTP_400_BAD_REQUEST)
     
    # return all inventory from owner in array
    arr = []
    for inventory in qa_collection.find({ 'owner': ownerId }):
        inventory['_id'] = str(inventory['_id'])
        arr.append(inventory)
    
    return Response(arr, status.HTTP_200_OK)

# create single inventory Q&A record
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def createInventory(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)

    # if sku exist return conflict
    inv = qa_collection.find_one({'sku': body['sku']})
    if inv:
        return Response('SKU Already Existed', status.HTTP_409_CONFLICT)
    
    try:
        # construct new inventory
        newInventory = InventoryItem(
            time=str(ctime(time())),
            sku=sku,
            itemCondition=body['itemCondition'],
            comment=body['comment'],
            link=body['link'],
            platform=body['platform'],
            shelfLocation=body['shelfLocation'],
            amount=body['amount'],
            owner=body['owner'],
            marketplace=body['marketplace']
        )
        # pymongo need dict or bson object
        res = qa_collection.insert_one(newInventory.__dict__)
    except:
        return Response('Invalid Inventory Information', status.HTTP_400_BAD_REQUEST)
    return Response('Inventory Created', status.HTTP_200_OK)

# query param sku and body of new inventory info
# sku: string
# newInventory: Inventory
"""
{
    sku: xxxxx,
    newInv: {
        sku,
        itemCondition,
        comment,
        link,
        platform,
        shelfLocation,
        amount
    }
}
"""
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def updateInventoryBySku(request, sku):
    try:
        # convert to object id
        body = decodeJSON(request.body)
        sku = sanitizeSku(int(sku))
        if not sku:
            return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
        
        # check body
        newInv = body['newInventoryInfo']
        newInventory = InventoryItem(
            time = newInv['time'],
            sku = newInv['sku'],
            itemCondition = newInv['itemCondition'],
            comment = newInv['comment'],
            link = newInv['link'],
            platform = newInv['platform'],
            shelfLocation = newInv['shelfLocation'],
            amount = newInv['amount'],
            owner = newInv['owner'],
            marketplace = newInv['marketplace']
        )
    except:
        return Response('Invalid Inventory Info', status.HTTP_406_NOT_ACCEPTABLE)
    
    # check if inventory exists
    oldInv = qa_collection.find_one({ 'sku': sku })
    if not oldInv:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    # update inventory
    res = qa_collection.update_one(
        { 'sku': sku },
        {
            '$set': 
            {
                'amount': newInventory.amount,
                'itemCondition': newInventory.itemCondition,
                'platform': newInventory.platform,
                'shelfLocation': newInventory.shelfLocation,
                'comment': newInventory.comment,
                'link': newInventory.link,
                'marketplace': newInventory.marketplace
            }
        }
    )
    
    # return update status 
    if not res:
        return Response('Update Failed', status.HTTP_404_NOT_FOUND)
    return Response('Update Success', status.HTTP_200_OK)

# delete inventory by sku
# QA personal can only delete record created within 24h
# sku: string
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def deleteInventoryBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    if not sku:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    
    # pull time
    res = qa_collection.find_one({'sku': sku}, {'time': 1})
    if not res:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    

    # calculate time left to delete, prevent delete if result delta seconds is negative
    # convert form time string to time obj
    timeCreated = convertToTime(res['time'])
    one_day_later = timeCreated + timedelta(days=1)
    today = datetime.now()
    canDel = (one_day_later - today).total_seconds() > 0
    
    # perform deletion or throw error
    if canDel:
        de = qa_collection.delete_one({'sku': sku})
        return Response('Inventory Deleted', status.HTTP_200_OK)
    return Response('Cannot Delete Inventory After 24H, Please Contact Admin', status.HTTP_403_FORBIDDEN)