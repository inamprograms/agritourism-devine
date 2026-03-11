import requests
from config import Config
from .base import BaseEmbeddingProvider

class HfEmbeddingProvider(BaseEmbeddingProvider):
    
    def __init__(self):
        self.api_key = Config.HUGGINGFACE_API_KEY
        self.model = Config.HUGGINGFACE_MODEL
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model}/pipeline/feature-extraction"
        
    def embed(self, text: str) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "inputs": text
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.status_code != 200:  
            raise ValueError(f"HuggingFace API error {response.status_code}: {response.text}")
        embedding = response.json()
        return embedding