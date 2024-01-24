import os
import io
import random
import requests
import pillow_heif
from PIL import Image
import datetime
from datetime import timedelta
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from CCPDController.utils import decodeJSON, getNDayBefore, sanitizeNumber, sanitizeString, getBlobTimeString, get_db_client
from CCPDController.authentication import JWTAuthentication
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from dotenv import load_dotenv
from urllib import parse
import pymongo
load_dotenv()

# Mongo DB
db = get_db_client()
qa_collection = db['Inventory']

# Azure Blob
account_name = 'CCPD'
container_name = 'product-image'
# blob client object from azure access keys
azure_blob_client = BlobServiceClient.from_connection_string(os.getenv('SAS_KEY'))
# container handle for product image
product_image_container_client = azure_blob_client.get_container_client(container_name)

# return array of all image url from owner
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getUrlsByOwner(request):
    try:
        body = decodeJSON(request.body)
        sanitizeString(body['owner'])
    except:
        return Response('Invalid Owner Id', status.HTTP_400_BAD_REQUEST)
    
    # format: Wed Jan 10 2024
    # filter image created within 2 days
    time = "\"time\"<='" + getNDayBefore(2, getBlobTimeString()) + "'"
    owner = "\"owner\"='" + body['owner'] + "'"
    query = owner + " AND " + time
    print(query)
    blob_list = product_image_container_client.find_blobs_by_tags(filter_expression=query)
    
    arr = []
    for blob in blob_list:
        blob_client = product_image_container_client.get_blob_client(blob.name)
        arr.append(blob_client.url)

    if len(arr) < 1:
        return Response('No Images Found for Owner', status.HTTP_404_NOT_FOUND)
    return Response(arr, status.HTTP_200_OK)

# sku: str
# returns an array of image uri (for public access)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getUrlsBySku(request):
    try:
        body = decodeJSON(request.body)
        sanitizeNumber(int(body['sku']))
    except:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    sku = "sku = '" + body['sku'] + "'"
    blob_list = product_image_container_client.find_blobs_by_tags(filter_expression=sku)
    
    arr = []
    for blob in blob_list:
        blob_client = product_image_container_client.get_blob_client(blob.name)
        arr.append(blob_client.url)
        
    if len(arr) < 1:
        return Response('No images found for sku', status.HTTP_404_NOT_FOUND)
    return Response(arr, status.HTTP_200_OK)

# single image upload
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def uploadImage(request, ownerId, owner, sku):
    # request body content type is file form therefore only binary data allowed
    # sku will be in the path parameter
    # request.FILES looks like this and is a multi-value dictionary
    # {
    #     'IMG_20231110_150642.jpg': [<InMemoryUploadedFile: IMG_20231110_150642.jpg (image/jpeg)>], 
    #     'IMG_20231110_150000.jpg': [<InMemoryUploadedFile: IMG_20231110_150000.jpg (image/jpeg)>]
    # }
    
    # azure allow tags on each blob
    inventory_tags = {
        "sku": sku, 
        "time": getBlobTimeString(), # format: Wed Jan 10 2024
        "owner": ownerId,
        "ownerName": owner
    }
    
    # loop the files in the request
    for name, value in request.FILES.items():
        # images will be uploaded to the folder named after their sku
        img = value
        imageName = sku + '/' + sku + '_' + name
        
        # process apples photo format
        if 'heic' in name or 'HEIC' in name:
            # convert image to jpg
            heicFile = pillow_heif.read_heif(value)
            byteImage = Image.frombytes (
                heicFile.mode,
                heicFile.size,
                heicFile.data,
                "raw"
            )
            buf = io.BytesIO()
            byteImage.save(buf, format="JPEG")
            img = buf.getvalue()
            # change extension to jpg
            base_name = os.path.splitext(name)[0]
            imageName = sku + '/' + base_name + '.' + 'jpg'
        
        try:
            res = product_image_container_client.upload_blob(imageName, img, tags=inventory_tags)
        except ResourceExistsError:
            return Response(imageName + 'Already Exist!', status.HTTP_409_CONFLICT)
    return Response(res.url, status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def deleteImageByName(request):
    body = decodeJSON(request.body)
    sku = body['sku']
    name = body['name']
    
    # azure automatically unquote all % in url
    imageName = parse.unquote(sku + '/' + name)
    try:
        res = product_image_container_client.delete_blob(imageName)
    except:
        return Response('No Such Image', status.HTTP_404_NOT_FOUND)
    return Response('Image Deleted', status.HTTP_200_OK)