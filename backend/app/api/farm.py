import uuid
from flask import Blueprint, jsonify, request, g
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service
from app.services.event_service import log_event, CLIENT_EVENT_TYPES

farm_bp = Blueprint("farm", __name__)


def _clean_distance(value):
    """Returns (km_or_None, error). Keeps 0 (a farm right at the city edge) as 0."""
    if value is None or value == "":
        return None, None
    try:
        km = int(value)
    except (TypeError, ValueError):
        return None, "distance_from_city_km must be a whole number"
    if km < 0 or km > 5000:
        return None, "distance_from_city_km is out of range"
    return km, None


@farm_bp.route("/farms", methods=["GET"])
@require_auth
def list_farms():
    """Returns all farms for the logged-in user."""
    farms = farmer_service.get_farms_for_user(g.user_id)
    return jsonify({"farms": farms}), 200


@farm_bp.route("/farms", methods=["POST"])
@require_auth
def create_farm():
    """
    Explicitly create a new farm.
    Only the name is required. farm_type defaults to "Mixed".
    """
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    farm_type = (data.get("farm_type") or "").strip() or "Mixed"
    size_category = (data.get("size_category") or "medium").strip()
    location = (data.get("location") or "").strip() or None
    description = (data.get("description") or "").strip() or None
    crops = data.get("crops") or []
    animals = data.get("animals") or {}
    existing_trees = data.get("existing_trees") or []
    water_source = data.get("water_source") or None
    structures = data.get("structures") or []
    road_access = data.get("road_access") or None
    scenic_features = data.get("scenic_features") or []

    distance_from_city_km, distance_error = _clean_distance(data.get("distance_from_city_km"))

    if not name:
        return jsonify({"error": "Farm name is required"}), 400
    if distance_error:
        return jsonify({"error": distance_error}), 400

    farm = farmer_service.create_farm(
        user_id=g.user_id,
        name=name,
        farm_type=farm_type,
        size_category=size_category,
        location=location,
        description=description,
        crops=crops,
        animals=animals,
        existing_trees=existing_trees,
        water_source=water_source,
        structures=structures,
        road_access=road_access,
        distance_from_city_km=distance_from_city_km,
        scenic_features=scenic_features,
    )

    log_event(g.user_id, "farm_created", farm_id=farm.get("id") if isinstance(farm, dict) else None,
              details={
                  "farm_type": farm_type,
                  "crops": len(crops) if isinstance(crops, list) else 0,
                  "animal_kinds": len(animals) if isinstance(animals, dict) else 0,
                  "has_location": location is not None,
              })
    
    return jsonify({"farm": farm}), 201


@farm_bp.route("/farms/<farm_id>", methods=["GET"])
@require_auth
def get_farm(farm_id):
    """Get a single farm by id."""
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    farm = farmer_service.get_farm_by_id(farm_id)
    if not farm:
        return jsonify({"error": "Farm not found"}), 404
    return jsonify({"farm": farm}), 200


@farm_bp.route("/farms/<farm_id>", methods=["PATCH"])
@require_auth
def update_farm(farm_id):
    """
    Update farm details.
    Only fields provided in body will be updated.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    data = request.get_json() or {}

    allowed_fields = {
        "name", "farm_type", "size_category", "location", "description",
        "crops", "animals", "existing_trees", "water_source", "structures",
        "road_access", "distance_from_city_km", "scenic_features"
    }

    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "No valid fields to update"}), 400

    if "distance_from_city_km" in update_data:
        km, distance_error = _clean_distance(update_data["distance_from_city_km"])
        if distance_error:
            return jsonify({"error": distance_error}), 400
        update_data["distance_from_city_km"] = km

    updated_farm = farmer_service.update_farm(farm_id, update_data)
    if not updated_farm:
        return jsonify({"error": "Update failed"}), 500

    return jsonify({"farm": updated_farm}), 200


# --- Browser-only events: the copy button and the share button ---
CHANNELS = {"whatsapp", "sms", "facebook", "copy"}


@farm_bp.route("/farms/<farm_id>/events", methods=["POST"])
@require_auth
def client_event(farm_id):
    """
    Saves an event only the browser can know about (story copied, share clicked).
    Only the short fixed list in event_service.CLIENT_EVENT_TYPES is accepted.
    """
    if not farmer_service.verify_farm_ownership(farm_id, g.user_id):
        return jsonify({"error": "Farm not found or access denied"}), 403

    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}

    event = data.get("event")
    if not isinstance(event, str) or event not in CLIENT_EVENT_TYPES:
        return jsonify({"error": "Unknown event"}), 400

    experience_id = data.get("experience_id")
    try:
        experience_id = str(uuid.UUID(str(experience_id))) if experience_id else None
    except ValueError:
        experience_id = None

    channel = data.get("channel")
    details = {}
    if isinstance(channel, str) and channel in CHANNELS:
        details["channel"] = channel

    log_event(g.user_id, event, farm_id=farm_id, experience_id=experience_id, details=details)
    return jsonify({"ok": True}), 200