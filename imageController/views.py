import os
import time
from django.shortcuts import render, HttpResponse
# from azure.storage.blob import BlobServiceClient
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# MongoDB
client = MongoClient(os.getenv('DATABASE_URL'))
db = client['CCPD']
collection = db['Inventory']

# single image download
def downloadSingleImage(request):
    if request.method == "GET":
        print(request)
        return collection.find()
    
# single image download
def bulkDownloadImages(request):
    if request.method == "GET":
        print(request)
        return collection.find()

# single image upload
def uploadSingleImage(request):
    if request.method == "GET":
        print(request)
        newDocument = {
            "time": time.time(),
            "sku": 11000,
            "description": "example inventory, please do not buy",
            "condition": "new",
            "owner": "Michael"
        }
        collection.insert_one(newDocument)
        return HttpResponse()

# bulk image upload
def bulkUploadImages(request):
    print(request)
    return HttpResponse("Multiple image upload happens here")
