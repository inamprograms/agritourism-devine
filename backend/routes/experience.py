from flask import Blueprint

experience_bp = Blueprint("experience", __name__)

@experience_bp.route("/farms/<farm_id>/experiences", methods=["GET"])
def get_experiences(farm_id):
    return {"message": f"Stub: List experiences for farm {farm_id}"}
