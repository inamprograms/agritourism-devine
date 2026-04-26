from flask import Blueprint, request, jsonify, g
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.farmer_service import farmer_service
from app.auth.decorators import require_auth
from app.services.plan_service import plan_service

transformation_bp = Blueprint("transformation", __name__)
transformation_service = TransformationService()

@transformation_bp.route("/farms/transform", methods=["POST"])
@require_auth
def transform_farm():
    farm_data = request.get_json()
    if not farm_data:
        return jsonify({"error": "Missing JSON body"}), 400

    if "animals" not in farm_data or not isinstance(farm_data["animals"], list):
        return jsonify({"error": "Missing or invalid 'animals' field"}), 400

    if "farm_type" not in farm_data:
        return jsonify({"error": "Missing 'farm_type' field"}), 400

    # Get or create farmer/farm for this user — replaces hardcoded farm_id
    ids = farmer_service.get_or_create_for_user(
        user_id=g.user_id,
        farm_type=farm_data["farm_type"]
    )
    farm_id = ids["farm_id"]

    experiences = transformation_service.generate_experiences(farm_data)
    experience_service.save_experiences(farm_id, experiences)
    plan_service.increment_transformation_counter(g.user_id)
    
    return jsonify({
        "farm_id": farm_id,
        "message": "Experiences generated successfully"
    }), 200
    
# NEW ROUTE: called by Dashboard and Transform on page load
@transformation_bp.route("/farms/my", methods=["GET"])
@require_auth
def get_my_farm():
    ids = farmer_service.get_farm_for_user(g.user_id)

    if not ids:
        return jsonify({"farm_id": None, "experiences": []}), 200

    experiences = experience_service.list_experiences(ids["farm_id"])

    return jsonify({
        "farm_id": ids["farm_id"],
        "experiences": experiences
    }), 200