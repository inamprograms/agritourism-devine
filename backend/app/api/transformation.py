from flask import Blueprint, request, jsonify, g
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.farmer_service import farmer_service
from app.auth.decorators import require_auth
from app.services.plan_service import plan_service

transformation_bp = Blueprint("transformation", __name__)
transformation_service = TransformationService()

@transformation_bp.route("/farms/<farm_id>/transform", methods=["POST"])
@require_auth
def transform_farm(farm_id):
    """
    Run farm transformation for a specific farm.
    farm_id comes from the URL - client picks which farm to transform.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    farm_data = request.get_json()
    if not farm_data:
        return jsonify({"error": "Missing JSON body"}), 400

    if "animals" not in farm_data or not isinstance(farm_data["animals"], list):
        return jsonify({"error": "Missing or invalid 'animals' field"}), 400

    if "farm_type" not in farm_data:
        return jsonify({"error": "Missing 'farm_type' field"}), 400

    experiences = transformation_service.generate_experiences(farm_data)
    experience_service.save_experiences(farm_id, experiences)
    plan_service.increment_transformation_counter(g.user_id)

    return jsonify({
        "farm_id": farm_id,
        "message": "Experiences generated successfully"
    }), 200
    

@transformation_bp.route("/farms/<farm_id>/experiences", methods=["GET"])
@require_auth
def get_farm_experiences(farm_id):
    """
    Get all experiences for a specific farm.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    experiences = experience_service.list_experiences(farm_id)
    return jsonify({
        "farm_id": farm_id,
        "experiences": experiences
    }), 200