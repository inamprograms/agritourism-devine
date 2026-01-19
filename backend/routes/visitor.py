# routes/visitor.py

from flask import Blueprint
from services.visitor_service import visitor_service

visitor_bp = Blueprint("visitor", __name__)

@visitor_bp.route("/farms/<farm_id>/interactions", methods=["POST"])
def add_visitor_interaction(farm_id):
    return {"message": f"Stub: Add/list visitor interaction for farm {farm_id}"}

@visitor_bp.route("/farms/<int:farm_id>/experiences/<int:experience_id>", methods=["GET"])
def get_experience_for_visitor(farm_id, experience_id):
    """
    Returns experience info for visitors, including:
    - Photos
    - Reviews
    - Views count
    """
    experience = visitor_service.get_experience(experience_id)
    if not experience:
        return {"error": "Experience not found"}, 404

    # Increment view count
    visitor_service.increment_views(experience_id)

    return {
        "experience": experience
    }
