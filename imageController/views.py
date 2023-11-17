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

# sample code from Microsoft for generating user delegation sas key
# def request_user_delegation_key(self, blob_service_client: BlobServiceClient) -> UserDelegationKey:
#     # Get a user delegation key that's valid for 1 day
#     delegation_key_start_time = datetime.datetime.now(datetime.timezone.utc)
#     delegation_key_expiry_time = delegation_key_start_time + datetime.timedelta(days=1)

#     user_delegation_key = blob_service_client.get_user_delegation_key(
#         key_start_time=delegation_key_start_time,
#         key_expiry_time=delegation_key_expiry_time
#     )

#     return user_delegation_key

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
def uploadImage(request, sku, owner):
    # request body is unreadable binary code
    # sku will be in the path parameter
    # request.FILES looks like this and is a multi-value dictionary
    # {
    #     'IMG_20231110_150642.jpg': [<InMemoryUploadedFile: IMG_20231110_150642.jpg (image/jpeg)>], 
    #     'IMG_20231110_150000.jpg': [<InMemoryUploadedFile: IMG_20231110_150000.jpg (image/jpeg)>]
    # }
    
    # loop the files in the request
    for name, value in request.FILES.items():
        # add tags of owner and time info
        inventory_tags = {
            "sku": sku, 
            "time": str(ctime(time())),
            "owner": owner
        }
        # images will be uploaded to the folder named after their sku
        imageName = sku + '/' + sku + '_' + name
        try:
            res = product_image_container.upload_blob(imageName, value.file, tags=inventory_tags)
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

    return Response(res.url, status.HTTP_200_OK)

# list blob containers
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def listBlobContainers(request):
    
    
    return Response('Listing blob containers......', status.HTTP_200_OK)
    