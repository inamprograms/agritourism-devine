from flask import Flask
from flask_cors import CORS

from config import Config
from app.api import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    register_routes(app)

    return app