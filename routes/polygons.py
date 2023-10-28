from flask import Blueprint, request
from flasgger import swag_from

from utils.read_data import read_data

polygons_bp = Blueprint('polygons', __name__)

@polygons_bp.post("/to_line")
@swag_from('./docs/polygons/to_line.yml')
def polygon_to_line():
    """
    Returns a boundary line of a polygon
    """
    print(request.json)
    polygon = read_data(request.json)
    line = polygon.boundary
    return line.to_json()

@polygons_bp.post("/simplify")
@swag_from('./docs/polygons/simplify.yml')
def polygon_simplify():
    """
    Returns a simplified polygon
    """
    polygon = read_data(request.json)
    tolerance = float(request.args.get('tolerance', default=0.01))
    polygon = polygon.simplify(tolerance)
    return polygon.to_json()
