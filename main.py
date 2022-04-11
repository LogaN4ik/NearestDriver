import json
import requests
import folium
import time
from folium.plugins import HeatMap
#test branch. Funcs args of coord add
#           lat             lon
#norilsk 69.346        88.21
#valek   69.4          88.36
#talnakh 69.49         88.38


def collect_data(our_lat, our_lon):
    result = [] # create a list cuz error
    url = 'https://ya-authproxy.taxi.yandex.ru/integration/turboapp/v1/nearestdrivers' # url for POST
    #send POST body parametres
    response = requests.post(url, json={
        "point": [our_lon, our_lat], #our position
        "classes": ["econom"],
        "current_drivers": [],
        "is_retro": True,
        "simplify": True})
    data_source = response.json()
    print(str(len(data_source.get('drivers'))) + ' drivers') #count of nearest drivers
    data_drivers = data_source.get('drivers')
    for i in data_drivers:  #for each driver in json we will get only intereting for us info
        driver_id = i.get('id')
        driver_tariff = i.get('display_tariff')
        driver_position_lon = i.get('positions')[0].get('lon')
        driver_position_lat = i.get('positions')[0].get('lat')
        driver_position_timestamp = i.get('positions')[0].get('timestamp')
        result.append(
            {
                'driver_id': driver_id,
                'driver_tariff': driver_tariff,
                'driver_position_lon': driver_position_lon,
                'driver_position_lat': driver_position_lat,
                'driver_position_timestamp': driver_position_timestamp
            }
        )
    #with open('result.json', 'w') as file: #write drivers info into result.json
    #    json.dump(result, file, indent=4, ensure_ascii=False)
    #print('result= ', result)
    return result

def collect_coord():
    #with open('result.json') as file:   # read result.json
    with open('alldata.json') as file:   # read result.json
        drivers_info = json.load(file)
    #print('all drivers info: ', drivers_info)
    print(len(drivers_info))

    lats = []
    lons = []
    warm = 0.1 # warm-level of point on map
    for i, val in enumerate(drivers_info):  #create a list with list of lats and lons coordinate for every drivers
         lat = [drivers_info[i]['driver_position_lat']]
         lon = [drivers_info[i]['driver_position_lon']]
         lats = lats + lat
         lons = lons + lon
    map_data = []
    for i, val in enumerate(lats):  #create data list for map generating like [lat, lon, warm]
        map_data_temp = [lats[i] , lons[i] , warm]
        map_data = map_data + [map_data_temp]
    print(map_data)
    return(map_data)

def map_generate(map_centre):
    mapObj = folium.Map(location=map_centre, zoom_start=9.4)
    HeatMap(collect_coord()).add_to(mapObj)
    mapObj.save("map_norilsk.html")

def main():
    while(True):
        lat_list = [69.346, 69.367273]
        lon_list = [88.21, 88.163294]
        all_data = []
        for i, val in enumerate(lat_list):
            data = collect_data(lat_list[i], lon_list[i])
            all_data = all_data + data
            print(i, lat_list[i], lon_list[i])
            print('collect data = ', data)
        print('all data = ',all_data)

        d = {}
        for x in all_data:
            d[x['driver_id']] = x
        all_data = list((d.values()))

        with open('alldata.json', 'w') as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
        map_generate([69.4, 87.4])
        time.sleep(6)

if __name__ == '__main__':
    main()
