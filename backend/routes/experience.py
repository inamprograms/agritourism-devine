from flask import Blueprint, jsonify, request
from services.experience_service import experience_service

experience_bp = Blueprint("experience", __name__)

@experience_bp.route("/farms/<farm_id>/experiences", methods=["GET"])
def get_experiences(farm_id):
    level = request.args.get("level", type=int)
    experiences = experience_service.list_experiences(farm_id, level)
    return jsonify({
        "farm_id": farm_id,
        "experiences": experiences
    })

# --- Enable experience ---
@experience_bp.route("/farms/<farm_id>/experiences/enable", methods=["PATCH"])
def enable_experience(farm_id):
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    updated = experience_service.enable_experience(farm_id, title)
    if not updated:
        return jsonify({"error": "Experience not found"}), 404
    return jsonify({
        "farm_id": farm_id,
        "experience": updated
    })


# --- Disable experience ---
@experience_bp.route("/farms/<farm_id>/experiences/disable", methods=["PATCH"])
def disable_experience(farm_id):
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