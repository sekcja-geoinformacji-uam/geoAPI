from flask import Flask, request
import math
import numpy as np
import numpy.ma as ma
import geopandas as gpd
from jenkspy import JenksNaturalBreaks
import json as jsn
from pyproj.exceptions import CRSError

from routes.misc import misc_bp

app = Flask(__name__)
app.register_blueprint(misc_bp, url_prefix='/misc')

@app.post("/centroid")
def centroid():
    json = jsn.dumps(request.json)
    points = gpd.read_file(json, driver='GeoJSON')
    centroid = points.dissolve().centroid
    return centroid.to_json()

@app.post("/nearest_n")
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

@app.post("/jenks")
def jenks():
    nclass = int(request.args.get("nclass"))
    colname = request.args.get("colname")

    json = jsn.dumps(request.json)
    points = gpd.read_file(json, driver='GeoJSON')
    
    jnb = JenksNaturalBreaks(nclass)

    try:
        jnb.fit(points[colname])
    except KeyError:
        return {'KeyError': 'No column found named ' + colname}, 400
    except TypeError:
        return {'TypeError': 'Column must contain numeric values'}, 400

    points["class"] = jnb.labels_

    return points.to_json()

def get_UTM_zone(bounds):
        if math.ceil((bounds[2] + 180) / 6) - math.ceil((bounds[0] + 180) / 6) > 1:
            return 3857
        else:
            zone = math.ceil(((bounds[2] + bounds[0]) / 2 + 180) / 6)
            if bounds[3] >= 0:
                crs = int("326" + str(zone))
            else:
                crs = int("327" + str(zone))
            return crs

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
