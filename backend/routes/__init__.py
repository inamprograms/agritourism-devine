from .health import health_bp

def register_routes(app):
    app.register_blueprint(health_bp)
