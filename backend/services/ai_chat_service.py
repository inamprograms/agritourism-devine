from services.ai.factory import get_ai_provider
from services.ai.prompts.system_prompts import ai_assistant_system_prompt
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

    def chat(self, message: str, history: list, language: str = "en") -> str:
        """
        Process a conversational message with history context.
        
        history format: [{"role": "user", "content": "..."}, 
                         {"role": "assistant", "content": "..."}]
        """
        system = ai_assistant_system_prompt(language)
        
        # Build the full conversation as context for the AI
        # We append the new message at the end
        conversation_context = self._build_conversation_context(history, message)
        
        response = self.provider.complete(
            system_prompt=system,
            user_prompt=conversation_context,
            temperature=self.temperature,
            max_tokens=1000,
        )
        
        return response.strip()

    def _build_conversation_context(self, history: list, new_message: str) -> str:
        """
        Format conversation history into a single prompt string.
        
        Why not pass history as separate messages?
        Our BaseAIProvider.complete() takes a single user_prompt string —
        this keeps the provider interface simple. We format history as 
        context text instead. This works well for single-turn providers
        and is easy to upgrade later if needed.
        """
        if not history:
            return new_message
        
        # Build readable conversation history
        lines = ["Previous conversation:"]
        for turn in history[-6:]:  # Last 6 turns max - keeps context window manageable
            role_label = "User" if turn["role"] == "user" else "Assistant"
            lines.append(f"{role_label}: {turn['content']}")
        
        lines.append(f"\nFarmer's new message: {new_message}")
        lines.append("\nContinue the conversation naturally, referring to previous context where relevant.")
        
        return "\n".join(lines)