import logging
import time
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelListResponse,
    ModelInfo,
    HealthResponse,
    Usage,
    EmbeddingData
)
from app.backends import get_backend

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"Starting LLM API Server with {settings.model_backend} backend")
    logger.info(f"Default model: {settings.ollama_model}")
    yield
    logger.info("Shutting down LLM API Server")


# Create FastAPI app
app = FastAPI(
    title="LLM API Server",
    description="Scalable LLM API Server with multiple backend support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key if enabled"""
    if settings.enable_api_key:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing API key")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        if token != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLM API Server",
        "backend": settings.model_backend,
        "model": settings.ollama_model,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    backend = get_backend()
    
    try:
        is_healthy = await backend.health_check()
        
        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            backend=settings.model_backend,
            model=settings.ollama_model,
            gpu_available=True  # Could add actual GPU check here
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            backend=settings.model_backend,
            model=settings.ollama_model,
            gpu_available=False
        )


@app.get("/v1/models", response_model=ModelListResponse)
async def list_models(api_key: str = Depends(verify_api_key)):
    """List available models"""
    backend = get_backend()
    
    try:
        models = await backend.list_models()
        
        return ModelListResponse(
            object="list",
            data=[
                ModelInfo(
                    id=model,
                    object="model",
                    owned_by="system"
                )
                for model in models
            ]
        )
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    """OpenAI-compatible chat completions endpoint"""
    backend = get_backend()
    
    try:
        if request.stream:
            # Return streaming response
            async def generate():
                async for chunk in backend.chat_completion_stream(request):
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        else:
            # Return regular response
            result = await backend.chat_completion(request)
            return JSONResponse(content=result)
            
    except Exception as e:
        logger.error(f"Chat completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    api_key: str = Depends(verify_api_key)
):
    """OpenAI-compatible embeddings endpoint"""
    backend = get_backend()
    
    try:
        # Handle both string and list inputs
        texts = [request.input] if isinstance(request.input, str) else request.input
        
        embeddings = await backend.get_embeddings(texts, request.model)
        
        return EmbeddingResponse(
            object="list",
            data=[
                EmbeddingData(
                    object="embedding",
                    embedding=emb,
                    index=idx
                )
                for idx, emb in enumerate(embeddings)
            ],
            model=request.model,
            usage=Usage(
                prompt_tokens=sum(len(text.split()) for text in texts),
                completion_tokens=0,
                total_tokens=sum(len(text.split()) for text in texts)
            )
        )
    except Exception as e:
        logger.error(f"Embeddings creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
