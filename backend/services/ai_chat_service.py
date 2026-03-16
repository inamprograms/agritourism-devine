import time
from services.ai.factory import get_ai_provider
from services.ai.prompts.system_prompts import ai_assistant_system_prompt
from services.ai.guardrails import GuardrailsService
from services.ai.interaction_logger import InteractionLogger
from services.ai.retriever import ContextRetriever
from config import Config


class AIChatService:
    """
    AI Assistant Service.

    A platform-wide conversational AI assistant with multi-turn context and
    retrieval-augmented generation (RAG) support. 

    Key features:
    - Multi-turn conversation history support (last N turns)
    - RAG-enabled: injects relevant context from the knowledge base
    - Returns plain text responses for general chat
    - Covers platform features, agritourism concepts, carbon credits, and guidance
    - Logs interactions and enforces guardrails for safety and consistency
    """

    def __init__(self):
        self.provider = get_ai_provider()
        self.temperature = Config.AI_TEMPERATURE
        self.guardrails = GuardrailsService()
        self.logger = InteractionLogger()
        self.retriever = ContextRetriever()
        
    def chat(self, message: str, history: list, language: str = "en", session_id: str = "anonymous", source: str = "web") -> str:
        """
        Process a user message through the AI assistant with RAG context and multi-turn history.

        Steps performed:
        1. Validate input using guardrails.
        2. Retrieve relevant context from knowledge base (RAG).
        3. Build structured messages including:
        - System prompt
        - RAG context (if any)
        - Last N turns of conversation history
        - Current user message
        4. Call AI model with structured messages.
        5. Measure latency and log interaction details.
        6. Return model-generated response as plain text.

        Args:
            message (str): The user's current message.
            history (list[dict]): Conversation history, each dict with keys 'role' and 'content'.
            language (str, optional): Language of the conversation. Defaults to "en".
            session_id (str, optional): Identifier for logging and session tracking. Defaults to "anonymous".

        Returns:
            str: AI-generated response to the user message.

        Raises:
            ValueError: If the model returns an empty response.
            Exception: If guardrails or AI provider fail.
        """
        # 1. Guardrails check — before anything reaches the model
        self.guardrails.validate(message)
        
        # 2. Build structured messages list
        messages, rag_hit, retrieved_context = self._build_messages(history, message, language)
        
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
            ai_response=result,
            language=language,
            latency_ms=latency_ms,
            source=source,
            rag_hit=rag_hit,
            response_length=len(result.split()),
            retrieved_context=retrieved_context,
        )
        
        return result
    
    def _build_messages(self, history: list, new_message: str, language: str) -> tuple[list, bool, str | None]:
        """
        Build structured messages list for AI provider.
        """
        messages = []

        # System prompt 
        messages.append({
            "role": "system",
            "content": ai_assistant_system_prompt(language)
        })
        
        # RAG retrieval point 
        retrieved_context = self.retriever.retrieve(new_message)
        rag_hit = bool(retrieved_context)
        context = "\n\n".join(retrieved_context) if retrieved_context else None
        
        # RAG injection point 
        if retrieved_context:
            messages.append({
                "role": "system",
                "content": f"Relevant context from knowledge base:\n\n{context}"
            })

        # Conversation history - last 6 turns max
        for turn in history[-6:]:
            messages.append({
                "role": turn["role"],
                "content": turn["content"]
            })

        # Current user message
        messages.append({
            "role": "user",
            "content": new_message
        })

        return messages, rag_hit, context if rag_hit else None
    
chat_service = AIChatService()