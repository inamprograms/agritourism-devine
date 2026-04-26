# =============================================================================
# api/plans.py
# =============================================================================
# ENDPOINTS:
#   GET /plans/me → Returns current user's plan, usage counters, and limits
#
# Used by frontend to:
#   - Show current plan tier
#   - Display usage indicators (e.g. "3/10 AI chats used")
#   - Show/hide features based on plan (e.g. carbon credits)
#   - Prompt upgrade when limits are approaching
# =============================================================================

from flask import Blueprint, jsonify, g
from app.auth.decorators import require_auth
from app.services.plan_service import plan_service

plans_bp = Blueprint("plans", __name__)

@plans_bp.route("/plans/me", methods=["GET"])
@require_auth
def get_my_plan():
    """
    Returns the current user's plan and usage.
    Frontend calls this to show plan status and usage indicators.
    """
    plan = plan_service.get_plan(g.user_id)

    if not plan:
        return jsonify({"error": "Plan not found"}), 404

    # Calculate total AI usage across all types
    total_ai_used = (
        plan.get("ai_assistant_used", 0) +
        plan.get("ai_farm_used", 0) +
        plan.get("ai_experience_used", 0) +
        plan.get("ai_story_used", 0)
    )

    return jsonify({
        "plan": plan.get("plan", "free"),
        "carbon_credits_enabled": plan.get("carbon_credits_enabled", True),

        # AI usage — broken down + total
        "ai_usage": {
            "assistant":  plan.get("ai_assistant_used", 0),
            "farm":       plan.get("ai_farm_used", 0),
            "experience": plan.get("ai_experience_used", 0),
            "story":      plan.get("ai_story_used", 0),
            "total":      total_ai_used,
            "limit":      plan.get("ai_chats_limit", 999999),
        },

        # Transformation usage
        "transformations": {
            "used":  plan.get("transformations_used", 0),
            "limit": plan.get("transformations_limit", 999999),
        },

        # Plan period
        "reset_at":   plan.get("reset_at"),
        "created_at": plan.get("created_at"),
    }), 200