from flask import Blueprint, request, g
from app.services.transform_ai_service import transform_advisor_service, story_service
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.ai_chat_service import chat_service
from app.services.plan_service import plan_service
from app.auth.decorators import require_auth

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai/chat", methods=["POST"])
@require_auth
def ai_chat():
   
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
    data = request.json or {}

    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "en")

    farm_input = {
        "farm_id": farm_id,
        "notes": user_prompt
    }
    
    transformation_service = TransformationService()

    experiences = experience_service.list_experiences(farm_id)
    ai_summary = transformation_service.get_ai_summary(experiences)

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
    Endpoint to get AI explanation for a SINGLE experience.

    Flow:
    1. Fetch farm + farmer context from DB
    2. Fetch selected experience from DB
    3. Send data to AI as explanation layer
    4. Return AI response (no DB writes)
    """

    data = request.get_json() or {}
    language = data.get("language", "en")
    user_prompt = data.get("user_prompt", "")
    
    experience = experience_service.get_experience_by_id(experience_id)
    if not experience:
        return {"error": "Experience not found"}, 404

    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "level": experience["level"],
        "monetization": experience["monetization"],
        "enabled": experience["enabled"]
    }

    ai_response = transform_advisor_service.advise_experience(
        user_prompt=user_prompt,
        experience_details=experience_details,
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
    Endpoint to generate visitor-friendly story for a single experience.
    """
    data = request.get_json() or {}
    language = data.get("language", "en")

    experience = experience_service.get_experience_by_id(experience_id)
    if not experience:
        return {"error": "Experience not found"}, 404

    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "level": experience["level"],
        "monetization": experience["monetization"],
        "enabled": experience["enabled"]
    }

    ai_response = story_service.generate_story(
        experience_details=experience_details,
        language=language
    )
    plan_service.increment_ai_counter(g.user_id, "story")
    
    return {
        "experience_id": experience_id,
        "ai": ai_response
    }