from abc import ABC, abstractmethod

class BaseEmbeddingProvider(ABC):
    
    @abstractmethod    
    def embed(self, text: str) -> list[float]:
        pass