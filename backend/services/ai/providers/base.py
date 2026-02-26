from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers.
    
    Every provider (Groq, Bedrock, OpenAI, etc.) must implement
    these methods. This guarantees the rest of the system works
    identically regardless of which provider is active.
    
    This is called the "Strategy Pattern" — you swap the strategy
    (provider) without changing the code that uses it.
    """

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 1500
    ) -> str:
        """
        Send a prompt to the AI and return the text response.
        
        Args:
            system_prompt: Instructions that define AI behavior/role
            user_prompt: The actual user message or task
            temperature: Creativity vs focus (0.0 - 1.0)
            max_tokens: Maximum length of response
            
        Returns:
            str: The AI's text response
        """
        pass