from flask import Blueprint, jsonify, g, request
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service

farmer_bp = Blueprint("farmer", __name__)

@farmer_bp.route("/farmers", methods=["GET"])
@require_auth
def get_farmer():
    farmer = farmer_service.get_farmer_for_user(g.user_id)
    return jsonify({"farmer": farmer}), 200


@farmer_bp.route("/farmer/profile", methods=["GET"])
@require_auth
def get_farmer_profile():
    """Get farmer profile for the authenticated user."""
    farmer = farmer_service.get_farmer_for_user(g.user_id)
    if not farmer:
        return jsonify({"error": "Farmer profile not found"}), 404
    return jsonify({"farmer": farmer}), 200


@farmer_bp.route("/farmer/profile", methods=["PATCH"])
@require_auth
def update_farmer_profile():
    """
    Update farmer profile details — budget, goals, timeline etc.
    """
    data = request.get_json() or {}

    allowed_fields = {
        "budget_range", "family_helpers", "visitor_experience",
        "primary_goal", "timeline", "province", "location", "country"
    }

    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "No valid fields to update"}), 400

    updated = farmer_service.update_farmer_profile(g.user_id, update_data)
    if not updated:
        return jsonify({"error": "Update failed"}), 500

    return jsonify({"farmer": updated}), 200

