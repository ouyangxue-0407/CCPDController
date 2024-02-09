from CCPDController.utils import sanitizeString, sanitizeNumber
from pprint import pprint 


# unpack Q&A Record filter object passed in by frontend
def unpackQARecordFilter(query_filter, fil):
    # condition filter
    if query_filter.get('conditionFilter', '') != '':
        sanitizeString(query_filter['conditionFilter'])
        fil['itemCondition'] = query_filter['conditionFilter']
    
    # platform filter
    if query_filter.get('platformFilter', '') != '':
        sanitizeString(query_filter['platformFilter'])
        fil['platform'] = query_filter['platformFilter']
    
    # marketplace filter
    if query_filter.get('marketplaceFilter', '') != '':
        sanitizeString(query_filter['marketplaceFilter'])
        fil['marketplace'] = query_filter['marketplaceFilter']
        
    # time range filter
    timeRange = query_filter['timeRangeFilter']
    if timeRange != {}:
        sanitizeString(timeRange['from'])
        sanitizeString(timeRange['to'])
        fil['time'] = {
            # mongoDB time range query only support ISO 8601 format like '2024-01-03T05:00:00.000Z'
            '$gte': timeRange['from'],
            '$lt': timeRange['to']
        }
    return fil

# unpack instock inventory filter object passed in by frontend
def unpackInstockFilter(query_filter, fil):
    # mongo_or = { '$or': [] }
    # instock filter
    if 'instockFilter' in query_filter:
        sanitizeString(query_filter['instockFilter'])
        match query_filter['instockFilter']:
            case 'in':
                fil['quantityInstock'] = { '$gt': 0 }
            case 'out':
                fil['quantityInstock'] = { '$lte': 0 }
            case '':
                pass
    
    # create $and array
    if '$and' not in fil:
        fil['$and'] = []

    # item condition filter
    if 'conditionFilter' in query_filter and query_filter['conditionFilter'] != '':
        sanitizeString(query_filter['conditionFilter'])
        fil['$and'].append({'condition': query_filter['conditionFilter']})
    
    # original platform filter
    if 'platformFilter' in query_filter and query_filter['platformFilter'] != '':
        sanitizeString(query_filter['platformFilter'])
        fil['$and'].append({'platform': query_filter['platformFilter']})
        
    
    # marketplace filter
    if 'marketplaceFilter' in query_filter and query_filter['marketplaceFilter'] != '':
        sanitizeString(query_filter['marketplaceFilter'])
        fil['$and'].append({'marketplace': query_filter['marketplaceFilter']})
        

    # qa personal filter
    if 'qaFilter' in query_filter and len(query_filter['qaFilter']) > 0:
        qaf = { '$or': [] }
        for name in query_filter['qaFilter']:
            n = sanitizeString(name)
            qaf['$or'].append({ 'qaName': n })
        fil['$and'].append(qaf)
    
    # admin filter
    if 'adminFilter' in query_filter and len(query_filter['adminFilter']) > 0:
        adf = { '$or': [] }
        for name in query_filter['adminFilter']:
            n = sanitizeString(name)
            adf['$or'].append({ 'adminName': n })
        fil['$and'].append(adf)

    # shelf location Filter
    if 'shelfLocationFilter' in query_filter and len(query_filter['shelfLocationFilter']) > 0:
        shf = { '$or': [] }
        for loc in query_filter['shelfLocationFilter']:
            l = sanitizeString(loc)
            shf['$or'].append({ 'shelfLocation': l })
        fil['$and'].append(shf)
            
    # keyword filter
    if 'keywordFilter' in query_filter and len(query_filter['keywordFilter']) > 0:
        kwFilter = { '$or': [] }
        for word in query_filter['keywordFilter']:
            keyword = sanitizeString(word)
            kwFilter['$or'].append({ 'lead': {'$regex': keyword} })
            kwFilter['$or'].append({ 'description': {'$regex': keyword} })
        fil['$and'].append(kwFilter)
    
    # msrp filter
    if 'msrpFilter' in query_filter:
        msrpFilter = query_filter['msrpFilter']
        if msrpFilter['gte'] != '' or msrpFilter['lt'] != '':
            fil['msrp'] = {}
            if msrpFilter['gte'] != '':
                fil['msrp']['$gte'] = float(msrpFilter['gte'])
            if msrpFilter['lt'] != '': 
                fil['msrp']['$lt'] = float(msrpFilter['lt'])
            
    # time range filter
    if 'timeRangeFilter' in query_filter:
        timeRange = query_filter['timeRangeFilter']
        if ('from' in timeRange and timeRange['from'] != '') or ('to' in timeRange and timeRange['to'] != ''):
            f = sanitizeString(timeRange['from'])
            t = sanitizeString(timeRange['to'])
            fil['time'] = {
                # mongoDB time range query only support ISO 8601 format like '2024-01-03T05:00:00.000Z'
                '$gte': f,
                '$lt': t
            }
    
    # remove $and if no filter applied
    # $and cannot be empty
    if fil['$and'] == []:
        del fil['$and']
    
    pprint(fil)
    return fil