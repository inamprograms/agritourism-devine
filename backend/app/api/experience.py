from flask import Blueprint, jsonify, request, g
from app.services.experience_service import experience_service
from app.services.farmer_service import farmer_service
from app.auth.decorators import require_auth

experience_bp = Blueprint("experience", __name__)

MAX_PRICE = 1_000_000


def _parse_bool(value):
    """Turn the string 'true'/'false' from a URL into a real True/False."""
    if value is None:
        return None
    return value.strip().lower() in ("true", "1", "yes")


def _clean_price(value):
    """Optional price chosen by the farmer. Returns (price, error).
    None or blank means 'no price set'. 0 is allowed."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None, None
    if isinstance(value, bool):
        return None, "price must be a number"
    try:
        price = round(float(value), 2)
    except (TypeError, ValueError):
        return None, "price must be a number"
    if price < 0 or price > MAX_PRICE:
        return None, "price is out of range"
    return price, None


@experience_bp.route("/farms/<farm_id>/experiences", methods=["GET"])
@require_auth
def get_experiences(farm_id):
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    level = request.args.get("level", type=int)
    enabled_only = _parse_bool(request.args.get("enabled_only"))
    experiences = experience_service.list_experiences(farm_id, level, enabled_only=enabled_only)
    return jsonify({
        "farm_id": farm_id,
        "experiences": experiences
    })


# --- Enable experience (optional: the farmer's own price) ---
@experience_bp.route("/farms/<farm_id>/experiences/enable", methods=["PATCH"])
@require_auth
def enable_experience(farm_id):
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    price, error = _clean_price(data.get("price"))
    if error:
        return jsonify({"error": error}), 400

    updated = experience_service.enable_experience(farm_id, title, price=price, currency="USD")
    if not updated:
        return jsonify({"error": "Experience not found"}), 404
    return jsonify({
        "farm_id": farm_id,
        "experience": updated
    })


# --- Disable experience ---
@experience_bp.route("/farms/<farm_id>/experiences/disable", methods=["PATCH"])
@require_auth
def disable_experience(farm_id):
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    updated = experience_service.disable_experience(farm_id, title)
    if not updated:
        return jsonify({"error": "Experience not found"}), 404
    return jsonify({
        "farm_id": farm_id,
        "experience": updated
    })