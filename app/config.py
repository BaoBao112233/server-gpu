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
    model_backend: str = "llama-cpp"
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"
    
    # vLLM Configuration
    vllm_model: str = "microsoft/Phi-3-mini-4k-instruct"
    vllm_gpu_memory_utilization: float = 0.9
    vllm_max_model_len: int = 4096
    vllm_tensor_parallel_size: int = 1
    
    # llama.cpp Configuration (Mini Orca optimized for Orange Pi RV2 4GB)
    llamacpp_model_path: str = "./models/mini-orca-small-q4_k_m.gguf"
    llamacpp_n_ctx: int = 2048
    llamacpp_n_threads: int = 4
    llamacpp_n_gpu_layers: int = 0  # CPU-only for Orange Pi
    llamacpp_max_tokens: int = 512
    
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
