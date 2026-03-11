import time
from services.ai.factory import get_ai_provider
from services.ai.prompts.system_prompts import ai_assistant_system_prompt
from services.ai.guardrails import GuardrailsService
from services.ai.interaction_logger import InteractionLogger
from config import Config


class AIChatService:
    """
    Layer 1 AI Assistant Service.
    
    This is NOT the transform advisor — this is the platform-wide
    conversational assistant that lives on the AI Assistant page.
    
    Key difference from AIFarmAdvisorService:
    - Supports multi-turn conversation history
    - Returns plain text (not structured JSON) — it's chat
    - Has a broader scope: platform features, agritourism concepts,
      carbon credits, getting started guidance
    - Designed for farmers, investors, and partners
    """

    def __init__(self):
        self.provider = get_ai_provider()
        self.temperature = Config.AI_TEMPERATURE
        self.guardrails = GuardrailsService()
        self.logger = InteractionLogger()
        
    def chat(self, message: str, history: list, language: str = "en", session_id: str = "anonymous") -> str:
        """
        Process a conversational message with history context.
        
        history format: [{"role": "user", "content": "..."}, 
                         {"role": "assistant", "content": "..."}]
        """
        # 1. Guardrails check — before anything reaches the model
        self.guardrails.validate(message)
        
        # 2. Build structured messages list
        messages = self._build_messages(history, message, language)
        
        # 3. Call model and measure latency
        start = time.time()
        response = self.provider.chat(
            messages=messages,
            temperature=self.temperature,
            max_tokens=1000,
        )
        latency_ms = int((time.time() - start) * 1000)
        
        # 4. Validate response exists
        if not response or not response.strip():
            raise ValueError("Model returned empty response")
        
        result = response.strip()
        
        # 5. Log interaction
        self.logger.log(
            session_id=session_id,
            user_message=message,
            model_response=result,
            language=language,
            latency_ms=latency_ms,
        )
        
        return result
    
    def _build_messages(self, history: list, new_message: str, language: str) -> list:
        """
        Build structured messages list for AI provider.
        
        This is the industry standard format.
        
        Layer 2 RAG injection point:
        After history, before new_message — insert retrieved documents as:
        {"role": "system", "content": "Relevant context: {retrieved_docs}"}
        """
        messages = []

        # System prompt 
        messages.append({
            "role": "system",
            "content": ai_assistant_system_prompt(language)
        })

        # Conversation history — last 6 turns max
        for turn in history[-6:]:
            messages.append({
                "role": turn["role"],
                "content": turn["content"]
            })

        # RAG injection point - Layer 2 will add here
        # messages.append({"role": "system", "content": f"Relevant context:\n{retrieved_docs}"})

        # Current user message — always last
        messages.append({
            "role": "user",
            "content": new_message
        })

        return messages
    
chat_service = AIChatService()