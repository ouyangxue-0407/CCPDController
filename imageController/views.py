from io import BytesIO
import os
import json
from time import time, ctime
from imageController.models import InventoryImage
from django.shortcuts import render, HttpResponse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from CCPDController.utils import decodeJSON, get_db_client, sanitizeSku, sanitizeName, removeStr
from CCPDController.authentication import JWTAuthentication
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# Azure Blob
# blob client object from azure access keys
azure_blob_client = BlobServiceClient.from_connection_string(os.getenv('SAS_KEY'))
# container handle for product image
product_image_container = azure_blob_client.get_container_client("product-image")

# MongoDB
db = get_db_client()
collection = db['InventoryImage']

# download all images related to 1 sku
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def downloadAllImagesBySKU(request):
    
    print(request.data)
    return Response('here is all the image for sku: ', status.HTTP_200_OK)

# single image upload
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def uploadImage(request, sku):
    # request body is unreadable binary code
    # sku will be in the path parameter
    # request.FILES looks like this and is a multi-value dictionary
    # {
    #     'IMG_20231110_150642.jpg': [<InMemoryUploadedFile: IMG_20231110_150642.jpg (image/jpeg)>], 
    #     'IMG_20231110_150000.jpg': [<InMemoryUploadedFile: IMG_20231110_150000.jpg (image/jpeg)>]
    # }
    for name, value in request.FILES.items():
        imageName = sku + '/' + sku + '_' + name
        try:
            res = product_image_container.upload_blob(imageName, value.file)
            print(res.url)
        except ResourceExistsError:
            return Response(imageName + 'Already Exist!', status.HTTP_409_CONFLICT)
        
    # construct database row object
    # newInventoryImage = InventoryImage(
    #     time = str(ctime(time())),
    #     sku = body["sku"],
    #     owner = body["owner"],
    #     images = body["images"]
    # )
    
    # push data to MongoDB
    # await collection.insert_one(newInventoryImage.__dict__)

    return Response("Upload Success", status.HTTP_200_OK)

# list blob containers
def listBlobContainers(request):
    if request.method == 'GET':
        return HttpResponse(product_image_container.list_blob_names())