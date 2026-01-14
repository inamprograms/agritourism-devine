from .health import health_bp
from .farmer import farmer_bp
from .farm import farm_bp
from .asset import asset_bp
from .experience import experience_bp
from .transformation import transformation_bp
from .ai import ai_bp
from .visitor import visitor_bp
from .growth import growth_bp

def register_routes(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(farm_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(experience_bp)
    app.register_blueprint(transformation_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(visitor_bp)
    app.register_blueprint(growth_bp)
