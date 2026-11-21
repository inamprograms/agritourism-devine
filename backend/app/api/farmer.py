from flask import Blueprint, jsonify, g, request
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service
from app.services.event_service import log_event

farmer_bp = Blueprint("farmer", __name__)

# Allowed answers for the choice fields. None (empty) is always allowed:
# it means "not answered" and is how a farmer clears an answer.
CHOICES = {
    "budget_range": {"low", "medium", "high"},
    "visitor_experience": {"none", "some", "experienced"},
    "primary_goal": {"income", "education", "both"},
    "timeline": {"weeks", "months", "next_season"},
}
TEXT_FIELDS = {"province", "location", "country"}
ALLOWED_FIELDS = set(CHOICES) | TEXT_FIELDS | {"family_helpers"}
MAX_TEXT = 120


def _validate_profile(data):
    """Returns (clean_data, error_message). error_message is None when all is fine."""
    clean = {}
    for key, value in data.items():
        if key in CHOICES:
            if value is not None and value not in CHOICES[key]:
                return None, f"Invalid value for {key}"
            clean[key] = value
        elif key == "family_helpers":
            if value is None:
                clean[key] = None
                continue
            try:
                number = int(value)
            except (TypeError, ValueError):
                return None, "family_helpers must be a whole number"
            if not 0 <= number <= 50:
                return None, "family_helpers must be between 0 and 50"
            clean[key] = number
        elif key in TEXT_FIELDS:
            if value is None:
                clean[key] = None
            elif isinstance(value, str):
                clean[key] = value.strip()[:MAX_TEXT] or None
            else:
                return None, f"Invalid value for {key}"
    return clean, None


@farmer_bp.route("/farmers", methods=["GET"])
@require_auth
def get_farmer():
    farmer = farmer_service.get_farmer_for_user(g.user_id)
    return jsonify({"farmer": farmer}), 200


@farmer_bp.route("/farmer/profile", methods=["GET"])
@require_auth
def get_farmer_profile():
    """
    Get farmer profile for the authenticated user.
    A farmer who has not created a farm yet has no row, so return an empty
    profile (all answers unanswered) instead of a 404.
    """
    farmer = farmer_service.get_farmer_for_user(g.user_id)
    return jsonify({"farmer": farmer or {}}), 200


@farmer_bp.route("/farmer/profile", methods=["PATCH"])
@require_auth
def update_farmer_profile():
    """
    Update farmer profile details. Creates the farmer record on first save,
    so a new farmer can answer the questions before creating a farm.
    """
    data = request.get_json() or {}
    candidate = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}

    if not candidate:
        return jsonify({"error": "No valid fields to update"}), 400

    update_data, error = _validate_profile(candidate)
    if error:
        return jsonify({"error": error}), 400

    updated = farmer_service.update_farmer_profile(g.user_id, update_data)
    if not updated:
        return jsonify({"error": "Update failed"}), 500

    # True = answered, False = cleared. Only the field names are logged, never the answers.
    answered = {key: value is not None for key, value in update_data.items()}
    if any(answered.values()):
        log_event(g.user_id, "profile_step_completed", details=answered)

    return jsonify({"farmer": updated}), 200