# =============================================================================
# auth_middleware.py
# =============================================================================
# Runs before EVERY request. Reads the JWT from the HttpOnly cookie,
# verifies it, and attaches user info to Flask's g object.
#
# KEY BEHAVIORS:
#   1. Valid JWT in cookie → g.user, g.user_id, g.user_role are set
#   2. JWT expired + refresh token exists → auto-refresh, set new cookies
#   3. No token → g.user = None (public routes still work)
#   4. Invalid token → g.user = None + clear bad cookies
#
# JWT VERIFICATION:
#   Supabase projects created after May 2025 use asymmetric ES256 keys.
#   We verify using Supabase's JWKS endpoint which supports both ES256 and HS256.
#   This is faster than calling get_user() on every request because JWKS
#   responses are cached — no network call needed after the first request.
# =============================================================================

import os
import logging
from config import Config
import jwt
from jwt import PyJWKClient
from flask import g, request, make_response
from app.utils.supabase_client import get_supabase_client, get_admin_supabase_client

# Cookie names — centralized here so we never typo them
ACCESS_TOKEN_COOKIE = "sb_access_token"
REFRESH_TOKEN_COOKIE = "sb_refresh_token"

# JWKS client — cached at module level so it's only created once per server start
# PyJWKClient caches the public keys from Supabase's JWKS endpoint
# This means after the first request, JWT verification requires no network call
_jwks_client = None

logger = logging.getLogger(__name__)

def _get_jwks_client() -> PyJWKClient:
    """
    Returns a cached JWKS client for JWT verification.

    LEARN: JWKS (JSON Web Key Set) is a standard way to publish public keys.
           Supabase exposes their public key at /auth/v1/.well-known/jwks.json
           We use this to verify ES256 tokens without needing the private secret.
           HS256 (legacy) tokens still work — PyJWT handles both automatically.
    """
    global _jwks_client
    if _jwks_client is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        if not supabase_url:
            raise RuntimeError("SUPABASE_URL not set in environment")
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        # cache_keys=True → keys are cached, lifespan=3600 → refresh every hour
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
    return _jwks_client


def _decode_jwt(token: str) -> dict:
    """
    Decodes and verifies a Supabase JWT.

    Supports both:
    - ES256 (asymmetric) — new Supabase projects (May 2025+)
    - HS256 (symmetric)  — legacy Supabase projects

    Tries JWKS first (works for both). Falls back to legacy JWT secret
    if JWKS fails, for compatibility.
    """
    # Try JWKS verification first (works for ES256 and RS256)
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256", "HS256"],
            issuer=Config.SUPABASE_URL + "/auth/v1",
            options={"verify_aud": False}
        )
    except Exception as e:
        logger.error("JWT decode error", exc_info=True)
        
    # WARNING: fallback to HS256 only for legacy support
    # Fallback: legacy HS256 with JWT secret
    # This handles projects still using the symmetric secret
    jwt_secret = os.environ.get("SUPABASE_JWT_SECRET")
    if jwt_secret:
        return jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )

    raise jwt.InvalidTokenError("Could not verify JWT with JWKS or JWT secret")


def load_user_from_request():
    """
    Flask before_request hook.
    Reads the access token JWT from the cookie, verifies it,
    and populates g.user for the duration of this request.
    """
    # Default: no user
    g.user = None
    g.user_id = None
    g.user_role = None
    g.access_token = None
    g.refresh_token = None
    g.supabase = None

    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)

    if not access_token:
        return

    try:
        payload = _decode_jwt(access_token)

        user_id = payload.get("sub")
        if not user_id:
            return

        g.user_id = user_id
        g.access_token = access_token
        g.refresh_token = refresh_token

        app_metadata = payload.get("app_metadata", {})
        g.user_role = app_metadata.get("role", "visitor")

        g.user = {
            "id": user_id,
            "email": payload.get("email"),
            "role": g.user_role,
            "email_confirmed_at": payload.get("email_confirmed_at"),
        }

        # Create a Supabase client scoped to this user (RLS applies)
        g.supabase = get_supabase_client(access_token=access_token)

    except jwt.ExpiredSignatureError:
        # Token expired — try silent refresh
        if refresh_token:
            _try_refresh_session(refresh_token)

    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token error: {str(e)}")
        g._clear_auth_cookies = True

    except Exception as e:
        # Unexpected error — fail safe, treat as unauthenticated
        logger.error(f"Loading user from request error: {str(e)}")


def _try_refresh_session(refresh_token: str):
    """
    Attempts to refresh the user's session using their refresh token.
    If successful, updates g.user and signals after_request to update cookies.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.refresh_session(refresh_token)
        # supabase = get_admin_supabase_client()
        # response = supabase.auth.refresh_session(refresh_token)

        if response.session:
            session = response.session
            new_access_token = session.access_token
            new_refresh_token = session.refresh_token

            payload = _decode_jwt(new_access_token)

            user_id = payload.get("sub")
            app_metadata = payload.get("app_metadata", {})

            g.user_id = user_id
            g.user_role = app_metadata.get("role", "visitor")
            g.access_token = new_access_token
            g.refresh_token = new_refresh_token
            g.user = {
                "id": user_id,
                "email": payload.get("email"),
                "role": g.user_role,
                "email_confirmed_at": payload.get("email_confirmed_at"),
            }
            g.supabase = get_supabase_client(access_token=new_access_token)

            # Signal after_request to update cookies with new tokens
            g._new_tokens = {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            }

    except Exception as e:
        logger.error(f"Refresh session error: {str(e)}")
        g._clear_auth_cookies = True


def update_auth_cookies(response):
    """
    Flask after_request hook.
    Updates or clears auth cookies based on what happened during the request.
    """
    if hasattr(g, "_new_tokens"):
        tokens = g._new_tokens
        _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])

    elif hasattr(g, "_clear_auth_cookies") and g._clear_auth_cookies:
        response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
        response.delete_cookie(REFRESH_TOKEN_COOKIE, path="/")

    return response


def _set_auth_cookies(response, access_token: str, refresh_token: str):
    """
    Sets the auth tokens as secure HttpOnly cookies on the response.

    - httponly=True  → JavaScript cannot read this cookie (XSS protection)
    - secure=True    → Cookie only sent over HTTPS (production only)
    - samesite="Lax" → Protects against CSRF attacks
    """
    
    IS_PRODUCTION = Config.IS_PRODUCTION
 
    response.set_cookie(
        ACCESS_TOKEN_COOKIE,
        access_token,
        max_age=3600,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="Lax" if not IS_PRODUCTION else "None"
    )

    response.set_cookie(
        REFRESH_TOKEN_COOKIE,
        refresh_token,
        max_age=30 * 24 * 3600,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="Lax" if not IS_PRODUCTION else "None"
    )