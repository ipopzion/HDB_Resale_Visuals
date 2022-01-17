from basic_api import get_info

## definition -----------------------------------------------------

def get_svy(blk, streetname):
    """Get SVY coordinate of a unit"""
    global cache
    if (blk, streetname) not in cache: 
        try:
            api = 'https://developers.onemap.sg/commonapi/search?searchVal={} {}&returnGeom=Y&getAddrDetails=Y&pageNum=1'.format(blk,streetname)
            address = get_info(api)
            svy = (address['results'][0]['X'],address['results'][0]['Y'])
        except:
            svy = (0,0)
        finally:
            cache[(blk, streetname)] = svy
    return cache[(blk, streetname)]

def get_hdb_list(api, search=None,limit='100'):
    """Generate a list of resale flats based on search critera"""
    if limit:
        api += f"&limit={str(limit)}"
    if search:
        api += f"&q={str(search)}"
    full_dic = get_info(api)
    hdb_list= full_dic['result']['records']
    return hdb_list

def filters(lis):
    """Function to combine multiple filters"""
    def filter_by_value(key, expected_value):
        return (lambda x: x[key] == expected_value)
    def pass_all_filters(x, list_of_filters):
        for fil in list_of_filters:
            if not fil(x):
                return False
        return True 
        
    lis_fils = [filter_by_value(tup[0], tup[1]) for tup in lis]
    return lambda x: pass_all_filters(x, lis_fils)


## variables ---------------------------------------------------------

datagov_api = "https://data.gov.sg/api/action/datastore_search"
hdb_endpoint = "?resource_id=f1765b54-a209-4718-8d38-a39237f502b3"
cache = {}

filterlist = [('flat_type','4 ROOM')] #list of tuples
search_term = None

## execution --------------------------------------------------------

"""Return the list of resale data for use for hdb_visual.py"""
def get_results(search_limit=100):
    hdb_api = datagov_api + hdb_endpoint
    hdb_list = get_hdb_list(hdb_api,limit=search_limit,search=search_term)
    currentfilter = filters(filterlist)
    filtered_list = list(filter(lambda x: currentfilter(x), hdb_list))

    cleaned_list = []
    for entry in filtered_list:
        useful_keys = ('block','street_name','resale_price',
                       'floor_area_sqm','storey_range')
        useful_dic = {}
        for key in useful_keys:
            value = entry[key]
            if key == 'storey_range':
                value = int(value[:2]) + 1 
            useful_dic.update({key:value})
        cleaned_list.append(useful_dic)

    return cleaned_list
