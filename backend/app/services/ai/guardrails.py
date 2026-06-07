from app.services.ai.factory import get_ai_provider
from app.services.ai.prompts.system_prompts import guardrail_system_prompt
from app.services.ai.prompts.user_prompts import guardrail_check_prompt
import json


class GuardrailsService:
    MAX_MESSAGE_LENGTH = 2000

    def __init__(self):
        self.provider = get_ai_provider()

    def validate(self, message: str):
        """
        Validate message before it reaches the main AI model.
        
        Checks:
        1. Not empty
        2. Not too long
        3. LLM safety and topic classification
        
        Raises ValueError with user-friendly message if any check fails.
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message too long. Maximum {self.MAX_MESSAGE_LENGTH} characters allowed")

        self._llm_check(message)

    def _llm_check(self, message: str):
        """
        Use LLM to classify message safety and topic relevance.
        Fails silently if LLM check itself errors — never blocks user on judge failure.
        """
        try:
            raw = self.provider.complete(
                system_prompt=guardrail_system_prompt(),
                user_prompt=guardrail_check_prompt(message),
                temperature=0.0,
                max_tokens=150,
            )
            result = json.loads(raw)

            if not result.get("is_safe", True):
                raise ValueError("Message contains unsafe content")

            if not result.get("is_on_topic", True):
                raise ValueError(
                    "I'm specialized in agritourism and sustainable farming. "
                    "I'm not able to help with that topic, but I'd be happy to "
                    "answer any questions about starting farm experiences, carbon "
                    "credits, or regenerative farming. What would you like to know?"
                )

        except ValueError:
            raise
        except Exception:
            pass