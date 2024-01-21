import re
import time
import random
import requests
from fake_useragent import UserAgent

# Amazon scrapping utils 
# center col div id and class name
centerColId = 'centerCol'
centerColClass = 'centerColAlign'

# right col tag id and class name
rightColId = 'rightCol'
rightColClass = rightColId

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
# Amazon CA
def getTitle(response) -> str:
    arr = getCenterCol(response)
    
    # get title
    # remove whitespace around it
    for p in arr.xpath(f'//span[@id="{productTitleId}"]/text()'):
        title = p.extract().strip()
    return title

# takes rawHTML str and returns
# mrsp in float 
# mrsp range in array of float
# or price unavailable string
# Amazon CA
def getMrsp(response):
    arr = getCenterCol(response)

    right = getRightCol(response)
    # if 'unqualifiedBuyBox' appears in arr for more than 2 times, return unavailable
    unqualifiedBox = right.xpath('//div[@id="unqualifiedBuyBox"]').getall()[:4]
    if len(unqualifiedBox) > 2:
        return 'Currently unavailable'


    # grab price in span tag 
    # mrsp whole joint by fraction
    integer = arr.xpath(f'//span[has-class("{priceWholeClass}")]/text()').extract()
    decimal = arr.xpath(f'//span[has-class("{priceFractionClass}")]/text()').extract()
    if integer and decimal:
        price = float(integer[0] + '.' + decimal[0])
        return price
    
    # extract price range if no fixed price
    price = []
    rangeTag = arr.xpath(f'//span[@class="{priceRangeClass}"]/child::*')
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
    
