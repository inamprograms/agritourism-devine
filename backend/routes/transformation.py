from flask import Blueprint

transformation_bp = Blueprint("transformation", __name__)

@transformation_bp.route("/farms/<farm_id>/transform", methods=["POST"])
def transform_farm(farm_id):
    return {"message": f"Stub: Run transformation for farm {farm_id}"}
