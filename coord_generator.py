from numpy import arange

step = 0.01


def get_lons(lat_start, lat_stop, lon_start, lon_stop):
    lat_delta = round(lat_start - lat_stop, 3)
    lon_delta = round(lon_start - lon_stop, 3)
    lat_count = round(lat_delta / step)
    lon_count = round(lon_delta / step)

    # print(lat_count, 'vert line')
    # print(lon_count, 'horizon line')
    # print(lat_count * lon_count, 'points ')

    lons = []
    lats = []

    for i in arange(lon_start, lon_stop, step):
        lon = [round(i, 3)]
        lons = lons + lon

    for i in arange(lat_start, lat_stop, step):
        lat = [round(i, 3)]
        lats = lats + lat

    # print('all lats: ', lats)
    # print('all lons: ', lons)

    lat_lon_comb = [(x, y) for x in lats for y in lons]
    # print('list of all combinations: ', lat_lon_comb)

    list_lats = []
    for i, val in enumerate(lat_lon_comb):
        clear_lat = ((lat_lon_comb[i])[0])
        float_lat = float(clear_lat)
        list_lat = [float_lat]
        list_lats = list_lats + list_lat
    # print(list_lats)

    list_lons = []
    for i, val in enumerate(lat_lon_comb):
        clear_lon = ((lat_lon_comb[i])[1])
        float_lon = float(clear_lon)
        list_lon = [float_lon]
        list_lons = list_lons + list_lon
    # print(list_lons)
    # print(list_lats[1], list_lons[1])
    return list_lons


def get_lats(lat_start, lat_stop, lon_start, lon_stop):
    lat_delta = round(lat_start - lat_stop, 3)
    lon_delta = round(lon_start - lon_stop, 3)
    lat_count = round(lat_delta / step)
    lon_count = round(lon_delta / step)

    # print(lat_count, 'vert line')
    # print(lon_count, 'horizon line')
    # print(lat_count * lon_count, 'points ')

    lons = []
    lats = []

    for i in arange(lon_start, lon_stop, step):
        lon = [round(i, 3)]
        lons = lons + lon

    for i in arange(lat_start, lat_stop, step):
        lat = [round(i, 3)]
        lats = lats + lat

    # print('all lats: ', lats)
    # print('all lons: ', lons)

    lat_lon_comb = [(x, y) for x in lats for y in lons]
    # print('list of all combinations: ', lat_lon_comb)

    list_lats = []
    for i, val in enumerate(lat_lon_comb):
        clear_lat = ((lat_lon_comb[i])[0])
        float_lat = float(clear_lat)
        list_lat = [float_lat]
        list_lats = list_lats + list_lat
    # print(list_lats)

    list_lons = []
    for i, val in enumerate(lat_lon_comb):
        clear_lon = ((lat_lon_comb[i])[1])
        float_lon = float(clear_lon)
        list_lon = [float_lon]
        list_lons = list_lons + list_lon
    # print(list_lons)
    # print(list_lats[1], list_lons[1])
    return list_lats
