from flask import Blueprint, request, jsonify
from services.transformation_service import TransformationService
from services.experience_service import experience_service

transformation_bp = Blueprint("transformation", __name__)
transformation_service = TransformationService()

@transformation_bp.route("/farms/<farm_id>/transform", methods=["POST"])
def transform_farm(farm_id):    
    farm_data = request.get_json()
    if not farm_data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    # Example validation
    if "animals" not in farm_data or not isinstance(farm_data["animals"], list):
        return jsonify({"error": "Missing or invalid 'animals' field"}), 400

    if "farm_type" not in farm_data:
        return jsonify({"error": "Missing 'farm_type' field"}), 400
    
    # Generate experiences from rules
    experiences = transformation_service.generate_experiences(farm_data)
    
    # Save experiences for farm
    experience_service.save_experiences(farm_id, experiences)

    return jsonify({
        "farm_id": farm_id,
        "message": "Experiences generated successfully"
    }), 200