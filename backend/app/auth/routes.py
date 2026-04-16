# =============================================================================
# auth/routes.py
# =============================================================================
# ENDPOINTS:
#   POST /auth/signup   → Register new user, send confirmation email
#   POST /auth/confirm  → Confirm email via token_hash
#   POST /auth/signin   → Login with email + password
#   POST /auth/signout  → Logout, clear cookies
#   GET  /auth/me       → Get current user profile
#   POST /auth/refresh  → Refresh access token
#
# SIGNUP FLOW (Production):
#   1. sign_up() → trigger creates profile row (full_name, role='visitor')
#   2. update_user_by_id → sets correct role in app_metadata (JWT claims)
#   3. Returns "check your email" — user cannot sign in until confirmed
#
# SIGNIN FLOW:
#   1. sign_in_with_password → Supabase verifies credentials
#   2. Syncs profiles table role from app_metadata (idempotent)
#   3. Sets HttpOnly cookies with access + refresh tokens
#
# DATABASE TRIGGER:
#   - Fires on INSERT into auth.users
#   - Creates profile row with full_name from user_metadata, role='visitor'
#   - Role is then synced to correct value on first signin
# =============================================================================

import logging
from flask import Blueprint, request, jsonify, g, make_response
from app.utils.supabase_client import get_admin_supabase_client, get_supabase_client
from app.auth.decorators import require_auth
from app.middleware.auth_middleware import (
    _set_auth_cookies,
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE
)
from config import Config
from app.utils.validators import is_valid_email, is_strong_password

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# ---------------------------------------------------------------------------
# Environment flag
# Set FLASK_ENV=prod in .env for production flow (email confirmation)
# Development flow skips email confirmation for easier testing
# ---------------------------------------------------------------------------
IS_PRODUCTION = Config.IS_PRODUCTION

# =============================================================================
# POST /auth/signup
# =============================================================================
@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Register a new user.

    Production flow (FLASK_ENV=production):
        → sign_up() → trigger creates profile → confirmation email sent
        → update_user_by_id sets role in app_metadata
        → Returns "check your email" — user cannot signin until confirmed

    Development flow (FLASK_ENV=development):
        → admin.create_user() with email_confirm=True → no email sent
        → Auto signin → cookies set → user is immediately logged in

    Request body:
        {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "full_name": "Ahmed Khan",
            "role": "farmer"    // "farmer" | "visitor" | "buyer"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "visitor")

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if not is_strong_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters and include uppercase, lowercase, number, and special character"
        }), 400

    allowed_roles = {"farmer", "visitor", "buyer"}
    if role not in allowed_roles:
        return jsonify({
            "error": f"Invalid role. Must be one of: {', '.join(allowed_roles)}"
        }), 400

    try:
        admin_client = get_admin_supabase_client()
        anon_client = get_supabase_client()

        if IS_PRODUCTION:
            # -----------------------------------------------------------------
            # PRODUCTION FLOW
            # -----------------------------------------------------------------
            # Step 1: Create user via sign_up()
            # - Supabase sends confirmation email automatically
            # - DB trigger fires → creates profile row:
            #     id = user.id
            #     full_name = from user_metadata
            #     role = 'visitor' (trigger default)
            # -----------------------------------------------------------------
            auth_response = anon_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": role
                    }
                }
            })

            if not auth_response.user:
                return jsonify({"error": "Failed to create user"}), 500

            user = auth_response.user

            # -----------------------------------------------------------------
            # Step 2: Detect duplicate email
            # Supabase quirk: sign_up() with existing confirmed email does NOT
            # throw an error. Instead it returns the existing user with
            # identities=[] (empty list). A new user always has identities.
            
            # Supabase returns identities=[] for existing confirmed users on duplicate signup
            # This is the recommended detection method per Supabase docs
            # -----------------------------------------------------------------
            if not (user.identities or []):
                return jsonify({
                    "error": "An account with this email already exists"
                }), 409

            # -----------------------------------------------------------------
            # Step 3: Set correct role in app_metadata via admin
            # This sets the role in the JWT claims so Flask middleware
            # can read g.user_role on every request without a DB call.
            # The profiles table role stays 'visitor' until first signin.
            # -----------------------------------------------------------------
            admin_client.auth.admin.update_user_by_id(
                str(user.id),
                {"app_metadata": {"role": role}}
            )

            return jsonify({
                "message": "Account created. Please check your email to verify your account.",
                "email": user.email,
            }), 201

        else:
            # -----------------------------------------------------------------
            # DEVELOPMENT FLOW
            # -----------------------------------------------------------------
            # Uses admin.create_user() with email_confirm=True so the user
            # is immediately confirmed — no email sent, no waiting.
            # Useful for local development and testing.
            # -----------------------------------------------------------------
            auth_response = admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": {
                    "full_name": full_name,
                },
                "app_metadata": {
                    "role": role
                },
                "email_confirm": True
            })

            if not auth_response.user:
                return jsonify({"error": "Failed to create user"}), 500

            user = auth_response.user

            # Auto signin — user is confirmed so this works immediately
            session_response = admin_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not session_response.session:
                return jsonify({
                    "message": "Account created. Please sign in.",
                    "email": user.email,
                }), 201

            session = session_response.session

            # Sync profiles table role on first login
            admin_client.table("profiles").upsert(
                {"id": str(user.id), "full_name": full_name, "role": role},
                on_conflict="id"
            ).execute()

            response = make_response(jsonify({
                "message": "Account created successfully",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": full_name,
                    "role": role,
                }
            }), 201)

            _set_auth_cookies(response, session.access_token, session.refresh_token)
            return response

    except Exception as e:
        error_message = str(e)
        logger.error("Signup error", exc_info=True)

        if "already registered" in error_message.lower() or "already exists" in error_message.lower():
            return jsonify({"error": "An account with this email already exists"}), 409

        return jsonify({"error": "Registration failed. Please try again."}), 500


# =============================================================================
# POST /auth/confirm
# =============================================================================
@auth_bp.route("/confirm", methods=["POST"])
def confirm_email():
    """
    Handles email confirmation via token_hash (PKCE flow).

    This endpoint is called by the frontend in Phase 2 when Supabase
    redirects with ?token_hash=xxx&type=email in the URL.

    Currently Supabase is using implicit flow (tokens in URL hash #)
    so this endpoint is ready for Phase 2 when we switch to PKCE flow.

    Request body:
        {
            "token_hash": "xxx",
            "type": "email"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    token_hash = data.get("token_hash", "").strip()
    type_ = data.get("type", "email")
    if type_ != "email":
        return jsonify({"error": "Invalid confirmation type"}), 400

    if not token_hash:
        return jsonify({"error": "token_hash is required"}), 400

    try:
        anon_client = get_supabase_client()
        admin_client = get_admin_supabase_client()

        auth_response = anon_client.auth.verify_otp({
            "token_hash": token_hash,
            "type": type_
        })

        if not auth_response.session or not auth_response.user:
            return jsonify({"error": "Invalid or expired confirmation link"}), 400

        session = auth_response.session
        user = auth_response.user

        app_metadata = user.app_metadata or {}
        role = app_metadata.get("role", "visitor")
        full_name = (user.user_metadata or {}).get("full_name", "")

        # Sync profiles table with correct role after confirmation
        admin_client.table("profiles").upsert(
            {"id": str(user.id), "full_name": full_name, "role": role},
            on_conflict="id"
        ).execute()

        response = make_response(jsonify({
            "message": "Email confirmed. You are now signed in.",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": full_name,
                "role": role,
            }
        }), 200)

        _set_auth_cookies(response, session.access_token, session.refresh_token)
        return response

    except Exception as e:
        error_message = str(e).lower()
        logger.error(f"Email confirm error: {error_message}")

        if "expired" in error_message or "invalid" in error_message:
            return jsonify({
                "error": "Confirmation link is invalid or has expired. Please sign up again."
            }), 400

        return jsonify({"error": "Email confirmation failed. Please try again."}), 500


# =============================================================================
# POST /auth/signin
# =============================================================================
@auth_bp.route("/signin", methods=["POST"])
def signin():
    """
    Authenticate an existing user.

    After successful signin:
    - Syncs profiles table role from app_metadata (idempotent)
    - Sets HttpOnly cookies with access + refresh tokens

    Request body:
        {
            "email": "user@example.com",
            "password": "SecurePassword123!"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    try:
        anon_client = get_supabase_client()
        admin_client = get_admin_supabase_client()

        auth_response = anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.session or not auth_response.user:
            return jsonify({"error": "Invalid email or password"}), 401

        session = auth_response.session
        user = auth_response.user

        app_metadata = user.app_metadata or {}
        role = app_metadata.get("role", "visitor")
        full_name = (user.user_metadata or {}).get("full_name", "")

        # Sync profiles table role from app_metadata
        # This is idempotent — safe to run on every signin
        # Ensures profiles table always reflects the correct role
        # even if signup flow didn't complete the update
        admin_client.table("profiles").upsert(
            {"id": str(user.id), "full_name": full_name, "role": role},
            on_conflict="id"
        ).execute()

        response = make_response(jsonify({
            "message": "Signed in successfully",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": full_name,
                "role": role,
                "email_confirmed_at": str(user.email_confirmed_at) if user.email_confirmed_at else None,
            }
        }), 200)

        _set_auth_cookies(response, session.access_token, session.refresh_token)
        return response

    except Exception as e:
        error_message = str(e).lower()
        logger.error("Signin error", exc_info=True)

        if "not confirmed" in error_message:
            return jsonify({
                "error": "Please confirm your email before signing in. Check your inbox."
            }), 403

        if "invalid" in error_message or "credentials" in error_message:
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({"error": "Sign in failed. Please try again."}), 500


# =============================================================================
# POST /auth/signout
# =============================================================================
@auth_bp.route("/signout", methods=["POST"])
@require_auth
def signout():
    """
    Sign out the current user.
    Revokes session server-side and clears auth cookies from browser.
    """
    try:
        if getattr(g, "access_token", None):
            anon_client = get_supabase_client()
            anon_client.auth.sign_out()
    except Exception as e:
        # Even if server-side revocation fails, cookies are cleared below
        # User is effectively logged out on their device
        logger.error(f"Signout error: {str(e)}")

    response = make_response(jsonify({"message": "Signed out successfully"}), 200)
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/", samesite="None", secure=True)
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/", samesite="None", secure=True)
    return response


# =============================================================================
# GET /auth/me
# =============================================================================
@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    """
    Get the current authenticated user's full profile.

    Called by frontend on app load to:
    - Check if user is logged in
    - Get user role (determines what UI they see)
    - Get profile details (name, avatar, bio)

    Uses g.supabase (scoped to current user) so RLS applies —
    user can only read their own profile row.
    """
    try:
        supabase = g.supabase

        profile_response = supabase.table("profiles").select("*").eq(
            "id", g.user_id
        ).single().execute()

        profile = profile_response.data if profile_response.data else {}

        return jsonify({
            "user": {
                **g.user,
                "full_name": profile.get("full_name", ""),
                "avatar_url": profile.get("avatar_url", ""),
                "bio": profile.get("bio", ""),
                "created_at": profile.get("created_at", ""),
            }
        }), 200

    except Exception as e:
        logger.error("/me error", exc_info=True)
        # Fallback: return basic info from JWT if profiles query fails
        return jsonify({"user": g.user}), 200


# =============================================================================
# POST /auth/refresh
# =============================================================================
@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Manually refresh the access token using the refresh token cookie.

    Normally the middleware handles this automatically when it detects
    an expired access token. This endpoint exists for cases where the
    frontend wants to proactively refresh before expiry.
    """
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)

    if not refresh_token:
        return jsonify({"error": "No refresh token found"}), 401

    try:
        anon_client = get_supabase_client()
        session_response = anon_client.auth.refresh_session(refresh_token)

        if not session_response.session:
            return jsonify({"error": "Session refresh failed"}), 401

        session = session_response.session

        response = make_response(jsonify({"message": "Token refreshed"}), 200)
        if session.refresh_token:
            _set_auth_cookies(response, session.access_token, session.refresh_token)
        return response

    except Exception as e:
        logger.error("Token refresh error", exc_info=True)
        response = make_response(
            jsonify({"error": "Session expired. Please sign in again."}), 401
        )
        response.delete_cookie(ACCESS_TOKEN_COOKIE, samesite="None", secure=True)
        response.delete_cookie(REFRESH_TOKEN_COOKIE, samesite="None", secure=True)
        return response