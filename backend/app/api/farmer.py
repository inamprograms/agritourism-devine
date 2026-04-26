from flask import Blueprint, jsonify, g
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service

farmer_bp = Blueprint("farmer", __name__)

@farmer_bp.route("/farmers", methods=["GET"])
@require_auth
def get_farmer():
    farmer = farmer_service.get_farmer_for_user(g.user_id)
    return jsonify({"farmer": farmer}), 200