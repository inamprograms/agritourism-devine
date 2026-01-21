from flask import Blueprint, request, jsonify
from services.carbon_service import CarbonCreditService

# Blueprint
carbon_bp = Blueprint("carbon_bp", __name__, url_prefix="/carbon")

# Service instance
carbon_service = CarbonCreditService()


@carbon_bp.route("/estimate", methods=["POST"])
def estimate_carbon():
    """
    Endpoint to calculate carbon credits for agroforestry.
    Accepts JSON input and returns carbon estimates.
    """
    try:
        data = request.get_json() or {}

        # Call service (schema + rules handled inside)
        result = carbon_service.calculate(data)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
