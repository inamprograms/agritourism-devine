import boto3
import json
from config import Config
from .base import BaseEmbeddingProvider

class BrEmbeddingProvider(BaseEmbeddingProvider):
    
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )
        self.model = Config.BEDROCK_EMBEDDING_MODEL
    
    def embed(self, text: str) -> list[float]:
        
        body = {"inputText": text}
        
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        
        response = json.loads(response["body"].read())
        return response["embedding"]