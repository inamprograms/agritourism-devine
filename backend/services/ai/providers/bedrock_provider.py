import json
import boto3
from config import Config
from .base import BaseAIProvider


class BedrockProvider(BaseAIProvider):
    """
    Amazon Bedrock provider implementation.
    Supports Amazon Nova and other Bedrock-hosted models.
    
    Bedrock is different from Groq — it uses AWS SDK (boto3)
    and has a different message format. The base class contract
    ensures this difference is hidden from the rest of the system.
    """

    def __init__(self):
        # boto3 is the AWS SDK for Python
        # It reads AWS credentials from config or environment
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )
        self.model = Config.BEDROCK_MODEL

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 1500
    ) -> str:
        # Bedrock uses a different message format than OpenAI-compatible APIs
        # System prompt goes in a separate "system" field
        # User message goes in the "messages" array
        body = {
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "system": [
                {"text": system_prompt}
            ],
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens,
            }
        }

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        
        # Nova returns content in this structure
        return response_body["output"]["message"]["content"][0]["text"]