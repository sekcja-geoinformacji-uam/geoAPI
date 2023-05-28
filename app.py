from flask import Flask, request
from flasgger import Swagger

from routes.misc import misc_bp
from routes.general import general_bp
from routes.points import points_bp
from utils.template import template
from routes.lines import lines_bp

app = Flask(__name__)
swagger = Swagger(app, template=template)
app.register_blueprint(misc_bp, url_prefix='/misc')
app.register_blueprint(lines_bp, url_prefix='/lines')
app.register_blueprint(general_bp, url_prefix='/')
app.register_blueprint(points_bp, url_prefix='/points')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
