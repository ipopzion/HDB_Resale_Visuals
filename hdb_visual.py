import folium
from hdb_getter import get_results, get_svy
from svy21 import SVY21
from folium import features
import shapely
import branca.colormap as cm
import webbrowser
SVY = SVY21()

## Functions -----------------------------------------------

def main():
    """"Save a leaflet map in html form with elements added"""
    units = get_results(num_results)
    unitswithsvy = update_svy(units)
    info_dic = sort_into_bits(bit_size,unitswithsvy)
    new_info_dic = info_dic_process(info_dic)
            
    sg_map = plot_bits(bit_size, new_info_dic)
    sg_map.save("sg_map.html")
    webbrowser.open("sg_map.html")
    return 0

def update_svy(units):
    """Getting the SVY coordinate of each unit"""
    unitswithsvy = []
    for unit in units:
        svy = get_svy(unit['block'], unit['street_name'])
        if svy != (0,0):
            unit.update({'svy':svy})
            unitswithsvy.append(unit)
    return unitswithsvy

def svy_to_bit(bit_size, svy):
    """Simplifying location data into 'bits'"""
    bit = (float(svy[0])//bit_size, 
           float(svy[1])//bit_size)
    return bit
    
def sort_into_bits(bit_size, unitswithsvy):
    """Sorting units into boxes based on the bit they are in"""
    info_dic = {}  
    for unit in unitswithsvy:
        try:
            bit = svy_to_bit(bit_size, unit['svy'])
        except:
            continue
        bit_dic = info_dic.get(bit, {})
        bit_dic['entries'] = bit_dic.get('entries', 0) + 1 
        for var in ('resale_price', 'floor_area_sqm','storey_range'):
            bit_dic[var] = bit_dic.get(var, 0) + float(unit[var])

        info_dic[bit] = bit_dic 
        
    return info_dic  

def info_dic_process(info_dic):
    """Aggregating the data of all the flats into average within a bit"""
    new_info_dic = {}
    for bit in info_dic: 
        properties = info_dic[bit]
        entries = properties['entries']
        
        new_properties = {'entries': entries}
        new_properties.update({
            "Average Price": 
                round(properties['resale_price']/ entries),
            "Price per sqm":
                round(properties['floor_area_sqm']/ entries, 3),
            "Average Height":
                round(properties['storey_range']/ entries, 1)
        })
        new_info_dic[bit] = new_properties
    return new_info_dic

def bit_to_latlng(bit_size, bit):
    """To convert back from bit to latlng for plotting""" 
    lat, lng = SVY.computeLatLon(bit[1] * bit_size, 
                                 bit[0] * bit_size)
    return [round(lng, 8), round(lat, 8)]
    
def box_coordinates(bit_size, bit):
    """Generating the box geometrical coordinate based on the bit"""
    bit00 = bit
    bit01 = (bit[0], bit[1] + 1) 
    bit10 = (bit[0] + 1, bit[1])
    bit11 = (bit[0] + 1, bit[1] + 1)
    
    corr = [[bit_to_latlng(bit_size,bit00),
             bit_to_latlng(bit_size,bit10),
             bit_to_latlng(bit_size,bit11),
             bit_to_latlng(bit_size,bit01),
             bit_to_latlng(bit_size,bit00)]]
    return corr
    
def plot_bits(bit_size, new_info_dic):
    """Plotting all the bits into an overlay"""
    sg_map = folium.Map(location=[1.36, 103.8], zoom_start=11)
    data_list = []
    data = {
        "type": "FeatureCollection",
        "features": []
    }   
    mini, maxi = 90, 90    
    count = 0
    new_info_dic_2 = {}
    
    for bit in new_info_dic:
        count += 1
        coor = box_coordinates(bit_size, bit)
        properties = new_info_dic[bit]

        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Polygon",
                "coordinates":coor,
            }
        }
        data["features"].append(feature)
        if count % 2 == 0:
            data_list.append(data)
            data = {
                "type": "FeatureCollection",
                "features": []
            } 
    
    colormap = cm.LinearColormap(colors=['green','yellow','red'], vmin=80,vmax=100) 
    colormap.caption = "Price per sqm"
    colormap.add_to(sg_map)
    style_function = lambda x: {'fillColor': colormap(x["properties"]["Price per sqm"]),
                                'color': '#000000',
                                'fillOpacity': 0.5,
                                'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000',
                                    'color': '#000000',
                                    'fillOpacity': 0.5,
                                    'weight': 0.1}

    for data in data_list:
        NIL = features.GeoJson(
            data = data,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['Price per sqm', 'Average Price', 'Average Height', 'entries'],
                aliases=['Price per sqm', 'Average Price', 'Average Height', 'Entries'],
                localize=True
            )
        )

        sg_map.add_child(NIL)
    return sg_map

## Variables --------------------------------------------------------------------
num_results = 100
bit_size = 2000

## Execution -------------------------------------------------------------------

if __name__ == "__main__":
    main()
