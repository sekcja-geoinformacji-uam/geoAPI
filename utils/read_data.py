import geopandas as gpd
import json as jsn

def read_data(data):
    if data['type'] in ('FeatureCollection', 'Feature'):
        return gpd.read_file(jsn.dumps(data), driver='GeoJSON')
    if data['type'] == 'wkt':
        return gpd.GeoSeries.from_wkt(data['wkt'])