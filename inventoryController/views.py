from time import time, ctime
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from inventoryController.models import InventoryItem
from CCPDController.utils import decodeJSON, get_db_client, sanitizeSku, sanitizeName, removeStr
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId

# pymongo
db = get_db_client()
collection = db['Inventory']

# query param sku for inventory db row
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission, IsAdminPermission])
async def getInventoryBySku(request):
    body = decodeJSON(request.body)
    sku = sanitizeSku(body['sku'])
    
    if sku:
        res = await collection.find_one({'sku': sku})
        return Response(res)
    else:
        return Response('Invalid SKU')     
        
# get all inventory by QA personal
@api_view(['GET'])
def getInventoryByOwnerId(request):
    body = decodeJSON(request.body)
    print(body['_id'])
    
    try:
        ownerId = ObjectId(body['_id'])
    except:
        return Response('Invalid Id', status.HTTP_400_BAD_REQUEST)
    
    
    # need a fix
    arr = []
    for inventory in collection.find({ 'owner': str(ownerId) }):
        arr.append(inventory)
    
    print(arr)
    
    return Response(arr, status.HTTP_200_OK)

# create single inventory Q&A record
@csrf_exempt
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission, IsAdminPermission])
async def createInventory(request):
    body = decodeJSON(request.body)
    sku = sanitizeSku(body['sku'])
    comment = removeStr(body['comment'])

    # if sku exist return error
    await collection.find_one({'sku': body['sku']})
    
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
    return Response(newInventory)

# query param sku and body of new inventory info
# sku
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission, IsAdminPermission])
def updateInventoryBySku(request):
    try:
        # convert to object id
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid User ID', status.HTTP_400_BAD_REQUEST)
    
    
    # update inventory
    res = collection.update_one(
        {
            'sku': sku,
        },
        { '$set': 
            {
                'password': 
                ''
            } 
        }
    )


# delete inventory by sku
# admin only
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
async def deleteInventoryBySku(request):
    body = decodeJSON(request.body)
    
    # delete inventory by sku
    await collection.find_one({ 'sku': body['sku'] })
