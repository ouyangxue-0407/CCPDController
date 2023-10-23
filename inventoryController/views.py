from time import time, ctime
from django.shortcuts import HttpResponse
from inventoryController.models import InventoryItem
from CCPDController.utils import decodeJSON, get_db_client, sanitizeSku, sanitizeName, removeStr
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

# pymongo
db = get_db_client()
collection = db['Inventory']

# query param sku for inventory db row
@api_view(['GET'])
def getInventoryBySku(request):
    body = decodeJSON(request.body)
    sku = sanitizeSku(body['sku'])
    
    if sku:
        res = collection.find_one({'sku': sku})
        return HttpResponse(res)
    else:
        return HttpResponse('Invalid SKU')    

        
        
# get all inventory by QA personal 
def getInventoryByOwner(request):
    if request.method == 'GET':
        body = decodeJSON(request.body)
        
        collection.find_one({
            
        })
        print (request)
    
       

# create single inventory Q&A record
@csrf_exempt
def createInventory(request):
    if request.method == 'PUT':
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
        comment = removeStr(body['comment'])
        
        
        # if sku exist return error
        collection.find_one({'sku': body['sku']})
        
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
            # images=body["images"] if body["images"]==None else None
        )
        
        # pymongo need dict or bson object
        res = collection.insert_one(newInventory.__dict__)
        return HttpResponse(newInventory)


# query param sku and body of new inventory info
def updateInventoryById(request):
    if request.method == 'POST':
        body = decodeJSON(request.body)
        
        # query if inventory exist
        print(request)

# delete inventory by sku
def deleteInventoryBySku(request):
    if request.method == 'DELETE':
        body = decodeJSON(request.body)
        
        # delete inventory by sku
        collection.find_one({ 'sku': body['sku'] })
