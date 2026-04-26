from flask import Blueprint, jsonify, g
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service

farm_bp = Blueprint("farm", __name__)

@farm_bp.route("/farms", methods=["GET"])
@require_auth
def list_farms():
    farms = farmer_service.get_farms_for_user(g.user_id)
    return jsonify({"farms": farms}), 200


@farm_bp.route("/farms/<farm_id>", methods=["GET"])
@require_auth
def get_farm(farm_id):
    farm = farmer_service.get_farm_by_id(farm_id)
    if not farm:
        return jsonify({"error": "Farm not found"}), 404
    return jsonify({"farm": farm}), 200