from flask import Blueprint

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/farms/<farm_id>/ai", methods=["POST"])
def ai_interaction(farm_id):
    return {"message": f"Stub: AI interaction for farm {farm_id}"}
