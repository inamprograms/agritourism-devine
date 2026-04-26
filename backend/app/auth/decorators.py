# =============================================================================
# decorators.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   Without decorators, every protected route would need to repeat the same
#   auth-checking code. Decorators let us write it ONCE and apply it cleanly.
#
#   USAGE EXAMPLES:
#
#     @app.route("/farms")
#     @require_auth
#     def list_farms():
#         user = g.user  # ← guaranteed to exist here
#         ...
#
#     @app.route("/admin/users")
#     @require_auth
#     @require_role("admin")
#     def admin_users():
#         ...   # Only admins reach here
#
#     @app.route("/farms/create")
#     @require_auth
#     @require_role("farmer")
#     def create_farm():
#         ...   # Only farmers reach here
#
#     A Python decorator is just a function that wraps another function.
#        `functools.wraps` preserves the original function's name/docstring
#        so Flask's routing doesn't get confused.
# =============================================================================

import functools
from flask import g, jsonify


def require_auth(f):
    """
    Decorator that blocks unauthenticated requests.

    Checks if the auth middleware has successfully set g.user.
    If not, returns a 401 Unauthorized response immediately —
    the actual route function is never called.

    Stack order matters: put @require_auth BEFORE @require_role
    so we always check authentication before checking authorization.

    Example:
        @app.route("/profile")
        @require_auth
        def profile():
            return jsonify(g.user)
    """
    @functools.wraps(f)  # Preserves function name — important for Flask routing
    def decorated_function(*args, **kwargs):
        # g.user is set by auth_middleware.py in before_request
        # If it's not set, the user isn't logged in
        if not hasattr(g, "user") or g.user is None:
            return jsonify({
                "error": "Authentication required",
                "code": "UNAUTHENTICATED",
                "message": "You must be logged in to access this resource"
            }), 401

        # Auth passed — call the actual route function
        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    Decorator factory that restricts access to specific roles.

    Accepts one or more role strings. The user must have at least
    one of the specified roles to proceed.

    Args:
        *allowed_roles: One or more role strings.
                        e.g. require_role("admin")
                        e.g. require_role("farmer", "admin")  ← either role works

    Example:
        @app.route("/carbon-credits")
        @require_auth
        @require_role("buyer", "admin")
        def carbon_credits():
            ...

           The outer function `require_role` receives the role arguments.
           It returns the inner `decorator` function which does the actual wrapping.
           This is a "decorator factory" — a decorator that takes arguments.
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # At this point, @require_auth already ran, so g.user exists
            user_role = getattr(g, "user_role", None)

            if user_role is None:
                return jsonify({
                    "error": "Authorization failed",
                    "code": "NO_ROLE",
                    "message": "Your account has no role assigned. Contact support."
                }), 403

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Insufficient permissions",
                    "code": "FORBIDDEN",
                    "message": f"This action requires one of these roles: {', '.join(allowed_roles)}",
                    "your_role": user_role
                }), 403

            # Role check passed — call the actual route function
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_verified_email(f):
    """
  
    Decorator that blocks users who haven't verified their email.

    NOTE: In the current architecture, unconfirmed users cannot sign in at all
    (Supabase blocks signin with 403). This decorator is therefore redundant
    for standard routes but kept for future use cases where partial access
    may be granted before email confirmation.
    ---
    Useful for sensitive actions like posting a farm listing or
    completing a purchase. Email verification is a Supabase feature —
    users get an email with a confirmation link after signup.

    Example:
        @app.route("/farms/create")
        @require_auth
        @require_role("farmer")
        @require_verified_email
        def create_farm():
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(g, "user", None)

        if not user:
            return jsonify({
                "error": "Authentication required",
                "code": "UNAUTHENTICATED"
            }), 401

        # Supabase puts email_confirmed_at in the user object
        # If it's None/missing, the user hasn't clicked the confirmation link
        if not user.get("email_confirmed_at"):
            return jsonify({
                "error": "Email not verified",
                "code": "EMAIL_UNVERIFIED",
                "message": "Please verify your email address before continuing"
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def require_plan(feature: str):
    """
    Decorator factory that checks if user has access to a feature based on their plan.
    
    Currently passes everyone through since all limits are set to 999999.
    To enforce limits later — just set real numbers in user_plans table.
    No code changes needed.

    Usage:
        @app.route("/farms/transform")
        @require_auth
        @require_plan("transformation")
        def transform_farm():
            ...

        @app.route("/ai/chat")
        @require_auth
        @require_plan("ai")
        def ai_chat():
            ...

        @app.route("/carbon/estimate")
        @require_auth
        @require_plan("carbon_credits")
        def carbon_estimate():
            ...

    Supported features:
        "ai"             → checks total AI usage against ai_chats_limit
        "transformation" → checks transformations_used against transformations_limit
        "carbon_credits" → checks carbon_credits_enabled flag
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            from app.services.plan_service import plan_service

            plan = plan_service.get_plan(g.user_id)

            if not plan:
                # No plan row — fail open, let request through
                # signin should have created it, this is a safety net
                return f(*args, **kwargs)

            # --- Carbon credits: on/off flag ---
            if feature == "carbon_credits":
                if not plan.get("carbon_credits_enabled", True):
                    return jsonify({
                        "error": "Feature not available on your plan",
                        "code": "PLAN_LIMIT_REACHED",
                        "feature": "carbon_credits",
                        "upgrade_message": "Upgrade to Pro to access carbon credits"
                    }), 403

            # --- AI chats: total usage vs limit ---
            elif feature == "ai":
                total_used = (
                    plan.get("ai_assistant_used", 0) +
                    plan.get("ai_farm_used", 0) +
                    plan.get("ai_experience_used", 0) +
                    plan.get("ai_story_used", 0)
                )
                limit = plan.get("ai_chats_limit", 999999)
                if total_used >= limit:
                    return jsonify({
                        "error": "AI chat limit reached for this month",
                        "code": "PLAN_LIMIT_REACHED",
                        "feature": "ai",
                        "used": total_used,
                        "limit": limit,
                        "reset_at": plan.get("reset_at"),
                        "upgrade_message": "Upgrade to Pro for more AI chats"
                    }), 403

            # --- Transformations: usage vs limit ---
            elif feature == "transformation":
                used = plan.get("transformations_used", 0)
                limit = plan.get("transformations_limit", 999999)
                if used >= limit:
                    return jsonify({
                        "error": "Farm transformation limit reached for this month",
                        "code": "PLAN_LIMIT_REACHED",
                        "feature": "transformation",
                        "used": used,
                        "limit": limit,
                        "reset_at": plan.get("reset_at"),
                        "upgrade_message": "Upgrade to Pro for more transformations"
                    }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator