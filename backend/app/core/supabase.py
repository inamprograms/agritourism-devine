# DEPRECATED: Use get_admin_supabase_client() from app.utils.supabase_client instead.
# This global client causes HTTP/2 connection issues under load.
# Kept temporarily for backward compatibility with existing routes.
# TODO: Migrate all imports to app.utils.supabase_client and delete this file.

from supabase import create_client
from config import Config

supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_ROLE_KEY
)
