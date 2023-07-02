from flask import Blueprint, request
from flasgger import swag_from
import geopandas as gpd
import json as jsn
from shapely.geometry import Polygon

general_bp = Blueprint('general', __name__)

@general_bp.post('/bbox')
@swag_from('./docs/general/bbox.yml')
def bbox():
    json = jsn.dumps(request.json)
    layer = gpd.read_file(json, driver='GeoJSON')
    bbox = layer.bounds
    polygon = Polygon([(bbox.minx[0], bbox.miny[0]),
                       (bbox.minx[0], bbox.maxy[0]),
                       (bbox.maxx[0], bbox.maxy[0]),
                       (bbox.maxx[0], bbox.miny[0]),
                       (bbox.minx[0], bbox.miny[0])])
    response = {"type": "Polygon", "coordinates": [list(polygon.exterior.coords)]}
    return jsn.dumps(response), 200
