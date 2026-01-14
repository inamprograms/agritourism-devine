from flask import Blueprint

growth_bp = Blueprint("growth", __name__)

@growth_bp.route("/farmers/<farmer_id>/growth", methods=["GET"])
def get_growth(farmer_id):
    return {"message": f"Stub: Get growth state for farmer {farmer_id}"}
