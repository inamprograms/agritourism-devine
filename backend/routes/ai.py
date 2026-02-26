from flask import Blueprint, request
from services.transform_ai_service import transform_advisor_service, story_service
from services.transformation_service import TransformationService
from services.experience_service import experience_service

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai/chat", methods=["POST"])
def ai_chat():
   
    data = request.get_json() or {}
    
    user_message = data.get("message", "")
    language = data.get("language", "en")
    # Frontend sends conversation history as a list of {role, content} objects
    # This lets the AI remember what was said earlier in the session
    history = data.get("history", [])
    
    if not user_message:
        return {"error": "message is required"}, 400
    
    from services.ai_chat_service import AIChatService
    chat_service = AIChatService()
    
    response = chat_service.chat(
        message=user_message,
        history=history,
        language=language
    )
    return {
        "response": response
    }

@ai_bp.route("/farms/<farm_id>/ai", methods=["POST"])
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

    return {
        "farm_id": farm_id,
        "ai": ai_response
    }

@ai_bp.route("/farms/<int:farm_id>/experiences/<int:experience_id>/ai", methods=["POST"])
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

    return {
        "experience_id": experience_id,
        "ai": ai_response
    }
    
@ai_bp.route("/farms/<int:farm_id>/experiences/<int:experience_id>/story", methods=["POST"])
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
    return {
        "experience_id": experience_id,
        "ai": ai_response
    }