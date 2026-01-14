from flask import Blueprint

visitor_bp = Blueprint("visitor", __name__)

@visitor_bp.route("/farms/<farm_id>/interactions", methods=["POST"])
def add_visitor_interaction(farm_id):
    return {"message": f"Stub: Add visitor interaction for farm {farm_id}"}

@visitor_bp.route("/farms/<farm_id>/interactions", methods=["GET"])
def get_visitor_interactions(farm_id):
    return {"message": f"Stub: List visitor interactions for farm {farm_id}"}
