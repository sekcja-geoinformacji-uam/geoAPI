import json as jsn
from flask import Blueprint, request
from flasgger import swag_from
import geopandas as gpd
import numpy as np
import numpy.ma as ma
from pyproj.exceptions import CRSError
from utils.get_UTM_zone import get_UTM_zone

points_bp = Blueprint('points', __name__)

@points_bp.post("/nearest_n")
@swag_from('./docs/points/nearest_n.yml')
def nearest_neighbour():
    json = jsn.dumps(request.json)
    points = gpd.read_file(json, driver='GeoJSON')

    crs = int(request.args.get('crs', default=4326))
    if points.crs.to_authority()[1] != str(crs):
        try:
            points.to_crs(epsg=crs, inplace=True)
        except CRSError:
            return {'CRSError': f'Projection EPSG:{crs} not found!'}, 400
    
    if crs == 4326 and int(request.args.get('crs', default=-1)) != 4326:
        crs = get_UTM_zone(points.total_bounds)
        try:
            points.to_crs(epsg=crs, inplace=True)
        except CRSError:
            crs = 4326
            pass

    distance_matrix = np.array(points.geometry.apply(lambda x: points.distance(x).astype(np.int64)))
    points['nearest_dist'] = np.min(ma.masked_array(distance_matrix, mask = distance_matrix==0), axis=1)
    points['nearest'] = np.argmin(ma.masked_array(distance_matrix, mask = distance_matrix==0), axis=1)
    points["epsg_used"] = crs
    points.to_crs(epsg=4326, inplace=True)
    return points.to_json()

