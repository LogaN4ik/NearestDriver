import json
import requests
import folium
import coord_generator
import pandas as pd
from folium.plugins import HeatMap
from pyfiglet import Figlet
from loguru import logger
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')

print(Figlet(font='small').renderText('Nearest Driver     0.6'))  # preview

norilsk = ['norilsk', 69.340, 69.365, 88.150, 88.255]
talnah = ['talnah', 69.48, 69.505, 88.36, 88.41]
dudinka = ['dudinka', 69.400, 69.420, 86.155, 86.230]  # 69.420 86.155    69.400 86.230
kayerkan = ['kayerkan', 69.340, 69.360, 87.740, 87.770]  # 69.360 87.740    69.340 87.770


@logger.catch
def parse_data(our_lat, our_lon):
    result = []  # create a list cuz error
    url = 'https://ya-authproxy.taxi.yandex.ru/integration/turboapp/v1/nearestdrivers'  # url for POST
    # send POST body parameters
    response = requests.post(url, json={
        "point": [our_lon, our_lat],  # our position
        "classes": ["econom"],
        "current_drivers": [],
        "is_retro": True,
        "simplify": True})
    data_drivers = response.json().get('drivers')
    for driver in (data_drivers or []):  # for each driver in json we will get only interesting for us info
        driver_id = driver.get('id')
        driver_tariff = driver.get('display_tariff')
        driver_position_lon = driver.get('positions')[0].get('lon')
        driver_position_lat = driver.get('positions')[0].get('lat')
        driver_position_timestamp = driver.get('positions')[0].get('timestamp')
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


@logger.catch
def map_coords():
    with open('geodata.json') as file:  # read
        drivers_info = json.load(file).get('data')[0]
    logger.debug(f'{len(drivers_info)} records of drivers info')

    lats = []
    lons = []
    warm = 0.1  # warm-level of point on map
    for i, val in enumerate(drivers_info):  # create a list with list of lats and lons coordinate for every drivers
        lat = [drivers_info[i]['driver_position_lat']]
        lon = [drivers_info[i]['driver_position_lon']]
        lats = lats + lat
        lons = lons + lon
    map_data = []
    for i, val in enumerate(lats):  # create data list for map generating like [lat, lon, warm]
        map_data_temp = [lats[i], lons[i], warm]
        map_data = map_data + [map_data_temp]
    logger.debug(map_data)
    return map_data


@logger.catch
def map_generate():
    map_centre = [69.35999, 87.21222]
    map_object = folium.Map(location=map_centre, zoom_start=9)
    HeatMap(map_coords()).add_to(map_object)
    map_object.save("/var/www/html/map_norilsk.html")  # /var/www/html/map_norilsk.html
    logger.debug('Map saved')


@logger.catch
def get_free_drivers(region):
    region_scan_lats = coord_generator.get_lats(region[1], region[2], region[3], region[4])
    regions_scan_lons = coord_generator.get_lons(region[1], region[2], region[3], region[4])
    geo_data = []  # create empty list
    for i, val in enumerate(region_scan_lats):
        data = parse_data(region_scan_lats[i], regions_scan_lons[i])
        if data is not None:
            geo_data = geo_data + data
            logger.info(f"{region[0]} scan {i}, scan for:{region_scan_lats[i]}, {regions_scan_lons[i]}, data: {data}")

    d = {}
    for x in geo_data:
        d[x['driver_id']] = x
    geo_data = list((d.values()))
    free_drivers = len(geo_data)
    drivers = {'free_drivers_at_region': free_drivers}
    j = json.dumps(drivers)  # save output in json files
    with open('/var/www/html/' + region[0] + '_drivers.json', 'w', encoding='utf-8') as f: # '/var/www/html/' + region[0] + '_drivers.json'
        f.write(j)
        f.close()
    if free_drivers > 0:
        with open((region[0] + '_geodata.json'), 'w') as f:
            json.dump(geo_data, f, indent=4, ensure_ascii=False)
    else:
        with open((region[0] + '_geodata.json'), 'w') as f:
            f.write('[]')


@logger.catch
def concat_geo_json():
    with open('kayerkan_geodata.json') as f1:  # open the file
        data1 = json.load(f1)
    with open('dudinka_geodata.json') as f2:  # open the file
        data2 = json.load(f2)
    with open('talnah_geodata.json') as f3:  # open the file
        data3 = json.load(f3)
    with open('norilsk_geodata.json') as f4:  # open the file
        data4 = json.load(f4)
    df1 = pd.DataFrame([data1])  # Creating DataFrames
    df2 = pd.DataFrame([data2])  # Creating DataFrames
    df3 = pd.DataFrame([data3])  # Creating DataFrames
    df4 = pd.DataFrame([data4])  # Creating DataFrames
    merge_json = pd.concat([df1, df2, df3, df4], axis=1)  # Concat DataFrames
    merge_json.to_json("geodata.json", orient='split')  # Writing Json , orient='split'


if __name__ == '__main__':
    get_free_drivers(kayerkan)
    get_free_drivers(dudinka)
    get_free_drivers(talnah)
    get_free_drivers(norilsk)
    concat_geo_json()
    map_generate()

