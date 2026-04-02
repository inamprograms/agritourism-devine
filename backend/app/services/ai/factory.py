from config import Config
from .providers.groq_provider import GroqProvider
from .providers.bedrock_provider import BedrockProvider
from .providers.base import BaseAIProvider


def get_ai_provider() -> BaseAIProvider:
    """
    Factory function — reads AI_PROVIDER from config and returns
    the correct provider instance.
    
    Factory Pattern: instead of creating objects directly, you call
    a factory that decides which object to create based on config.
    
    To add a new provider (e.g. OpenAI):
    1. Create openai_provider.py implementing BaseAIProvider
    2. Add elif clause here
    3. Add config values in config.py
    That's it — nothing else in the system needs to change.
    """
    provider = Config.AI_PROVIDER.lower()

    if provider == "groq":
        return GroqProvider()
    
    elif provider == "bedrock":
        return BedrockProvider()
    
    else:
        raise ValueError(
            f"Unknown AI provider: '{provider}'. "
            f"Valid options: 'groq', 'bedrock'"
        )