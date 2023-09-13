import os
import time
import json
from django.shortcuts import render, HttpResponse
# from azure.storage.blob import BlockBlobService
from pymongo import MongoClient
from inventoryController.models import InventoryItem
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

# Azure Blob

# MongoDB
client = MongoClient(os.getenv('DATABASE_URL'))
db = client['CCPD']
collection = db['Inventory']

# single image download
def downloadSingleImage(request):
    if request.method == "GET":
        print(request)
        return collection.find()
    return HttpResponse("Please use GET method")
    
    
# single image download
def bulkDownloadImages(request):
    if request.method == "GET":
        print(request)
        return collection.find()
    return HttpResponse("Please use GET method")

# download all images related to 1 sku
def downloadAllImagesBySKU(request):
    if request.method == "GET":
        print(request)


# single image upload
@csrf_exempt
def uploadSingleImage(request):
    if request.method == "PUT":
        obj = json.loads(request.body.decode('utf-8'))
        print(obj)
        print(obj.sku)
        # obj = request.body.decode('utf-8')
        # print("obj: " + obj)
        # body = json.loads(obj)
        # print("body: " + body)
        
        
        # newInventory = InventoryItem(
        #     time=time.time(),
        #     sku=body.sku, 
        #     description=body.description, 
        #     owner=body.owner
        # )
        
        # newDocument = {
        #     "time": time.time(),
        #     "sku": 11000,
        #     "description": "example inventory, please do not buy",
        #     "condition": "new",
        #     "owner": "Michael",
        #     "images": [
        #         "link1",
        #         "link2",
        #         "link3",
        #         "link4"
        #     ]
        # }
        # res = collection.insert_one(newInventory)
        return HttpResponse('upload single image')
    return HttpResponse("Please use PUT method")


# bulk image upload
def bulkUploadImages(request):
    print(request)
    return HttpResponse("Multiple image upload happens here")
