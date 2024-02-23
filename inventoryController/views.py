from enum import unique
import os
import requests
from scrapy.http import HtmlResponse
from datetime import datetime
from inventoryController.models import InstockInventory, InventoryItem
from CCPDController.scrape_utils import extract_urls, getCurrency, getImageUrl, getMsrp, getTitle
from CCPDController.utils import (
    convertToAmountPerDayData, decodeJSON, 
    get_db_client, 
    getIsoFormatInv, 
    getNDayBeforeToday, 
    populateSetData, 
    sanitizeNumber, 
    sanitizeSku, 
    convertToTime, 
    getIsoFormatNow, 
    qa_inventory_db_name, 
    getIsoFormatNow, 
    sanitizeString
)
from CCPDController.permissions import IsQAPermission, IsAdminPermission, IsSuperAdminPermission
from CCPDController.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from fake_useragent import UserAgent
from bson.objectid import ObjectId
from collections import Counter
from CCPDController.chat_gpt_utils import generate_description, generate_title
from inventoryController.unpack_filter import unpackInstockFilter
import pymongo
import pandas as pd
from bs4 import BeautifulSoup

# pymongo
db = get_db_client()
qa_collection = db[qa_inventory_db_name]
instock_collection = db['InstockInventory']
user_collection = db['User']
ua = UserAgent()


'''
QA Inventory stuff
'''
# query param sku for inventory db row
# sku: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeNumber(int(body['sku']))
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)

    # find the Q&A record
    try:
        res = qa_collection.find_one({'sku': sku}, {'_id': 0})
    except:
        return Response('Cannot Fetch From Database', status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not res:
        return Response('Record Not Found', status.HTTP_400_BAD_REQUEST)
    
    # replace owner field in response
    return Response(res, status.HTTP_200_OK)

# get all inventory of owner by page
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

# get all qa inventory by qa name
# ownerName: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getInventoryByOwnerName(request):
    # try:
    body = decodeJSON(request.body)
    name = sanitizeString(body['ownerName'])
    currPage = sanitizeNumber(body['page'])
    # except:
    #     return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
        
    # get all qa inventory
    # default item per page is 10
    skip = currPage * 10
    res = qa_collection.find({ 'ownerName': name }, { '_id': 0 }).sort('sku', pymongo.DESCENDING).skip(skip).limit(10)
    if not res:
        return Response('No Inventory Found', status.HTTP_200_OK)
    
    # make array of items
    arr = []
    for item in res:
        arr.append(item)
 
    return Response(arr, status.HTTP_200_OK)

# get all qa inventory condition stats for graph by qa name
# ownerName: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsQAPermission | IsAdminPermission])
def getQAConditionInfoByOwnerName(request):
    # try:
    body = decodeJSON(request.body)
    name = sanitizeString(body['ownerName'])
    # except:
    #     return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    
    arr = []
    # array of all inventory
    condition = []
    con = qa_collection.find({ 'ownerName': name }, { 'itemCondition': 1 })
    if not con:
        return Response('No Inventory Found', status.HTTP_204_NO_CONTENT)
    for inventory in con:
        arr.append(inventory['itemCondition'])
    
    # make data object for charts
    itemCount = Counter()
    for condition in arr:
        itemCount[condition] += 1   
    return Response(dict(itemCount))

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
    
    try:
        # construct new inventory
        newInventory = InventoryItem(
            time = getIsoFormatNow(),
            sku = sku,
            itemCondition = body['itemCondition'],
            comment = body['comment'],
            link = body['link'],
            platform = body['platform'],
            shelfLocation = body['shelfLocation'],
            amount = body['amount'],
            owner = body['owner'],
            ownerName = body['ownerName'],
            marketplace = body['marketplace']
        )
        # pymongo need dict or bson object
        res = qa_collection.insert_one(newInventory.__dict__)
    except:
        return Response('Invalid Inventory Information', status.HTTP_400_BAD_REQUEST)
    return Response('Inventory Created', status.HTTP_200_OK)

# update qa record by sku
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
            owner =  newInv['owner'] if 'owner' in newInv else '',
            ownerName = newInv['ownerName'],
            marketplace = newInv['marketplace'] if 'marketplace' in newInv else ''
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
    
    # pull time created
    res = qa_collection.find_one({'sku': sku}, {'time': 1})
    if not res:
        return Response('Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    # check if the created time is within 2 days (175000 seconds)
    timeCreated = convertToTime(res['time'])
    createdTimestamp = datetime.timestamp(timeCreated)
    today = datetime.now()
    todayTimestamp = datetime.timestamp(today)
    
    two_days = 175000
    canDel = (todayTimestamp- createdTimestamp) < two_days
    
    # perform deletion or throw error
    if canDel:
        qa_collection.delete_one({'sku': sku})
        return Response('Inventory Deleted', status.HTTP_200_OK)
    return Response('Cannot Delete Inventory After 24H, Please Contact Admin', status.HTTP_403_FORBIDDEN)

# get all QA shelf location
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllQAShelfLocations(request):
    try:
        arr = qa_collection.distinct('shelfLocation')
    except:
        return Response('Cannot Fetch From Database', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(arr, status.HTTP_200_OK)


'''
In-stock stuff
'''
# currPage: number
# itemsPerPage: number
# filter: { 
#   timeRangeFilter: { from: string, to: string }, 
#   conditionFilter: string, 
#   platformFilter: string,
#   marketplaceFilter: string,
#   ownerFilter: string,
#   shelfLocationFilter: string[],
#   keywordFilter: string[],
# }
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getInstockByPage(request):
    body = decodeJSON(request.body)
    sanitizeNumber(body['page'])
    sanitizeNumber(body['itemsPerPage'])
    query_filter = body['filter']

    fil = {}
    fil = unpackInstockFilter(query_filter, fil)

    try:
        arr = []
        skip = body['page'] * body['itemsPerPage']
        
        # see if filter is applied to determine the query
        if fil == {}:
            query = instock_collection.find().sort('sku', pymongo.DESCENDING).skip(skip).limit(body['itemsPerPage'])
            count = instock_collection.count_documents({})
        else:
            query = instock_collection.find(fil).sort('sku', pymongo.DESCENDING).skip(skip).limit(body['itemsPerPage'])
            count = instock_collection.count_documents(fil)

        # get rid of object id
        for inventory in query:
            inventory['_id'] = str(inventory['_id'])
            arr.append(inventory)
        
        # if pulled array empty return no content
        if len(arr) == 0:
            return Response([], status.HTTP_200_OK)

        # make chart data
        res = instock_collection.find({'time': {'$gte': getNDayBeforeToday(10)}}, {'_id': 0})
        chart_arr = []
        for item in res:
            chart_arr.append(item)
        output = convertToAmountPerDayData(chart_arr)
    except:
        return Response('Cannot Fetch From Database', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({ "arr": arr, "count": count, "chartData": output }, status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getInstockBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid SKU', status.HTTP_400_BAD_REQUEST)
    
    try:
        res = instock_collection.find_one({'sku': sku}, {'_id': 0})
    except:
        return Response('Cannot Fetch From Database', status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not res:
        return Response('No Instock Record Found', status.HTTP_404_NOT_FOUND)
    return Response(res, status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def updateInstockBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)

    oldInv = instock_collection.find_one({ 'sku': sku })
    if not oldInv:
        return Response('Instock Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    # construct $set data according to body
    setData = {}
    populateSetData(body, 'sku', setData, sanitizeNumber)
    populateSetData(body, 'time', setData, sanitizeString)
    populateSetData(body, 'condition', setData, sanitizeString)
    populateSetData(body, 'platform', setData, sanitizeString)
    populateSetData(body, 'marketplace', setData, sanitizeString)
    populateSetData(body, 'shelfLocation', setData, sanitizeString)
    populateSetData(body, 'comment', setData, sanitizeString)
    populateSetData(body, 'url', setData, sanitizeString)
    populateSetData(body, 'quantityInstock', setData, sanitizeNumber)
    populateSetData(body, 'quantitySold', setData, sanitizeNumber)
    populateSetData(body, 'qaName', setData, sanitizeString)
    populateSetData(body, 'adminName', setData, sanitizeString)

    populateSetData(body, 'msrp', setData, sanitizeNumber)
    populateSetData(body, 'lead', setData, sanitizeString)
    populateSetData(body, 'description', setData, sanitizeString)
    
    
    # update inventory
    res = instock_collection.update_one(
        { 'sku': sku },
        { '$set': setData }
    )
    
    # return update status 
    if not res:
        return Response('Update Failed', status.HTTP_404_NOT_FOUND)
    return Response('Update Success', status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperAdminPermission])
def deleteInstockBySku(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeSku(body['sku'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    
    oldInv = instock_collection.find_one({ 'sku': sku })
    if not oldInv:
        return Response('Instock Inventory Not Found', status.HTTP_404_NOT_FOUND)
    
    try:
        instock_collection.delete_one({ 'sku': sku })
    except:
        return Response('Cannot Delete Instock Inventory', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response('Instock Inventory Deleted', status.HTTP_200_OK)

# get all in-stock shelf location
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getAllShelfLocations(request):
    try:
        arr = instock_collection.distinct('shelfLocation')
    except:
        return Response('Cannot Fetch From Database', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(arr, status.HTTP_200_OK)

# converts qa record to inventory
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def createInstockInventory(request):
    try:
        body = decodeJSON(request.body)
        sku = sanitizeNumber(body['sku'])
        res = instock_collection.find_one({'sku': sku})
        if res:
            return Response(f'Inventory {sku} Already Instock', status.HTTP_409_CONFLICT)
        msrp = sanitizeNumber(body['msrp']) if 'msrp' in body else ''
        shelfLocation = sanitizeString(body['shelfLocation'])
        condition = sanitizeString(body['condition'])
        platform = sanitizeString(body['platform'])
        marketplace = sanitizeString(body['marketplace']) if 'marketplace' in body else 'Hibid'
        comment = sanitizeString(body['comment'])
        lead = sanitizeString(body['lead'])
        description = sanitizeString(body['description'])
        url = sanitizeString(body['url'])
        quantityInstock = sanitizeNumber(body['quantityInstock'])
        quantitySold = sanitizeNumber(body['quantitySold'])
        adminName = sanitizeString(body['adminName'])
        qaName = sanitizeString(body['qaName'])
        time = getIsoFormatInv()
        
        newInv: InstockInventory = InstockInventory(
            sku=sku,
            time=time,
            shelfLocation=shelfLocation,
            condition=condition,
            comment=comment,
            lead=lead,
            description=description,
            url=url,
            marketplace=marketplace,
            platform=platform,
            adminName=adminName,
            qaName=qaName,
            quantityInstock=quantityInstock,
            quantitySold=quantitySold,
            msrp=msrp
        )
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)

    try:
        instock_collection.insert_one(newInv.__dict__)
    except:
        return Response('Cannot Add to Database', status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response('Inventory Created', status.HTTP_200_OK)

# generate instock inventory csv file competible with hibid
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def getInstockCsv():
    
    # append this in front of description for item msrp lte 80$
    desc_under_80 = 'READ NEW TERMS OF USE BEFORE YOU BID!'
    vendor_name = 'B0000'
    msrp = 'MSRP:$'
    
    default_start_bid = 5
    default_start_bid_mystery_box = 5
    aliexpress_mystery_box_closing = 25
    
    reserve_default = 0
    
    # Lot	Lead	Description	MSRP:$	Price	Location	item	vendor	start bid	reserve	Est
    header = [
        'Lot',
        'Lead',        # original lead from recording
        'Description', # original description from recording
        'MSRP:$',      
        'Price',       # original scraped msrp  
        'Location',    # original shelfLocation
        'item',
        'vendor',     
        'start bid',
        'reserve',
        'Est'
    ]
    
    return Response('csv', status.HTTP_200_OK)


'''
Scraping stuff 
'''
# description: string
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def generateDescriptionBySku(request):
    try:
        body = decodeJSON(request.body)
        condition = sanitizeString(body['condition'])
        comment = sanitizeString(body['comment'])
        title = sanitizeString(body['title'])
    except:
        return Response('Invalid Body', status.HTTP_400_BAD_REQUEST)
    
    # call chat gpt to generate description
    lead = generate_title(title)
    desc = generate_description(condition, comment, title)
    return Response({ 'lead': lead, 'desc': desc }, status.HTTP_200_OK)

# return info from amazon for given sku
# sku: string
@api_view(['POST'])
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

    # extract link with regex
    # return error if not amazon link or not http
    link = extract_urls(target['link'])
    if 'https' not in link and '.ca' not in link and '.com' not in link:
        return Response('Invalid URL', status.HTTP_400_BAD_REQUEST)
    if 'a.co' not in link and 'amazon' not in link and 'amzn' not in link:
        return Response('Invalid URL, Not Amazon URL', status.HTTP_400_BAD_REQUEST)
    
    # generate header with random user agent
    headers = {
        'User-Agent': f'user-agent={ua.random}',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # get raw html and parse it with scrapy
    # TODO: use 10 proxy service to incraese scraping speed
    payload = {
        'title': '',
        'msrp': '',
        'imgUrl': '',
        'currency':''
    }
    
    # request the raw html from Amazon
    rawHTML = requests.get(url=link, headers=headers).text
    response = HtmlResponse(url=link, body=rawHTML, encoding='utf-8')
    try:
        payload['title'] = getTitle(response)
    except:
        return Response('Failed to Get Title', status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        payload['msrp'] = getMsrp(response)
    except:
        return Response('Failed to Get MSRP', status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        payload['imgUrl'] = getImageUrl(response)
    except:
        return Response('No Image URL Found', status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        payload['currency'] = getCurrency(response)
    except:
        return Response('No Currency Info Found', status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(payload, status.HTTP_200_OK)

# return msrp from home depot for given sku
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


'''
Migration stuff 
'''
# for instock record csv processing to mongo db
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def sendInstockCSV(request):
    body = decodeJSON(request.body)
    path = body['path']

    # joint file location with relative path
    dirName = os.path.dirname(__file__)
    fileName = os.path.join(dirName, path)
    print(getIsoFormatNow())
    
    # parse csv to pandas data frame
    data = pd.read_csv(filepath_or_buffer=fileName)
    
    # loop pandas dataframe
    for index in data.index:
        # if time is malformed set to empty string
        if len(str(data['time'][index])) < 19 or '0000-00-00 00:00:00':
            data.loc[index, 'time'] = ''
        else:
            # time convert to iso format
            # original: 2023-08-03 17:47:00
            # targeted: 2024-01-03T05:00:00.000
            time = datetime.strptime(str(data['time'][index]), "%Y-%m-%d %H:%M:%S").isoformat()
            data.loc[index, 'time'] = time
        
        # check url is http
        if 'http' not in str(data['url'][index]) or len(str(data['url'][index])) < 15 or '<' in str(data['url'][index]):
            data.loc[index, 'url'] = ''
        
        condition = str(data['condition'][index]).title().strip()
        
        # condition
        if 'A-B' in condition:
            data.loc[index, 'condition'] = 'A-B'
        elif 'API' in condition:
            data.loc[index, 'condition'] = 'New'
        elif 'NO MANUAL' in condition:
            data.loc[index, 'condition'] = 'New'
        else:
            # item condition set to capitalized
            data.loc[index, 'condition'] = condition
            
        # remove $ inside msrp price
        if 'NA' in str(data['msrp'][index]) or '***Need Price***' in str(data['msrp'][index]):
            data.loc[index, 'msrp'] = ''
        else:
            msrp = str(data['msrp'][index]).replace('$', '')
            msrp = msrp.replace(',', '')
            data.loc[index, 'msrp'] = float(msrp)

    # set output copy path
    data.to_csv(path_or_buf='./output.csv', encoding='utf-8', index=False)
    return Response(str(data), status.HTTP_200_OK)

# for qa record csv processing to mongo db
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def sendQACSV(request):
    body = decodeJSON(request.body)
    path = body['path']

    # joint file location with relative path
    dirName = os.path.dirname(__file__)
    fileName = os.path.join(dirName, path)
    
    # parse csv to pandas data frame
    data = pd.read_csv(filepath_or_buffer=fileName)
    
    # loop pandas dataframe
    for index in data.index:
        # time convert to iso format
        # original: 2023-08-03 17:47:00
        # targeted: 2024-01-03T05:00:00.000   optional time zone: -05:00 (EST is -5)
        time = datetime.strptime(data['time'][index], "%m/%d/%Y %I:%M %p").isoformat()
        data.loc[index, 'time'] = time
        
        # remove all html tags
        # if link containes '<'
        if '<' in data['link'][index]:
            cleanLink = BeautifulSoup(data['link'][index], "lxml").text
            data.loc[index, 'link'] = cleanLink
        
        # item condition set to capitalized
        condition = str(data['itemCondition'][index]).title()
        data.loc[index, 'itemCondition'] = condition
        
        # platform other capitalize
        if data['platform'][index] == 'other':
            data.loc[index, 'platform'] = 'Other'

    # set output copy path
    data.to_csv(path_or_buf='./output.csv', encoding='utf-8', index=False)
    return Response(str(data), status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def fillPlatform(request):
    # find
    myquery = {
       '$nor': [
           {'url': {"$regex": "ebay"}}, 
           {'url': {"$regex": "homedepot"}}, 
           {'url': {"$regex": "amazon"}}, 
           {'url': {"$regex": "a.co"}}, 
           {'url': {"$regex": "amzn"}}, 
           {'url': {"$regex": "ebay"}}, 
           {'url': {"$regex": "aliexpress"}},
           {'url': {"$regex": "walmart"}}
        ], 
    }

    # set
    newvalues = { "$set": { "platform": "Other" }}
    res = instock_collection.update_many(myquery, newvalues)
    return Response('Platform Filled', status.HTTP_200_OK)