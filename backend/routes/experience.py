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
