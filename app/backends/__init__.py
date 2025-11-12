from app.backends.base import BaseBackend
from app.backends.ollama import OllamaBackend
from app.backends.vllm import VLLMBackend
from app.backends.voice import VoiceBackend
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
        return VLLMBackend(
            model_name=settings.vllm_model,
            gpu_memory_utilization=settings.vllm_gpu_memory_utilization,
            max_model_len=settings.vllm_max_model_len,
            tensor_parallel_size=settings.vllm_tensor_parallel_size
        )
    elif settings.model_backend == "llamacpp":
        # TODO: Implement llama.cpp backend
        raise NotImplementedError("llama.cpp backend not yet implemented")
    else:
        raise ValueError(f"Unknown backend: {settings.model_backend}")


def get_voice_backend() -> VoiceBackend:
    """Factory function to get the voice backend"""
    settings = get_settings()
    
    return VoiceBackend(
        whisper_model=settings.whisper_model,
        tts_model=settings.tts_model,
        device=settings.voice_device,
        gpu_memory_fraction=settings.voice_gpu_memory_fraction
    )

