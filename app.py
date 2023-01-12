from flask import Flask, request
import math
import numpy as np
import numpy.ma as ma
import geopandas as gpd
from jenkspy import JenksNaturalBreaks
import json as jsn
from pyproj.exceptions import CRSError

app = Flask(__name__)

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

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/tomek")
def wodzionka():
    text = "<p>Mmmm. Wodzionka, suchy chlyb i wody szklonka.<br>Mmmm. Wodzionka, to nojlepszo z wszystkich ślonskich zup.<br> Mmmm. Wodzionka, jak jom zrobi moja żonka.<br> Mmmm. Wodzionka, to jes łósmy świata cud.</p>"
    return text


@app.route("/olek/<tekst>")
def papuga(tekst):
    tekst = "<p>🦜" + tekst + "</p>"
    return tekst


@app.route("/Filip_Fujak")
def grruszki_w_winie():
    return "<p>Potem wrzucę przepis jak się rozbudzę ^^</p>"


@app.post("/json")
def process_json():
    json = request.json
    json['x'] = 15
    json['y'] = int(request.args.get('value'))
    return json


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


@app.route("/medoid", methods=['POST'])
def medoid():
    from shapely.wkt import loads
    json = jsn.dumps(request.json)#szukanie środka ciężkości
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

    centroid = points.dissolve().centroid
    # szukanie najbliższego punktu do centroidu
    points['id'] = range(0, points.shape[0])
    points['Dist'] = points.apply(lambda row: centroid.distance(row.geometry), axis=1)
    geoseries = points.iloc[points['Dist'].argmin()]
    # wybranie wiersza z koordynatami
    # geoseries[0] oznacza nazwę punktu
    closest_point = geoseries[1]
    closest_point = str(closest_point)
    # wyciągnięcie odpowiednich danych z obiektu POINT
    output = closest_point.lstrip('POINT (').rstrip(')')
    output_list_x_y = output.split(' ')

    if(request.args.get('format')=='json'):
        json_output = {
            'name': geoseries[0],
            'x': output_list_x_y[0],
            'y': output_list_x_y[1]
        }
        return json_output
    elif request.args.get('format')=='geojson':
        geojson_output = points[points['id'] == points['Dist'].argmin()].to_json()
        return geojson_output
    elif request.args.get('format')=='point':
        return output
    else:
        geojson_output = points[points['id'] == points['Dist'].argmin()].to_json()
        return geojson_output


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
