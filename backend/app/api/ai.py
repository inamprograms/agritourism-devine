from flask import Blueprint, request, g, current_app
from app.services.transform_ai_service import transform_advisor_service, story_service, AIUnavailable
from app.services.transformation_service import TransformationService
from app.services.experience_service import experience_service
from app.services.ai_chat_service import chat_service, ChatRequest
from app.services.farmer_service import farmer_service
from app.services.plan_service import plan_service
from app.auth.decorators import require_auth
from app.services.farm_normalizer import normalize_farm
from app.services.post_builder import build_post_facts, assemble_post, fallback_post
from app.services.ai.languages import clean_language

ai_bp = Blueprint("ai", __name__)

def _or_not_provided(value):
    return "not provided" if value is None or value == "" else value

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
        response = chat_service.chat(ChatRequest(
            message=user_message,
            history=history,
            language=language,
            session_id=session_id,
            user_id=g.user_id,
            ai_type="assistant",
        ))
        return {
            "response": response
        }
    except ValueError as e:
        # Guardrails rejection - return 400 with clear message
        return {"error": str(e)}, 400


def _read_chat_input(data):
    """Question, language and recent chat messages from the request, cleaned and limited."""
    user_prompt = str(data.get("user_prompt") or "").strip()[:1000]
    language = clean_language(data.get("language"))
    raw = data.get("history") if isinstance(data.get("history"), list) else []
    history = [
        {
            "role": "assistant" if m.get("role") == "assistant" else "user",
            "content": str(m.get("content") or "")[:2000],
        }
        for m in raw[-6:]
        if isinstance(m, dict)
    ]
    return user_prompt, language, history


@ai_bp.route("/farms/<farm_id>/ai", methods=["POST"])
@require_auth
def ai_interaction(farm_id):
    """
    Farm-level advice about the farmer's own plan.
    Fetches full farm + farmer context before calling the AI.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return {"error": "Farm not found or access denied"}, 403

    user_prompt, language, history = _read_chat_input(request.get_json(silent=True) or {})
    if not user_prompt:
        return {"error": "Please type a question."}, 400

    farm_record = farmer_service.get_farm_by_id(farm_id) or {}
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}

    # None means "not answered". The prompt prints it as "not provided".
    farm_data = {
        **farm_record,
        "budget_range": farmer_profile.get("budget_range"),
        "family_helpers": farmer_profile.get("family_helpers"),
        "visitor_experience": farmer_profile.get("visitor_experience"),
        "primary_goal": farmer_profile.get("primary_goal"),
        "timeline": farmer_profile.get("timeline"),
        "province": farmer_profile.get("province"),
        "country": farmer_profile.get("country"),
    }
    farm_data, _ = normalize_farm(farm_data)

    experiences = experience_service.list_experiences(farm_id)
    ai_summary = TransformationService().get_ai_summary(experiences, farm_data)

    try:
        ai_response = transform_advisor_service.advise(
            user_prompt=user_prompt,
            transformation_summary=ai_summary,
            language=language,
            history=history,
        )
    except AIUnavailable:
        return {"error": AIUnavailable.user_message}, 503

    plan_service.increment_ai_counter(g.user_id, "farm")

    return {
        "farm_id": farm_id,
        "ai": ai_response
    }


@ai_bp.route("/farms/<farm_id>/experiences/<experience_id>/ai", methods=["POST"])
@require_auth
def ai_explain_experience(farm_id, experience_id):
    """
    Advice about one experience, using the farm facts and the plan's own steps and safety notes.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return {"error": "Farm not found or access denied"}, 403

    user_prompt, language, history = _read_chat_input(request.get_json(silent=True) or {})
    if not user_prompt:
        return {"error": "Please type a question."}, 400

    experience = experience_service.get_experience_by_id(experience_id)
    if not experience or experience["farm_id"] != farm_id:
        return {"error": "Experience not found"}, 404

    farm_record = farmer_service.get_farm_by_id(farm_id) or {}
    farm_record, _ = normalize_farm(farm_record)
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}

    farm_context = {
        "farm_type": farm_record.get("farm_type"),
        "crops": farm_record.get("crops") or [],
        "animals": farm_record.get("animals") or {},
        "province": farmer_profile.get("province"),
        "family_helpers": farmer_profile.get("family_helpers"),
        "visitor_experience": farmer_profile.get("visitor_experience"),
    }

    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "monetization": experience["monetization"],
        "description": experience.get("description"),
        "setup_cost_range": experience.get("setup_cost_range"),
        "time_to_launch": experience.get("time_to_launch"),
        "season": experience.get("season"),
        "price": experience.get("price"),
        "first_steps": experience.get("first_steps") or [],
        "safety_notes": experience.get("safety_notes") or [],
        "why_for_you": experience.get("why_for_you"),
    }

    try:
        ai_response = transform_advisor_service.advise_experience(
            user_prompt=user_prompt,
            experience_details=experience_details,
            farm_context=farm_context,
            language=language,
            history=history,
        )
    except AIUnavailable:
        return {"error": AIUnavailable.user_message}, 503

    plan_service.increment_ai_counter(g.user_id, "experience")

    return {
        "experience_id": experience_id,
        "ai": ai_response
    }


@ai_bp.route("/farms/<farm_id>/experiences/<experience_id>/story", methods=["POST"])
@require_auth
def generate_experience_story(farm_id, experience_id):
    """
    Short invitation message the farmer can send to visitors.
    The AI writes the friendly text; farm name, place, price and phone
    are added from the database (post_builder), never by the AI.
    If the AI fails, a plain template message is used instead.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return {"error": "Farm not found or access denied"}, 403

    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    language = clean_language(data.get("language"))

    experience = experience_service.get_experience_by_id(experience_id)
    if not experience or experience["farm_id"] != farm_id:
        return {"error": "Experience not found"}, 404

    farm_record = farmer_service.get_farm_by_id(farm_id) or {}
    farm_record, _ = normalize_farm(farm_record)
    farmer_profile = farmer_service.get_farmer_for_user(g.user_id) or {}
    phone = farmer_service.get_profile_phone(g.user_id)

    facts = build_post_facts(farm_record, farmer_profile, experience, phone)

    farm_context = {
        "farm_type": farm_record.get("farm_type"),
        "crops": farm_record.get("crops") or [],
        "animals": list((farm_record.get("animals") or {}).keys()),
    }

    experience_details = {
        "title": experience["title"],
        "type": experience["type"],
        "description": experience.get("description"),
        "season": experience.get("season"),
    }

    try:
        ai_response = story_service.generate_story(
            experience_details=experience_details,
            farm_context=farm_context,
            language=language
        )
    except Exception:
        current_app.logger.warning("Story AI failed for experience %s", experience_id, exc_info=True)
        ai_response = None

    post = assemble_post(ai_response, facts)
    if post is not None:
        post["source"] = "ai"
        plan_service.increment_ai_counter(g.user_id, "story")
    else:
        # AI down or unusable: send a plain template message so the farmer is never blocked
        post = assemble_post(fallback_post(experience["title"]), facts)
        post["source"] = "template"

    return {
        "experience_id": experience_id,
        "ai": post
    }