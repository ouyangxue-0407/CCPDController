from django.shortcuts import render, HttpResponse
# from azure.storage.blob import BlobServiceClient
import requests

# service = BlobServiceClient(account_url="https://<my_account_name>.blob.core.windows.net", credential="<account_access_key>")

# single image upload
def singleImage(request):

    print(request)    
    return HttpResponse('single image upload happens here')

# bulk image upload
def bulkImage(request):
    print(request)
    return HttpResponse("Multiple image upload happens here")
