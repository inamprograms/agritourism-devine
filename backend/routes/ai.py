from flask import Blueprint, request
from services.ai_service import AIFarmAdvisorService
from services.transformation_service import TransformationService

ai_bp = Blueprint("ai", __name__)
ai_service = AIFarmAdvisorService()

@ai_bp.route("/farms/<farm_id>/ai", methods=["POST"])
def ai_interaction(farm_id):
    data = request.json or {}

    farmer_notes = data.get("farmer_notes", "")
    language = data.get("language", "en")

    farm_input = {
        "farm_id": farm_id,
        "notes": farmer_notes
    }
    
    transformation_service = TransformationService()

    experiences = transformation_service.generate_experiences(farm_input)
    ai_summary = transformation_service.get_ai_summary(experiences)

    ai_response = ai_service.advise(
        farm_notes=farmer_notes,
        transformation_summary=ai_summary,
        language=language
    )

    return {
        "farm_id": farm_id,
        "experiences": experiences,
        "ai": ai_response
    }
