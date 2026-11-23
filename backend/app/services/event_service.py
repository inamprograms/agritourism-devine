"""
Event log: a small record of what farmers do, step by step.

Why: so we can see where farmers stop (profile, transform, enabling an experience,
setting a price, creating and sharing the message) and fix that part first.

Rules:
  - Logging must NEVER break the farmer's action. Any problem is swallowed and logged.
  - Only event names from the list below are stored.
  - Only small, plain details are stored (numbers, short codes). Never free text such as
    the farmer's questions, messages, names or phone numbers.
  - Browsers may only send the CLIENT_EVENT_TYPES. All other events are logged by the server,
    so a browser cannot invent them.
"""
import logging
from app.utils.supabase_client import get_admin_supabase_client

logger = logging.getLogger(__name__)

# Events logged by the server
SERVER_EVENT_TYPES = {
    "farm_created",
    "profile_step_completed",
    "transformed",
    "experience_enabled",
    "experience_disabled",
    "price_set",
    "story_generated",
    "ai_question_asked",
}

# Events only the browser can know about (copy button, share button)
CLIENT_EVENT_TYPES = {
    "story_copied",
    "share_clicked",
}

EVENT_TYPES = SERVER_EVENT_TYPES | CLIENT_EVENT_TYPES

MAX_DETAIL_KEYS = 10
MAX_TEXT_LENGTH = 60


def clean_details(details):
    """Keep only small plain values. Anything else is dropped."""
    if not isinstance(details, dict):
        return {}
    cleaned = {}
    for key, value in list(details.items())[:MAX_DETAIL_KEYS]:
        if not isinstance(key, str):
            continue
        if isinstance(value, bool) or value is None:
            cleaned[key[:40]] = value
        elif isinstance(value, (int, float)):
            cleaned[key[:40]] = value
        elif isinstance(value, str):
            cleaned[key[:40]] = value[:MAX_TEXT_LENGTH]
    return cleaned


def log_event(user_id, event_type, farm_id=None, experience_id=None, details=None):
    
    """
    Save one event. Returns True if saved, False if not.
    Never raises: a failed log must not stop the farmer.
    """
    try:
        if event_type not in EVENT_TYPES:
            logger.warning("event ignored, unknown type: %r", event_type)
            return False
        if not user_id:
            return False
        row = {
            "user_id": str(user_id),
            "farm_id": str(farm_id) if farm_id else None,
            "experience_id": str(experience_id) if experience_id else None,
            "event_type": event_type,
            "meta": clean_details(details),
        }
        get_admin_supabase_client().table("events").insert(row).execute()
        return True
    except Exception as exc:  # logging must never break the app
        logger.warning("event not saved (%s): %s", event_type, exc)
        return False