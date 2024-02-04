from CCPDController.utils import sanitizeString

# unpack Q&A Record filter object passed in by frontend
def unpackQARecordFilter(query_filter, fil):
    # condition filter
    if query_filter['conditionFilter'] != '':
        sanitizeString(query_filter['conditionFilter'])
        fil['itemCondition'] = query_filter['conditionFilter']
    
    # platform filter
    if query_filter['platformFilter'] != '':
        sanitizeString(query_filter['platformFilter'])
        fil['platform'] = query_filter['platformFilter']
    
    # marketplace filter
    if query_filter['marketplaceFilter'] != '':
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
    # item condition filter
    if query_filter['conditionFilter'] != '':
        sanitizeString(query_filter['conditionFilter'])
        fil['itemCondition'] = query_filter['conditionFilter']
    
    # original platform filter
    if query_filter['platformFilter'] != '':
        sanitizeString(query_filter['platformFilter'])
        fil['platform'] = query_filter['platformFilter']
    
    # marketplace filter
    if query_filter['marketplaceFilter'] != '':
        sanitizeString(query_filter['marketplaceFilter'])
        fil['marketplace'] = query_filter['marketplaceFilter']
    
    # instock filter
    if query_filter['instockFilter'] != '':
        sanitizeString(query_filter['instockFilter'])
        match query_filter['instockFilter']:
            case 'in':
                fil['quantityInstock'] = { '$gt': 0 }
            case 'out':
                fil['quantityInstock'] = { '$lte': 0 }
            case '':
                pass
            
    # qa personal filter
    if query_filter['ownerFilter'] != '':
        sanitizeString(query_filter['ownerFilter'])
        fil['qaName'] = query_filter['ownerFilter']
    
    # admin filter
    if query_filter['adminFilter'] != '':
        sanitizeString(query_filter['adminFilter'])
        fil['adminName'] = query_filter['adminFilter']
    
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