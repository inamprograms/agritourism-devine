import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", 5000))

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # AI config
    AI_ENABLED = True
    AI_PROVIDER = "groq"
    AI_MODEL = "llama-3.1-8b-instant"
    AI_API_KEY = os.getenv("GROQ_API_KEY")