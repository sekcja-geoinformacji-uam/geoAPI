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


@app.route("/medoid", methods=['POST'])
def medoid():
    from shapely.wkt import loads
    json = jsn.dumps(request.json)#szukanie środka ciężkości
    points = gpd.read_file(json, driver='GeoJSON')
    centroid = points.dissolve().centroid
    #szukanie najbliższego punktu do centroidu
    points['Dist'] = points.apply(lambda row: centroid.distance(row.geometry), axis=1)
    geoseries = points.iloc[points['Dist'].argmin()]
    #wybranie wiersza z koordynatami
    #geoseries[0] oznacza nazwę punktu
    closest_point = geoseries[1]
    # Strworzenie punktu z WKT POINT
    closest_point = loads(str(closest_point))
    output = str(closest_point)
    #wyciągnięcie odpowiednich danych z obiektu POINT
    output = output.lstrip('POINT (').rstrip(')')
    output_list = output.split(' ')
    #stworzenie dictionary z nazwą punktu i koordynatami
    dictionary = {
        'name': geoseries[0],
        'x': output_list[0],
        'y': output_list[1]
    }
    if (request.args.get('json')=='True' or request.args.get('json')=='true'): return dictionary
    else: return output 


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
