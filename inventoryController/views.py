import os
import time
from django.shortcuts import render, HttpResponse
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# create inventory
def createInventory(request):
    if request.method == "PUT":
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
    
