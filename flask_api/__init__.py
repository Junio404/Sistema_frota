from flask import Flask
from config import Config
from flask_api.models.db import init_db
from flask_api.routes.routes import bp as routes_bp
from flask_api.routes.routes_api import bp_routes_api
from flask_api.routes.routes_create import bp_routes_create
from flask_api.routes.routes_delete import bp_routes_delete
from flask_api.routes.routes_index_options import bp_routes_index_options
from flask_api.routes.routes_read import bp_routes_read
from flask_api.routes.routes_report import bp_routes_report
from flask_api.routes.routes_update import bp_routes_update

def create_app():
    app = Flask(__name__)
    init_db()
    app.config.from_object(Config)
    app.register_blueprint(bp_routes_api)
    app.register_blueprint(bp_routes_create)
    app.register_blueprint(bp_routes_delete)
    app.register_blueprint(bp_routes_index_options)
    app.register_blueprint(bp_routes_read)
    app.register_blueprint(bp_routes_report)
    app.register_blueprint(bp_routes_update)
    

    
    return app