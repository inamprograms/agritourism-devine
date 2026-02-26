import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", 5000))

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # AI Configuration
    # To switch providers: change AI_PROVIDER value only
    # Options: "groq" | "bedrock"
    AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")

    # Groq settings (active when AI_PROVIDER = "groq")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # Amazon Bedrock settings (active when AI_PROVIDER = "bedrock")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "amazon.nova-lite-v1:0")

    # Temperature controls how creative vs focused the AI is
    # 0.0 = very focused/deterministic, 1.0 = more creative
    # For farm advisory: 0.4 is a good balance
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.4"))