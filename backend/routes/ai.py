from flask import Blueprint, request
from services.ai_service import AIFarmAdvisorService
from services.transformation_service import TransformationService
from services.experience_service import experience_service

ai_bp = Blueprint("ai", __name__)
ai_service = AIFarmAdvisorService()

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

    experiences = transformation_service.generate_experiences(farm_input)
    ai_summary = transformation_service.get_ai_summary(experiences)

    ai_response = ai_service.advise(
        user_prompt=user_prompt,
        transformation_summary=ai_summary,
        language=language
    )

    return {
        "farm_id": farm_id,
        "experiences": experiences,
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

    # 2. Fetch experience from DB  experience_id
    experience = experience_service.get_experience_by_id(experience_id)
    
    # 3. Prepare clean experience summary for AI
    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "level": experience["level"],
        "monetization": experience["monetization"],
        "enabled": experience["enabled"]
    }

    # 4. Call AI
    ai_service = AIFarmAdvisorService()
    ai_response = ai_service.advise_experience(
        user_prompt=user_prompt,
        experience_details=experience_details,
        language=language
    )

    return {
        "experience_id": experience_id,
        "ai": ai_response
    }
