import os
import time
import json
from django.shortcuts import render, HttpResponse
from azure.storage.blob import BlobServiceClient, BlobClient
from pymongo import MongoClient
from inventoryController.models import InventoryItem
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

# Azure Blob
client = BlobServiceClient(os.getenv('BLOB_KEY'),'QATeam')
# blobClient = client.get_blob_client('product-image', '')
# print(blobClient.account_name)
# container_client = blob_service_client.get_container_client(container=container_name)

# MongoDB
client = MongoClient(os.getenv('DATABASE_URL'))
db = client['CCPD']
collection = db['Inventory']

# single image download
def downloadSingleImage(request):
    if request.method == 'GET':
        print(request)
        return collection.find()
    return HttpResponse("Please use GET method")
    
# single image download
def bulkDownloadImages(request):
    if request.method == 'GET':
        print(request)
        return collection.find()
    return HttpResponse("Please use GET method")

# download all images related to 1 sku
def downloadAllImagesBySKU(request):
    if request.method == 'GET':
        print(request)

# single image upload
@csrf_exempt
def uploadSingleImage(request):
    if request.method == 'PUT':
        obj = json.loads(request.body.decode('utf-8'))
        print(obj)
        print(obj.sku)
        
        # fetch inventory with matching sku
        
        # if exist add image handle to it
        
        # if not, create empty row with only image urls filled up
        

        return HttpResponse("upload single image")
    return HttpResponse("Please use PUT method")

# bulk image upload
def bulkUploadImages(request):
    print(request)
    return HttpResponse("Multiple image upload happens here")

# list blob containers
def listBlobContainers(request):
    if request.method == 'GET':
        blob_service_client = BlobServiceClient(account_url=os.getenv('ACCOUNT_URL'), credential=os.getenv('BLOB_KEY'))
        return blob_service_client.get_account_information()