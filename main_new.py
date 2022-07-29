import sqlite3
import requests
import folium
from dateutil import parser
import time
from folium.plugins import MousePosition
from folium.plugins import MeasureControl
from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')

scan_points = [69.384970, 86.215555], [69.444730, 86.123540], [69.324550, 87.340110], [69.535900, 88.295960],\
              [69.524070, 88.334280], [69.502860, 88.357540], [69.480610, 88.457800], [69.416070, 86.178950],\
              [69.479900, 88.389520], [69.455990, 88.376450], [69.435870, 88.343020], [69.395490, 88.364870],\
              [69.418200, 88.303600], [69.358340, 88.410390], [69.377150, 88.337550], [69.360000, 88.288000],\
              [69.278950, 88.133980], [69.305890, 88.158400], [69.341300, 88.245810], [69.344030, 88.210290],\
              [69.345990, 88.206680], [69.348170, 88.202640], [69.350350, 88.198760], [69.352530, 88.194660],\
              [69.354740, 88.190640], [69.356930, 88.186570], [69.359190, 88.182800], [69.341850, 88.214190],\
              [69.339670, 88.218370], [69.337492, 88.222747], [69.361405, 88.178737], [69.363674, 88.174918],\
              [69.357396, 88.202233], [69.359605, 88.198178], [69.361821, 88.194144], [69.364015, 88.190110],\
              [69.366230, 88.186054], [69.355161, 88.206375], [69.352959, 88.210398], [69.350716, 88.214475],\
              [69.348487, 88.218573], [69.346258, 88.222672], [69.344010, 88.226749], [69.341793, 88.230901],\
              [69.339612, 88.235085], [69.349959, 88.182921], [69.347659, 88.187063], [69.345403, 88.190818],\
              [69.343102, 88.194466], [69.340846, 88.198414], [69.352275, 88.179295], [69.354597, 88.175776],\
              [69.356912, 88.172386], [69.359212, 88.168588], [69.326564, 88.206396], [69.351246, 87.347059],\
              [69.372573, 87.366028], [69.381945, 87.294788], [69.378907, 87.218871], [69.385360, 87.144756],\
              [69.386946, 87.068453], [69.377879, 86.996527], [69.368763, 86.924858], [69.371273, 86.848984],\
              [69.387143, 86.787271], [69.400540, 86.720806], [69.406918, 86.646423], [69.409858, 86.570302],\
              [69.413083, 86.494353], [69.420431, 86.420624], [69.412091, 86.347775], [69.410990, 86.271225],\
              [69.376096, 87.441838], [69.376768, 87.518227], [69.369927, 87.592149], [69.366321, 87.667873],\
              [69.352471, 87.733212], [69.340316, 87.801189], [69.329730, 87.871206], [69.316365, 87.937317],\
              [69.328109, 88.005788], [69.352184, 88.040035], [69.364166, 88.092456]

#scan_points = [69.34817, 88.20264], [69.351972, 88.195581]
@logger.catch
def db_create():
    db = sqlite3.connect('nearest_drivers.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS geohistory(
        gh_id TEXT,
        gh_timestamp DATETIME,
        gh_timestampu INTEGER,
        gh_lat REAL,
        gh_lon REAL,
        gh_tariff TEXT
    )""")
    db.commit()
    logger.debug(f'Data base created')

@logger.catch
def map_generate(points):

    map_centre = [69.35999, 87.21222]
    m = folium.Map(location=map_centre, zoom_start=9)
    logger.info(f'Points for scan: {len(points)}')
    for point in range(0, len(points)):
        folium.Circle(points[point], radius=3000).add_to(m)
        folium.Circle(points[point], radius=1).add_to(m)

    MousePosition().add_to(m)  # mouse pos to corner on map
    m.add_child(MeasureControl())  # measure at map
    m.save("map_npr.html")  # /var/www/html/map_norilsk.html
    logger.debug('Map saved')

def db_duplkill():
    db = sqlite3.connect('nearest_drivers.db')
    sql = db.cursor()
    sql.execute(f"DELETE FROM geohistory "
                f"WHERE rowid > (SELECT MIN(rowid) "
                f"FROM geohistory p2 "
                    f"WHERE geohistory.gh_id = p2.gh_id "
                    f"AND geohistory.gh_timestamp = p2.gh_timestamp "
                    f"AND geohistory.gh_timestampu = p2.gh_timestampu "
                    f"AND geohistory.gh_lat = p2.gh_lat "
                    f"AND geohistory.gh_lon = p2.gh_lon "
                    f"AND geohistory.gh_tariff = p2.gh_tariff)")
    db.commit()


@logger.catch
def parse_data(points):
    db = sqlite3.connect('nearest_drivers.db')
    sql = db.cursor()
    for element in range(0, len(points)):
        points[element][-1], points[element][0] = points[element][0], points[element][-1]  # reverse elements in points
    result = []  # create a list cuz error
    url = 'https://ya-authproxy.taxi.yandex.ru/integration/turboapp/v1/nearestdrivers'  # url for POST
    # send POST body parameters
    for point in range(0, len(points)):
        logger.info(f'START')
        logger.info(f'Current point = {points[point]}')
        response = requests.post(url, json={
         "point": points[point],  # our position
         "classes": ["econom"],
         "current_drivers": [],
         "is_retro": True,
         "simplify": True})
        logger.info(response)
        if str(response) == '<Response [200]>':
            data_drivers = response.json().get('drivers')
            logger.info(f'data drivers = {data_drivers}')
            for driver in (data_drivers or []):
                logger.info(f'driver {driver}')
                for i in range(0, len(driver.get('positions'))):
                    dr_lon = driver.get('positions')[i].get('lon')
                    dr_lat = driver.get('positions')[i].get('lat')
                    timestamp = driver.get('positions')[i].get('timestamp')
                    dr_time = parser.parse(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    dt = parser.parse(timestamp)
                    dr_timeu = int(time.mktime(dt.timetuple()))
                    dr_id = driver.get('id')
                    dr_tariff = driver.get('display_tariff')

                    logger.info(f'#{i} id = {dr_id}')
                    logger.info(f'#{i} driver_tariff = {dr_tariff}')
                    logger.info(f'#{i} lons = {dr_lon}')
                    logger.info(f'#{i} lats = {dr_lat}')
                    logger.info(f'#{i} driver_time = {dr_time}')
                    logger.info(f'#{i} driver_timeu = {dr_timeu}')
                    logger.debug(f'-----------')

                    sql.execute(f"INSERT INTO geohistory VALUES (?, ?, ?, ?, ?, ?)",
                                (dr_id, dr_time, dr_timeu, dr_lat, dr_lon, dr_tariff))
                    db.commit()
                    db_duplkill()
                    logger.info(f'DB updated')

                    result.append(
                        {
                            'dr_id': dr_id,
                            'dr_tariff': dr_tariff,
                            'dr_time': dr_time,
                            'dr_timeu': dr_timeu,
                            'dr_lon': dr_lon,
                            'dr_lat': dr_lat,
                        }
                    )

            logger.debug('data was parsed')
        else:
            logger.error('respone is not == 200')
    logger.debug(result)
    return


if __name__ == '__main__':
    db_create()
    map_generate(scan_points)
    #parse_data(scan_points)


