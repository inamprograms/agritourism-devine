from flask import Flask
from flask_cors import CORS
from config import Config
from app.api import register_routes
from app.middleware.auth_middleware import (
    load_user_from_request,
    update_auth_cookies
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config["SECRET_KEY"] = app.config["FLASK_SECRET_KEY"]
    
    CORS(
        app,
        origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://192.168.64.1:8080",
            Config.FRONTEND_URL,
        ],
        supports_credentials=True
    )
    
    app.before_request(load_user_from_request)
    app.after_request(update_auth_cookies)
    
    register_routes(app)

    return app