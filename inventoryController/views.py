from time import time, ctime
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from inventoryController.models import InventoryItem
from CCPDController.utils import decodeJSON, get_db_client, sanitizeSku, time_format
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
import json
import pymongo

# pymongo
db = get_db_client()
collection = db['Inventory']
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
    res = collection.find_one({'sku': sku}, {'_id': 0})
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
def getInventoryByOwnerId(request):
    try:
        body = decodeJSON(request.body)
    except:
        return Response('Invalid Body',status.HTTP_400_BAD_REQUEST)

    try:
        ownerId = str(ObjectId(body['id']))
    except:
        return Response('Invalid Id', status.HTTP_400_BAD_REQUEST)
    
    # return all inventory from owner in array
    arr = []
    for inventory in collection.find({ 'owner': ownerId }).sort('sku', pymongo.DESCENDING):
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

    # if sku exist return error
    inv = collection.find_one({'sku': body['sku']})
    if inv:
        return Response('SKU Already Existed', status.HTTP_409_CONFLICT)
    
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
    )
    
    # pymongo need dict or bson object
    res = collection.insert_one(newInventory.__dict__)
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
        sku = sanitizeSku(sku)
        if not sku:
            return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
        # check body
        newInv = body['newInventoryInfo']
        newInventory = InventoryItem(
            time = newInv['time'],
            sku = newInv['sku'],
            itemCondition = newInv['time'],
            comment = newInv['comment'],
            link = newInv['link'],
            platform = newInv['platform'],
            shelfLocation = newInv['shelfLocation'],
            amount = newInv['amount'],
            owner = newInv['owner']
        )
    except:
        return Response('Invalid Inventory Info', status.HTTP_400_BAD_REQUEST)
    
    print(sku)
    # check if inventory exists
    oldInv = collection.find_one({ 'sku': sku })
    if not oldInv:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    # try:
    #     # construct new inventory
    #     newInventory = InventoryItem(
    #         time = str(ctime(time())),
    #         sku = newInv['sku'] if newInv['sku'] is not None else oldInv['sku'],
    #         itemCondition = newInv['itemCondition'] if newInv['itemCondition'] is not None else oldInv['itemCondition'],
    #         comment = newInv['comment'] if newInv['comment'] is not None else oldInv['comment'],
    #         link = newInv['link'] if newInv['link'] is not None else oldInv['link'],
    #         platform = newInv['platform'] if newInv['platform'] is not None else oldInv['platform'],
    #         shelfLocation = newInv['shelfLocation'] if newInv['shelfLocation'] is not None else oldInv['shelfLocation'],
    #         amount = newInv['amount'] if newInv['amount'] is not None else oldInv['amount']
    #     )
    # except:
    #     return Response('Invalid Inventory Info', status.HTTP_400_BAD_REQUEST)
        
    # update inventory
    res = collection.update_one(
        { 'sku': sku },
        {
            '$set': 
            {
                'sku': newInventory.sku,
                'itemCondition': newInventory.itemCondition,
                'comment': newInventory.comment,
                'link': newInventory.link,
                'platform': newInventory.platform,
                'shelfLocation': newInventory.shelfLocation,
                'amount': newInventory.amount
            }
        }
    )
    
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
    res = collection.find_one({'sku': sku}, {'time': 1})
    if not res:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    

    # calculate time left to delete, prevent delete if result delta seconds is negative
    # convert form time string to time obj
    timeCreated = datetime.strptime(res['time'], time_format)
    one_day_later = timeCreated + timedelta(days=1)
    today = datetime.now()
    canDel = (one_day_later - today).total_seconds() > 0
    
    # perform deletion or throw error
    if canDel:
        de = collection.delete_one({'sku': sku})
        return Response('Inventory Deleted', status.HTTP_200_OK)
    return Response('Cannot Delete Inventory After 24H, Please Contact Admin', status.HTTP_403_FORBIDDEN)