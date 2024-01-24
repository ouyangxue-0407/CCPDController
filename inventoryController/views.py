import os
import re
import requests
from scrapy.http import HtmlResponse
from datetime import datetime, timedelta
from inventoryController.models import InventoryItem
from CCPDController.scrape_utils import extract_urls, getImageUrl, getMrsp, getTitle
from CCPDController.utils import decodeJSON, get_db_client, sanitizeNumber, sanitizeSku, convertToTime, getIsoFormatNow
from CCPDController.permissions import IsQAPermission, IsAdminPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from fake_useragent import UserAgent
from bson.objectid import ObjectId
from collections import Counter
from CCPDController.chat_gpt_utils import generate_short_product_title, generate_full_product_title
import pymongo
import pandas as pd
from bs4 import BeautifulSoup

# pymongo
db = get_db_client()
qa_collection = db['Inventory']
user_collection = db['User']
ua = UserAgent()

# query param sku for inventory db row
# sku: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    
    if not sku:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)

    # find the Q&A record
    res = qa_collection.find_one({'sku': sku}, {'_id': 0})
    if not res:
        return Response('Record Not Found', status.HTTP_400_BAD_REQUEST)
    
    # get user info
    user = user_collection.find_one({'_id': ObjectId(res['owner'])}, {'name': 1, 'userActive': 1, '_id': 0})
    if not user:
        return Response('Owner Not Found', status.HTTP_404_NOT_FOUND)
    
    # replace owner field in response
    res['owner'] = user
    return Response(res, status.HTTP_200_OK)
        
# get all inventory by QA personal
# id: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryByOwnerId(request, page):
    try:
        body = decodeJSON(request.body)
        ownerId = str(ObjectId(body['id']))
        
        # TODO: make limit a path parameter
        # get targeted page
        limit = 10
        skip = page * limit
    except:
        return Response('Invalid Id', status.HTTP_400_BAD_REQUEST)
     
    # return all inventory from owner in array
    arr = []
    skip = page * limit
    for inventory in qa_collection.find({ 'owner': ownerId }).sort('sku', pymongo.DESCENDING).skip(skip).limit(limit):
        inventory['_id'] = str(inventory['_id'])
        arr.append(inventory)
    
    return Response(arr, status.HTTP_200_OK)


# for charts and overview data
# id: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryInfoByOwnerId(request):
    try:
        body = decodeJSON(request.body)
        ownerId = str(ObjectId(body['id']))
    except:
        return Response('Invalid Id', status.HTTP_400_BAD_REQUEST)
     
    # array of all inventory
    arr = []
    cursor = qa_collection.find({ 'owner': ownerId }, { 'itemCondition': 1 })
    for inventory in cursor:
        # inventory['_id'] = str(inventory['_id'])
        arr.append(inventory['itemCondition'])
    
    itemCount = Counter()
    for condition in arr:
        itemCount[condition] += 1 

    return Response(dict(itemCount), status.HTTP_200_OK)

# create single inventory Q&A record
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def createInventory(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)

    # if sku exist return conflict
    inv = qa_collection.find_one({'sku': body['sku']})
    if inv:
        return Response('SKU Already Existed', status.HTTP_409_CONFLICT)
    
    # try:
    print(body['time'])
    # construct new inventory
    newInventory = InventoryItem(
        # time=str(ctime(time())),
        time=body['time'],
        sku=sku,
        itemCondition=body['itemCondition'],
        comment=body['comment'],
        link=body['link'],
        platform=body['platform'],
        shelfLocation=body['shelfLocation'],
        amount=body['amount'],
        owner=body['owner'],
        ownerName=body['ownerName'],
        marketplace=body['marketplace']
    )
    # pymongo need dict or bson object
    res = qa_collection.insert_one(newInventory.__dict__)
    # except:
    #     return Response('Invalid Inventory Information', status.HTTP_400_BAD_REQUEST)
    return Response('Inventory Created', status.HTTP_200_OK)

# query param sku and body of new inventory info
# sku: string
# newInventory: Inventory
"""
{
    sku: xxxxx,
    newInv: {
        sku,
        itemCondition,
        comment,
        link,
        platform,
        shelfLocation,
        amount
    }
}
"""
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def updateInventoryBySku(request, sku):
    try:
        # convert to object id
        body = decodeJSON(request.body)
        sku = sanitizeSku(int(sku))
        if not sku:
            return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
        
        # check body
        newInv = body['newInventoryInfo']
        newInventory = InventoryItem(
            time = newInv['time'],
            sku = newInv['sku'],
            itemCondition = newInv['itemCondition'],
            comment = newInv['comment'],
            link = newInv['link'],
            platform = newInv['platform'],
            shelfLocation = newInv['shelfLocation'],
            amount = newInv['amount'],
            owner = newInv['owner'],
            ownerName = newInv['ownerName'],
            marketplace = newInv['marketplace']
        )
    except:
        return Response('Invalid Inventory Info', status.HTTP_406_NOT_ACCEPTABLE)
    
    # check if inventory exists
    oldInv = qa_collection.find_one({ 'sku': sku })
    if not oldInv:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    # update inventory
    res = qa_collection.update_one(
        { 'sku': sku },
        {
            '$set': 
            {
                'amount': newInventory.amount,
                'itemCondition': newInventory.itemCondition,
                'platform': newInventory.platform,
                'shelfLocation': newInventory.shelfLocation,
                'comment': newInventory.comment,
                'link': newInventory.link,
                'marketplace': newInventory.marketplace
            }
        }
    )
    
    # return update status 
    if not res:
        return Response('Update Failed', status.HTTP_404_NOT_FOUND)
    return Response('Update Success', status.HTTP_200_OK)

# delete inventory by sku
# QA personal can only delete record created within 24h
# sku: string
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission])
def deleteInventoryBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    if not sku:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    
    # pull time
    res = qa_collection.find_one({'sku': sku}, {'time': 1})
    if not res:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    

    # calculate time left to delete, prevent delete if result delta seconds is negative
    # convert form time string to time obj
    timeCreated = convertToTime(res['time'])
    one_day_later = timeCreated + timedelta(days=1)
    today = datetime.now()
    canDel = (one_day_later - today).total_seconds() > 0
    
    # perform deletion or throw error
    if canDel:
        de = qa_collection.delete_one({'sku': sku})
        return Response('Inventory Deleted', status.HTTP_200_OK)
    return Response('Cannot Delete Inventory After 24H, Please Contact Admin', status.HTTP_403_FORBIDDEN)

# get all shelf location for existing inventories
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllShelfLocations():
    arr = qa_collection.distinct('shelfLocation')
    return Response(arr, status.HTTP_200_OK)

# description: string
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def generateDescriptionBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    
    print(sku)
    # grab comment from that specific item
    comment = qa_collection.find_one({'sku': sku}, {'comment': 1})
    if not comment:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    # call chat gpt to generate description
    lead = generate_short_product_title('USED LIKE NEW - MISISNG 2 ACCESSORIES - Double Canister Dry Food Dispenser Convenient Storage')
    # full_lead = generate_full_product_title(comment['comment'], '')
    
    return Response(lead, status.HTTP_200_OK)

# return mrsp from amazon for given sku
# sku: string
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def scrapeInfoBySkuAmazon(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeNumber(int(body['sku']))
    except:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    
    # find target inventory
    target = qa_collection.find_one({ 'sku': sku })
    if not target:
        return Response('No Such Inventory', status.HTTP_404_NOT_FOUND)

    # return error if not amazon link or not http
    link = target['link']
    link = "https://www.amazon.ca/Brightwell-Aquatics-AminOmega-Supplement-Aquaria/dp/B001DCV0ZI/ref=dp_fod_sccl_1/138-3560016-0966344?pd_rd_w=qG68t&content-id=amzn1.sym.e943220f-f90d-493f-b9ae-af4c3e457137&pf_rd_p=e943220f-f90d-493f-b9ae-af4c3e457137&pf_rd_r=HAX5TTWXAFJYSH2XSWVJ&pd_rd_wg=kvVBw&pd_rd_r=a446f094-3404-4173-abbc-8200b7f4c00e&pd_rd_i=B001DCV1PC&th=1"
    if 'amazon' not in link and 'http' not in link and 'a.co' not in link:
        return Response('Invalid URL', status.HTTP_400_BAD_REQUEST)
    
    # extract the first http url
    link = extract_urls(link)
    # generate header with random user agent
    headers = {
        'User-Agent': f'user-agent={ua.random}',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # get raw html and parse it with scrapy
    # TODO: use 10 proxy service to incraese scraping speed
    payload = {
        'title': '',
        'mrsp': '',
        'imgUrl': ''
    }
    
    # request the raw html from Amazon
    rawHTML = requests.get(url=link, headers=headers).text
    response = HtmlResponse(url=link, body=rawHTML, encoding='utf-8')
    try:
        payload['title'] = getTitle(response)
    except:
        return Response('Failed to Get Title', status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        payload['mrsp'] = getMrsp(response)
    except:
        return Response('Failed to Get MRSP', status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        payload['imgUrl'] = getImageUrl(response)
    except:
        return Response('No Image URL Found', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(payload, status.HTTP_200_OK)

# return mrsp from home depot for given sku
# sku: string
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def scrapePriceBySkuHomeDepot(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeNumber(int(body['sku']))
    except:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    
    # find target inventory
    target = qa_collection.find_one({ 'sku': sku })
    if not target:
        return Response('No Such Inventory', status.HTTP_404_NOT_FOUND)

    # check if url is home depot
    url = target['link']
    if 'homedepot' not in url or 'http' not in url:
        return Response('Invalid URL', status.HTTP_400_BAD_REQUEST)
    
    # extract url incase where the link includes title
    start_index = target['link'].find("https://")
    if start_index != -1:
        url = target['link'][start_index:]
        print("Extracted URL:", url)

    # generate header with random user agent
    headers = {
        'User-Agent': f'user-agent={ua.random}',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    # get raw html and parse it with scrapy
    # TODO: purchase and implement proxy service
    rawHTML = requests.get(url=url, headers=headers).text
    response = HtmlResponse(url=url, body=rawHTML, encoding='utf-8')
    
    # HD Canada className = hdca-product__description-pricing-price-value
    # HD Canada itemprop="price"
    # <span itemprop="price">44.98</span>
    # HD US className = ????
    
    

    # grab the fist span element encountered tagged with class 'a-price-whole' and extract the text
    price = response.selector.xpath('//span/text()').extract()
    # price = price[0].replace('$', '')
    
    if not price:
        return Response('No Result', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(price, status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def sendCSV(request):
    body = decodeJSON(request.body)
    # relative path
    path = body['path']

    # joint file location with relative path
    dirName = os.path.dirname(__file__)
    fileName = os.path.join(dirName, path)
    
    print(getIsoFormatNow())
    
    # parse csv to pandas data frame
    data = pd.read_csv(filepath_or_buffer=fileName)
    
    # loop pandas dataframe
    for index in data.head().index:
        # time convert to iso format
        # original: 12/22/2023 5:54pm
        # targeted: 2024-01-03T05:00:00.000   optional: -05:00 (EST is -5)
        data['time'][index] = datetime.strptime(data['time'][index], "%m/%d/%Y %I:%M%p").isoformat()
        # print(time)
        
        # remove all html tags
        cleanLink = BeautifulSoup(data['link'][index], "lxml").text
        
        # item condition set to capitalized
        itemCondition = data['itemCondition'][index]
        
        # platform
        platform = data['platform'][index]
        

        
    # set output copy path
    # output = os.path.join(dirName, 'output.csv')
    # data.to_csv(output)
        
    return Response(str(data.tail()), status.HTTP_200_OK)