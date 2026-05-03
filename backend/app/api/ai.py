from flask import Blueprint, request, g
from app.services.transform_ai_service import transform_advisor_service, story_service
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.ai_chat_service import chat_service
from app.services.farmer_service import farmer_service
from app.services.plan_service import plan_service
from app.auth.decorators import require_auth

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai/chat", methods=["POST"])
@require_auth
def ai_chat():
    """General AI assistant"""
    data = request.get_json() or {}
    
    user_message = data.get("message", "")
    language = data.get("language", "en")
    # Frontend sends conversation history as a list of {role, content} objects
    # This lets the AI remember what was said earlier in the session
    history = data.get("history", [])
    # Session ID from frontend - used for logging
    # Later: replace with real user ID from auth
    session_id = data.get("session_id", "anonymous")
    
    try:
        response = chat_service.chat(
            message=user_message,
            history=history,
            language=language,
            session_id=session_id,
            user_id=g.user_id,
            ai_type="assistant",
        )
        return {
            "response": response
        }
    except ValueError as e:
        # Guardrails rejection - return 400 with clear message
        return {"error": str(e)}, 400

@ai_bp.route("/farms/<farm_id>/ai", methods=["POST"])
@require_auth
def ai_interaction(farm_id):
    """
    Farm-level transformation advisory.
    Fetches full farm + farmer context before calling AI.
    """
    data = request.json or {}
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "en")
    
    # Fetch full farm record from DB for real context
    farm_record = farmer_service.get_farm_by_id(farm_id) or {}
    
    # Fetch farmer profile for goals/readiness context
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}
    
    # Build enriched farm_data combining both
    farm_data = {
        **farm_record,
        "budget_range": farmer_profile.get("budget_range", "low"),
        "family_helpers": farmer_profile.get("family_helpers", 0),
        "visitor_experience": farmer_profile.get("visitor_experience", "none"),
        "primary_goal": farmer_profile.get("primary_goal", "income"),
        "timeline": farmer_profile.get("timeline", "months"),
        "province": farmer_profile.get("province"),
    }
    
    transformation_service = TransformationService()
    experiences = experience_service.list_experiences(farm_id)
    
    # Pass full context to get_ai_summary
    ai_summary = transformation_service.get_ai_summary(experiences, farm_data)

    ai_response = transform_advisor_service.advise(
        user_prompt=user_prompt,
        transformation_summary=ai_summary,
        language=language
    )
    plan_service.increment_ai_counter(g.user_id, "farm")

    return {
        "farm_id": farm_id,
        "ai": ai_response
    }

@ai_bp.route("/farms/<farm_id>/experiences/<experience_id>/ai", methods=["POST"])
@require_auth
def ai_explain_experience(farm_id, experience_id):
    """
    Single experience advisory.
    Now passes farm context alongside experience details.
    """

    data = request.get_json() or {}
    language = data.get("language", "en")
    user_prompt = data.get("user_prompt", "")
    
    experience = experience_service.get_experience_by_id(experience_id)
    if not experience:
        return {"error": "Experience not found"}, 404
    
    # Fetch farm + farmer context for personalized advice
    farm_record = farmer_service.get_farm_by_id(farm_id) or {}
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}
    
    farm_context = {
        "farm_type": farm_record.get("farm_type"),
        "crops": farm_record.get("crops", []),
        "animals": farm_record.get("animals", {}),
        "province": farmer_profile.get("province"),
        "budget_range": farmer_profile.get("budget_range", "low"),
        "family_helpers": farmer_profile.get("family_helpers", 0),
        "visitor_experience": farmer_profile.get("visitor_experience", "none"),
    }

    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "level": experience["level"],
        "monetization": experience["monetization"],
        "enabled": experience["enabled"],
        "description": experience.get("description"),
        "setup_cost_range": experience.get("setup_cost_range"),
        "time_to_launch": experience.get("time_to_launch"),
        "estimated_revenue_pkr": experience.get("estimated_revenue_pkr"),
        "season": experience.get("season"),
    }
    
    ai_response = transform_advisor_service.advise_experience(
        user_prompt=user_prompt,
        experience_details=experience_details,
        farm_context=farm_context,
        language=language
    )
    plan_service.increment_ai_counter(g.user_id, "experience")
    
    return {
        "experience_id": experience_id,
        "ai": ai_response
    }
    
@ai_bp.route("/farms/<farm_id>/experiences/<experience_id>/story", methods=["POST"])
@require_auth
def generate_experience_story(farm_id, experience_id):
    """
    Visitor-facing story generation for a single experience.
    Now includes farm context for culturally authentic storytelling.
    """
    data = request.get_json() or {}
    language = data.get("language", "en")

    experience = experience_service.get_experience_by_id(experience_id)
    if not experience:
        return {"error": "Experience not found"}, 404
    
    # Fetch farm context for richer story
    farm_record = farmer_service.get_farm_by_id(farm_id) or {}
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}
    
    farm_context = {
        "farm_type": farm_record.get("farm_type"),
        "crops": farm_record.get("crops", []),
        "animals": farm_record.get("animals", {}),
        "province": farmer_profile.get("province"),
    }
    
    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "level": experience["level"],
        "monetization": experience["monetization"],
        "enabled": experience["enabled"],
        "description": experience.get("description"),
        "season": experience.get("season"),
    }

    ai_response = story_service.generate_story(
        experience_details=experience_details,
        farm_context=farm_context,
        language=language
    )
    plan_service.increment_ai_counter(g.user_id, "story")
    
    return {
        "experience_id": experience_id,
        "ai": ai_response
    }