from flask import Blueprint

farm_bp = Blueprint("farm", __name__)

@farm_bp.route("/farms", methods=["POST"])
def create_farm():
    return {"message": "Stub: Create farm endpoint"}

@farm_bp.route("/farms/<farm_id>", methods=["GET"])
def get_farm(farm_id):
    return {"message": f"Stub: Get farm {farm_id}"}
