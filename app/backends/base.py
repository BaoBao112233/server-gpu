from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any
from app.models import ChatCompletionRequest, Message


class BaseBackend(ABC):
    """Abstract base class for LLM backends"""
    
    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """Generate a chat completion"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion"""
        pass
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings for texts"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if backend is healthy"""
        pass
