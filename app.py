from flask import Flask, request
import numpy as np
import numpy.ma as ma
import geopandas as gpd
import json as jsn

app = Flask(__name__)


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
    points.to_crs(epsg=3857, inplace=True)
    distance_matrix = np.array(points.geometry.apply(lambda x: points.distance(x).astype(np.int64)))
    points['nearest_dist'] = np.min(ma.masked_array(distance_matrix, mask = distance_matrix==0), axis=1)
    points['nearest'] = np.argmin(ma.masked_array(distance_matrix, mask = distance_matrix==0), axis=1)
    points.to_crs(epsg=4326, inplace=True)
    return points.to_json()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
