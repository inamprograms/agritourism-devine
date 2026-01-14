from flask import Blueprint

farmer_bp = Blueprint("farmer", __name__)

@farmer_bp.route("/farmers", methods=["POST"])
def create_farmer():
    return {"message": "Stub: Create farmer endpoint"}

@farmer_bp.route("/farmers/<farmer_id>", methods=["GET"])
def get_farmer(farmer_id):
    return {"message": f"Stub: Get farmer {farmer_id}"}
