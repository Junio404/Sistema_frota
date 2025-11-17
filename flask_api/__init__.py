from flask import Flask
from config import Config
from flask_api.models.db import init_db
from flask_api.routes.routes import bp as routes_bp

def create_app():
    app = Flask(__name__)
    init_db()
    app.config.from_object(Config)
    app.register_blueprint(routes_bp)

    
    return app