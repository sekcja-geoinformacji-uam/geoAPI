from flask import Flask, request
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
