# routes/carbon_routes.py

from flask import Blueprint, request, jsonify
from services.carbon_service import CarbonCreditService

# Create blueprint
carbon_bp = Blueprint("carbon_bp", __name__, url_prefix="/carbon")

# Initialize service
carbon_service = CarbonCreditService()


@carbon_bp.route("/estimate", methods=["POST"])
def estimate_carbon():
    """
    Endpoint to calculate carbon credits for agroforestry.
    Expects JSON payload:
    {
        "land_size_hectares": float,
        "tree_density": str,
        "tree_age": str,
        "activity_level": str
    }
    """
    try:
        raw_data = request.get_json() or {}
        result = carbon_service.calculate(raw_data)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def register_carbon_routes(app):
    """
    Registers the carbon blueprint to Flask app.
    """
    app.register_blueprint(carbon_bp)
