import re
import time
import random
import requests
from fake_useragent import UserAgent

# Amazon scrapping utils 
# works for both Amazon CA nad US

# center col div id and class name
centerColId = 'centerCol'
centerColClass = 'centerColAlign'

# right col tag id and class name
rightColId = 'rightCol'
rightColClass = 'rightCol'

# product title span id
productTitleId = 'productTitle'

# price tag class
priceWholeClass = 'a-price-whole'
priceFractionClass = 'a-price-fraction'
priceRangeClass = 'a-price-range'

# image container class
imageContainerClass = 'imgTagWrapper'


# random wait time between scrape
random_wait = lambda : time.sleep(random.randint(30, 50))

# extract url from string using regex
def extract_urls(input):
    words = input.split()
    regex = re.compile(r'https?://\S+')
    return [word for word in words if regex.match(word)][0]

# returns children of top nav bar/belt
def getNavBelt(response):
    children = response.xpath(f'//div[@class="nav-right"]/child::*')
    if len(children) < 1:
        raise Exception('No right nav belt found')
    return children

# takes scrapy HtmlResponse generated from rawHTML
# return array of center col's children tags
def getCenterCol(response):
    # return error if no center col found
    children = response.xpath(f'//div[@id="{centerColId}" or @class="{centerColClass}"]/child::*')
    if len(children) < 1:
        raise Exception('No center column found')
    return children

def getRightCol(response):
    # id = "unqualifiedBuyBox"
    children = response.xpath(f'//div[@id="{rightColId}" or @class="{rightColClass}"]/child::*')
    if len(children) < 1:
        raise Exception('No right column found')
    return children

# takes scrapy HtmlResponse object and returns title
def getTitle(response) -> str:
    arr = getCenterCol(response)
    
    # get title
    # remove whitespace around it
    for p in arr.xpath(f'//span[@id="{productTitleId}"]/text()'):
        title = p.extract().strip()
    return title

# takes rawHTML str and returns:
# - msrp in float 
# - msrp range in array of float
# - or price unavailable string
def getMsrp(response):
    center = getCenterCol(response)
    right = getRightCol(response)
    
    
    # check for out of stock id in right col
    outOfStock = right.xpath('//div[@id="outOfStock"]').getall()
    if len(outOfStock) > 1:
        return 'Currently unavailable'
    
    # if 'unqualifiedBuyBox' appears in arr for more than 2 times, return unavailable
    unqualifiedBox = right.xpath('//div[@id="unqualifiedBuyBox"]').getall()[:4]
    if len(unqualifiedBox) > 2:
        return 'Currently unavailable'
    
    # Currently unavailable in right col set

    # grab price in span tag 
    # msrp whole joint by fraction
    integer = center.xpath(f'//span[has-class("{priceWholeClass}")]/text()').extract()
    decimal = center.xpath(f'//span[has-class("{priceFractionClass}")]/text()').extract()
    if integer and decimal:
        price = float(integer[0] + '.' + decimal[0])
        return price
    
    # extract price range if no fixed price
    price = []
    rangeTag = center.xpath(f'//span[@class="{priceRangeClass}"]/child::*')
    for p in rangeTag.xpath('//span[@data-a-color="price" or @class="a-offscreen"]/text()').extract():
        if '$' in p and p not in price:
            price.append(p)
    return price

# takes scrapy response and get full quality stock image
# src is the low quality image
# Amazon CA
def getImageUrl(response):
    # id="imgTagWrapperId" class="imgTagWrapper"
    img = response.xpath(f'//div[@class="{imageContainerClass}"]/child::*').extract_first()
    if img:
        http_pattern = re.compile(r'https?://\S+')
        res = http_pattern.findall(img)
        # return res[:2] # for both lq and hq image
        return res[1]

# look for US and CA flag
# <i class="icp-flyout-flag icp-flyout-flag-ca"></i>
# US: icp-flyout-flag-us
# CA: icp-flyout-flag-ca
def getCurrency(response) -> str:
    nav = getNavBelt(response)
    flag = nav.xpath("[@id='nav-tools']")
    print(flag)
    
    
    
    # for i in nav.xpath("//span[@class='icp-flyout-flag-us']").getall():
    #     print(i)
        # if 'icp-flyout-flag-us' in i:
        #     print(i)
        #     return i
        # if 'icp-flyout-flag-ca' in i:
        #     print(i)
        #     return i
        # if re.search('icp-flyout-flag-us', i):
        #     print("Found 'flag-us'")
        #     return i
        # if re.search('icp-flyout-flag-ca', i):
        #     print("Found 'flag-ca'")
        #     return i