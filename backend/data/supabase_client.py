from supabase import create_client
from config import Config

supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_ANON_KEY
)
