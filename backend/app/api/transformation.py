from flask import Blueprint, request, jsonify, g
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.farmer_service import farmer_service
from app.auth.decorators import require_auth
from app.services.plan_service import plan_service

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

    # Fetch full farm record from DB
    farm_data = farmer_service.get_farm_by_id(farm_id)
    if not farm_data:
        return jsonify({"error": "Farm not found"}), 404

    # Fetch farmer profile for goals/budget context
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}

    # Merge farmer profile into farm_data so scoring engine
    # has full context — budget, goals, visitor experience etc.
    farm_data["budget_range"] = farmer_profile.get("budget_range", "low")
    farm_data["family_helpers"] = farmer_profile.get("family_helpers", 0)
    farm_data["visitor_experience"] = farmer_profile.get("visitor_experience", "none")
    farm_data["primary_goal"] = farmer_profile.get("primary_goal", "income")
    farm_data["timeline"] = farmer_profile.get("timeline", "months")
    farm_data["province"] = farmer_profile.get("province")

    # Generate personalized experiences based on real farm data
    experiences = transformation_service.generate_experiences(farm_data)

    # Save to DB
    experience_service.save_experiences(farm_id, experiences)

    # Track usage
    plan_service.increment_transformation_counter(g.user_id)

    return jsonify({
        "farm_id": farm_id,
        "message": "Experiences generated successfully",
        "total_experiences": len(experiences),
        "breakdown": {
            "level_1": len([e for e in experiences if e["level"] == 1]),
            "level_2": len([e for e in experiences if e["level"] == 2]),
            "level_3": len([e for e in experiences if e["level"] == 3]),
        }
    }), 200


@transformation_bp.route("/farms/<farm_id>/experiences", methods=["GET"])
@require_auth
def get_farm_experiences(farm_id):
    """Get all experiences for a specific farm."""
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    experiences = experience_service.list_experiences(farm_id)
    return jsonify({
        "farm_id": farm_id,
        "experiences": experiences
    }), 200