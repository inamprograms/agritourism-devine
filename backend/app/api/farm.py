from flask import Blueprint, jsonify, request, g
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service

farm_bp = Blueprint("farm", __name__)


@farm_bp.route("/farms", methods=["GET"])
@require_auth
def list_farms():
    """Returns all farms for the logged-in user."""
    farms = farmer_service.get_farms_for_user(g.user_id)
    return jsonify({"farms": farms}), 200


@farm_bp.route("/farms", methods=["POST"])
@require_auth
def create_farm():
    """
    Explicitly create a new farm.
    Body: { name, farm_type, size_category (optional), location (optional), description (optional) }
    """
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    farm_type = data.get("farm_type", "").strip()
    size_category = data.get("size_category", "medium").strip()
    location = data.get("location", "").strip() or None
    description = data.get("description", "").strip() or None

    if not name:
        return jsonify({"error": "Farm name is required"}), 400
    if not farm_type:
        return jsonify({"error": "farm_type is required"}), 400

    farm = farmer_service.create_farm(
        user_id=g.user_id,
        name=name,
        farm_type=farm_type,
        size_category=size_category,
        location=location,
        description=description,
    )
    return jsonify({"farm": farm}), 201


@farm_bp.route("/farms/<farm_id>", methods=["GET"])
@require_auth
def get_farm(farm_id):
    """Get a single farm by id."""
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    farm = farmer_service.get_farm_by_id(farm_id)
    if not farm:
        return jsonify({"error": "Farm not found"}), 404
    return jsonify({"farm": farm}), 200