from config import Config
from .base import BaseEmbeddingProvider
from .bedrock import BrEmbeddingProvider
from .huggingface import HfEmbeddingProvider

def get_embedding_provider() -> BaseEmbeddingProvider:
    
    provider = Config.EMBEDDING_PROVIDER.lower()
    
    if provider == "huggingface":
        return HfEmbeddingProvider()
    elif provider == "bedrock":
        return BrEmbeddingProvider()
    else:
        raise ValueError(
            f"Unknown Embedding provider: '{provider}'. "
            f"Valid options: 'huggingface', 'bedrock'"
        )
        