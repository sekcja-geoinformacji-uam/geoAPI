from flask import Blueprint, request
from flasgger import swag_from
import geopandas as gpd
import json as jsn
from shapely.geometry import Polygon
from jenkspy import JenksNaturalBreaks

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
    return response, 200

@general_bp.post('/centroid')
@swag_from('./docs/general/centroid.yml')
def centroid():
    json = jsn.dumps(request.json)
    points = gpd.read_file(json, driver='GeoJSON')
    centroid = points.dissolve().centroid
    centroid_json = jsn.loads(centroid.to_json())
    response = centroid_json['features'][0]['geometry']

    return response

@general_bp.post('/buffer')
@swag_from('./docs/general/buffer.yml')
def buffer():
    payload = request.json
    buffer = payload['buffer']
    geojson = payload['geojson']
    geom = gpd.read_file(jsn.dumps(geojson), driver='GeoJSON')
    buffered = geom.buffer(buffer)
    buffered_json = jsn.loads(buffered.to_json())
    response = buffered_json['features'][0]['geometry']
    return response, 200

@general_bp.post("/jenks")
@swag_from('./docs/general/jenks.yml')
def jenks():
    nclass = int(request.args.get("nclass"))
    colname = request.args.get("colname")

    json = jsn.dumps(request.json)
    features = gpd.read_file(json, driver='GeoJSON')

    jnb = JenksNaturalBreaks(nclass)

    try:
        jnb.fit(features[colname])
    except KeyError:
        return {'KeyError': 'No column found named ' + colname}, 400
    except TypeError:
        return {'TypeError': 'Column must contain numeric values'}, 400

    features["class"] = jnb.labels_
    response = jsn.loads(features.to_json())
    return response, 200