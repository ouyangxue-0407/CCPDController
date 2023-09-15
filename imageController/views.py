import os
import json
from time import time, ctime
from imageController.models import InventoryImage
from django.shortcuts import render, HttpResponse
from azure.storage.blob import BlobServiceClient, BlobClient
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# Azure Blob
# client = BlobServiceClient(os.getenv('BLOB_KEY'),'QATeam')
# container = client.get_container_client('product-image')

# MongoDB
client = MongoClient(os.getenv('DATABASE_URL'))
db = client['CCPD']
collection = db['InventoryImage']

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


    return HttpResponse("Please use GET method")

# download all images related to 1 sku
def downloadAllImagesBySKU(request):
    if request.method == 'GET':
        print(request)

# single image upload
@csrf_exempt
def uploadSingleImage(request):
    if request.method == 'PUT' and request.body:
        
        # decode body to python object
        body = json.loads(request.body.decode('utf-8'))
        blob = BlobClient.from_connection_string(conn_str=os.getenv('BLOB_KEY'), container_name="product-image", blob_name=body["sku"])
    
        blob.upload_blob(body["images"][0])
        
        azureImageArr = []
        # push to azure blob
        # container.upload_blob('')
        # for x in body['images']:
        #     with open (x, 'r') as file:
        #         print(file)
                # await container.upload_blob(file)

        # build inventory image data object
        newInventoryImage = InventoryImage(
            time = str(ctime(time())),
            sku = body["sku"],
            owner = body["owner"],
            images = body["images"]
        )
        
        # push data to MongoDB
        # await collection.insert_one(newInventoryImage.__dict__)

        return HttpResponse("upload single image")
    return HttpResponse("Please upload using PUT method with JSON body")

# bulk image upload
def bulkUploadImages(request):
    print(request)
    return HttpResponse("Multiple image upload happens here")

# list blob containers
def listBlobContainers(request):
    if request.method == 'GET':
        print('list blob container')
        blob_list = container.list_blobs()
        
        # blob_service_client = BlobServiceClient(account_url=os.getenv('CONTAINER_URL'), credential=os.getenv('BLOB_KEY'))
        return HttpResponse(blob_list)