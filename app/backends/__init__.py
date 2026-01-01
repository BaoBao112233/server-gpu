from app.backends.base import BaseBackend
from app.backends.ollama import OllamaBackend
from app.config import get_settings


def get_backend() -> BaseBackend:
    """Factory function to get the appropriate backend"""
    settings = get_settings()
    
    if settings.model_backend == "ollama":
        return OllamaBackend(
            base_url=settings.ollama_host,
            default_model=settings.ollama_model
        )
    elif settings.model_backend == "vllm":
        # TODO: Implement vLLM backend
        raise NotImplementedError("vLLM backend not yet implemented")
    elif settings.model_backend in ["llamacpp", "llama-cpp"]:
        from app.backends.llamacpp import LlamaCppBackend
        return LlamaCppBackend()
    else:
        raise ValueError(f"Unknown backend: {settings.model_backend}")
