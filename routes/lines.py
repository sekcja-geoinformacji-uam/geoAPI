from flask import Blueprint, request
from flasgger import swag_from
import json as jsn
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.coordinates import get_coordinates
from pyproj.exceptions import CRSError
from utils.get_UTM_zone import get_UTM_zone
from utils.read_data import read_data

lines_bp = Blueprint('lines', __name__)

@lines_bp.post('/length')
@swag_from('./docs/lines/length.yml')
def length():
    lines = read_data(request.json)

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
    lines = read_data(request.json)

    coords, idx = get_coordinates(lines, return_index=True)
    sequences = [n for i in np.unique(idx, return_counts=True)[1].tolist() for n in range(0, i)]
    
    points = [Point(x, y) for x, y in coords.tolist()]
    points = gpd.GeoDataFrame({'line': idx.tolist(), 'sequence': sequences, 'geometry': points})
    return points.to_json()

@lines_bp.post('/interpolate')
def interpolate():
    json = jsn.dumps(request.json)
    lines:gpd.GeoDataFrame = gpd.read_file(json, driver='GeoJSON')
    spacing = request.args.get('spacing', default=None)
    n_points = request.args.get('n_points', default=None)
    spacing = float(spacing) if spacing is not None else spacing
    n_points = int(n_points) if n_points is not None else n_points

    pointsResult = lines.copy()
    for i, line in lines.iterrows():
        if spacing is not None:
            distances = np.arange(0, line.geometry.length, spacing)
            pointsList = [line.geometry.interpolate(d) for d in distances]
            pointsResult.loc[i, 'geometry'] = MultiPoint(pointsList)
        elif n_points is not None:
            distances = np.linspace(0, line.geometry.length, n_points)
            pointsList = [line.geometry.interpolate(d) for d in distances]
            pointsResult.loc[i, 'geometry'] = MultiPoint(pointsList)
    
    return pointsResult.to_json()
