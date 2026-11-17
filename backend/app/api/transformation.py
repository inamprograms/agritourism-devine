from flask import Blueprint, request, jsonify, g, current_app
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.farmer_service import farmer_service
from app.auth.decorators import require_auth
from app.services.plan_service import plan_service
from app.services.farm_normalizer import normalize_farm

transformation_bp = Blueprint("transformation", __name__)
transformation_service = TransformationService()


@transformation_bp.route("/farms/<farm_id>/transform", methods=["POST"])
@require_auth
def transform_farm(farm_id):
    """
    Run personalized farm transformation for a specific farm.
    Reads all farm data from DB — no body needed from frontend.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    farm_data = farmer_service.get_farm_by_id(farm_id)
    if not farm_data:
        return jsonify({"error": "Farm not found"}), 404

    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}

    # None means "not answered". We no longer invent defaults like "low" or 0.
    farm_data["budget_range"] = farmer_profile.get("budget_range")
    farm_data["family_helpers"] = farmer_profile.get("family_helpers")
    farm_data["visitor_experience"] = farmer_profile.get("visitor_experience")
    farm_data["primary_goal"] = farmer_profile.get("primary_goal")
    farm_data["timeline"] = farmer_profile.get("timeline")
    farm_data["province"] = farmer_profile.get("province")
    farm_data["country"] = farmer_profile.get("country")

    # Clean messy input (plurals, typos, "5 buffaloes") before the engine sees it
    farm_data, unrecognized = normalize_farm(farm_data)
    if unrecognized:
        current_app.logger.warning("Unrecognized farm input (farm %s): %s", farm_id, unrecognized)

    experiences = transformation_service.generate_experiences(farm_data)

    try:
        result = experience_service.save_experiences(farm_id, experiences)
    except Exception:
        current_app.logger.exception("save_experiences failed for farm %s", farm_id)
        return jsonify({"error": "Could not save experiences. Please try again."}), 500

    plan_service.increment_transformation_counter(g.user_id)

    return jsonify({
        "farm_id": farm_id,
        "message": "Experiences generated successfully",
        "total_experiences": len(experiences),
        "changes": result,
    }), 200