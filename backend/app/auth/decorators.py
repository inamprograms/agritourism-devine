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