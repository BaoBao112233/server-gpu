import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Model Backend
    model_backend: str = "ollama"
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    # vLLM Configuration
    vllm_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    vllm_gpu_memory_utilization: float = 0.85
    vllm_max_model_len: int = 8192
    vllm_tensor_parallel_size: int = 1
    
    # llama.cpp Configuration
    llamacpp_model_path: str = "./models/llama-3.1-8b-instruct.Q4_K_M.gguf"
    llamacpp_n_ctx: int = 8192
    llamacpp_n_gpu_layers: int = 32
    
    # Voice Configuration
    whisper_model: str = "base"  # tiny, base, small, medium, large-v3
    tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    voice_device: str = "cuda"  # cuda or cpu
    voice_gpu_memory_fraction: float = 0.3  # 30% of GPU for voice models
    
    # API Configuration
    api_key: Optional[str] = None
    enable_api_key: bool = False
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

