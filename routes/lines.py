from flask import Blueprint, request
import json as jsn
import numpy as np
import geopandas as gpd
from shapely import Point, get_coordinates
from pyproj.exceptions import CRSError
from utils.get_UTM_zone import get_UTM_zone

lines_bp = Blueprint('lines', __name__)

@lines_bp.post('/length')
def length():
    json = jsn.dumps(request.json)
    lines = gpd.read_file(json, driver='GeoJSON')

    crs = int(request.args.get('crs', default=4326))
    if lines.crs.to_authority()[1] != str(crs):
        try:
            lines.to_crs(epsg=crs, inplace=True)
        except CRSError:
            return {'CRSError': f'Projection EPSG:{crs} not found!'}, 400
    
    if crs == 4326 and int(request.args.get('crs', default=-1)) != 4326:
        crs = get_UTM_zone(lines.total_bounds)
        try:
            lines.to_crs(epsg=crs, inplace=True)
        except CRSError:
            crs = 4326
            pass
    
    lines['length'] = lines.length
    return lines.to_json()

@lines_bp.post('/vertices')
def vertices():
    json = jsn.dumps(request.json)
    lines = gpd.read_file(json, driver='GeoJSON')

    coords, idx = get_coordinates(lines, return_index=True)
    sequences = [n for i in np.unique(idx, return_counts=True)[1].tolist() for n in range(0, i)]
    
    points = [Point(x, y) for x, y in coords.tolist()]
    points = gpd.GeoDataFrame({'line': idx.tolist(), 'sequence': sequences, 'geometry': points})
    return points.to_json()