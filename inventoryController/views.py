import os
import time
from django.shortcuts import render, HttpResponse
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# create inventory
def createInventory(request):
    if request.method == "PUT":
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
        print(request)
        
def deleteInventory(request):
    if request.method == "DELETE":
        print(request)

def updateInventory(request):
    if request.method == "POST":
        print(request)
        
            
def getInventoryBySku(request):
    if request.method == "GET":
        print(request)
    
