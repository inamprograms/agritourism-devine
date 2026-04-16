# =============================================================================
# supabase_client.py
# =============================================================================
# WHY THIS FILE EXISTS:
#   Supabase's Python library is NOT thread-safe if you share one global client
#   across all users. Each request must get its own client instance, optionally
#   initialized with the requesting user's JWT token.
#
#   We expose two factory functions:
#     - get_supabase_client()       → Anonymous client (for public operations)
#     - get_admin_supabase_client() → Service role client (bypasses RLS, admin only)
#
# LEARN: Row Level Security (RLS) is a Postgres feature that restricts which rows
#        a user can see/edit based on their JWT. When you pass a user's access_token
#        to the Supabase client, RLS policies automatically filter data per that user.
# =============================================================================

import os
from config import Config
from supabase import create_client, Client
from flask import g  # g = "global" Flask context — lives for one request only


def get_supabase_client(access_token: str = None) -> Client:
    """
    Returns a Supabase client for normal (non-admin) operations.

    If an access_token (JWT) is passed, the client will make requests
    AS that user — meaning Supabase RLS policies will apply for that user.

    If no token is passed, the client uses the anon key — only public
    data (rows with RLS policy allowing anon access) will be visible.

    Args:
        access_token: The user's JWT access token (optional)

    Returns:
        Supabase Client instance
    """
    url = Config.SUPABASE_URL
    anon_key = Config.SUPABASE_ANON_KEY

    if not url or not anon_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
        )

    client: Client = create_client(url, anon_key)

    # If we have a user's JWT, tell the client to use it for all requests
    # This is what makes Row Level Security work correctly per-user
    if access_token:
        client.postgrest.auth(access_token)

    return client


def get_admin_supabase_client() -> Client:
    """
    Returns a Supabase client with SERVICE ROLE key.

    ⚠️  WARNING: This client BYPASSES all Row Level Security policies.
    Use ONLY for:
      - Admin operations (creating/deleting users from server side)
      - Background jobs that need full DB access
      - Seeding/migration scripts

    NEVER pass this client to a route handler that serves regular users.
    NEVER expose the service role key to the frontend.

    Returns:
        Supabase Client instance with elevated privileges
    """
    url = Config.SUPABASE_URL
    service_role_key = Config.SUPABASE_SERVICE_ROLE_KEY

    if not url or not service_role_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables"
        )

    return create_client(url, service_role_key)


def get_request_supabase() -> Client:
    """
    Returns the Supabase client for the current request.

    After auth middleware runs, it stores the client on Flask's `g` object
    (g is a request-scoped namespace — fresh for each request).

    This is a convenience function so route handlers don't need to
    manually create clients — they just call get_request_supabase().

    Usage in a route:
        from app.utils.supabase_client import get_request_supabase
        supabase = get_request_supabase()
        data = supabase.table("farms").select("*").execute()

    Returns:
        The Supabase client attached to the current request context
    """
    if not hasattr(g, "supabase"):
        # No authenticated user — return anon client
        g.supabase = get_supabase_client()
    return g.supabase