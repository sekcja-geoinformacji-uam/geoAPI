from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/tomek")
def wodzionka():
    text = "<p>Mmmm. Wodzionka, suchy chlyb i wody szklonka.<br>Mmmm. Wodzionka, to nojlepszo z wszystkich ślonskich zup.<br> Mmmm. Wodzionka, jak jom zrobi moja żonka.<br> Mmmm. Wodzionka, to jes łósmy świata cud.</p>"
    return text


@app.post("/json")
def process_json():
    json = request.json
    json['x'] = 15
    json['y'] = int(request.args.get('value'))
    return json


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
