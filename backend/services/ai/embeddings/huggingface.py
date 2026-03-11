import requests
from config import Config
from .base import BaseEmbeddingProvider

class HfEmbeddingProvider(BaseEmbeddingProvider):
    
    def __init__(self):
        self.api_key = Config.HUGGINGFACE_API_KEY
        self.model = Config.HUGGINGFACE_MODEL
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"
    
    def embed(self, text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "inputs": text
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        return response.json()