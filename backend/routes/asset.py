from flask import Blueprint

asset_bp = Blueprint("asset", __name__)

@asset_bp.route("/farms/<farm_id>/assets", methods=["POST"])
def add_asset(farm_id):
    return {"message": f"Stub: Add asset for farm {farm_id}"}

@asset_bp.route("/farms/<farm_id>/assets", methods=["GET"])
def list_assets(farm_id):
    return {"message": f"Stub: List assets for farm {farm_id}"}
