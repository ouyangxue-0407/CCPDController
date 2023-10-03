import os
import json
from time import time, ctime
import datetime
from django.shortcuts import render, HttpResponse
from inventoryController.models import InventoryItem
from pymongo import MongoClient
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
load_dotenv()

# MongoDB
client = MongoClient(os.getenv('DATABASE_URL'))
db = client['CCPD']
collection = db['Inventory']

# create single inventory
@csrf_exempt
def createInventory(request):
    if request.method == "PUT":
        # convert body from json to object
        body = json.loads(request.body.decode('utf-8'))
        
        # construct new inventory
        newInventory = InventoryItem(
            time=str(ctime(time())),
            sku=body["sku"],
            condition=body["condition"],
            description=body["description"],
            owner=body["owner"],
            images=body["images"]
        )
        
        # pymongo need dict or bson object
        res = collection.insert_one(newInventory.__dict__)
        return HttpResponse(newInventory)
        
# delete inventory by sku
def deleteInventory(request):
    if request.method == "DELETE":
        print(request)

# query param sku and body of new inventory info
def updateInventory(request):
    if request.method == "POST":
        print(request)

# query param sku for inventory db row
def getInventoryBySku(request):
    if request.method == "GET":
        
        
        print(request)
        
        
# get all inventory by QA personal 
def getInventoryByOwner(request):
    if request.method == "GET":
        
        collection.find_one({
            # owner: request
        })
        print (request)
    
