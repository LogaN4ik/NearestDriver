import json
import requests
import folium
import time
import coord_generator
from folium.plugins import HeatMap
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
    return result

def collect_coord():
    with open('alldata.json') as file:   # read result.json
        drivers_info = json.load(file)
    print(len(drivers_info), "records of drivers info")

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
        norilsk_lats = coord_generator.get_lats(69.340, 69.365, 88.150, 88.255)
        norilsk_lons = coord_generator.get_lons(69.340, 69.365, 88.150, 88.255)
        talnakh_lats = coord_generator.get_lats(69.48, 69.505, 88.36, 88.41)
        talnakh_lons = coord_generator.get_lons(69.48, 69.505, 88.36, 88.41)
        lat_list = norilsk_lats + talnakh_lats
        lon_list = norilsk_lons + talnakh_lons
        all_data = []
        for i, val in enumerate(lat_list):
            data = collect_data(lat_list[i], lon_list[i])
            all_data = all_data + data
            print("\n #",i, "coordinate of nearest drivers: ", lat_list[i], lon_list[i])
            print('collected data from coordinate = ', data)
        print('\n all data = ',all_data)

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
