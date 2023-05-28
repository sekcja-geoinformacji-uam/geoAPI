from flask import Blueprint, request
from flasgger import swag_from
import geopandas as gpd
import json as jsn

general_bp = Blueprint('general', __name__)

@general_bp.post('/bbox')
@swag_from('./docs/general/bbox.yml')
def bbox():
    json = jsn.dumps(request.json)
    layer = gpd.read_file(json, driver='GeoJSON')
    bbox = layer.bounds
    response = {
        'minx': bbox.minx[0],
        'miny': bbox.miny[0],
        'maxx': bbox.maxx[0],
        'maxy': bbox.maxy[0]
    }
    return response, 200