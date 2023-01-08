from flask import Flask, request
import geopandas as gpd
from jenkspy import JenksNaturalBreaks
import json as jsn
from random import randint

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
