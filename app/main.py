import logging
import time
import json
import io
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
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
    EmbeddingData,
    TranscriptionRequest,
    TranscriptionResponse,
    SpeechRequest,
    VoiceListResponse
)
from app.backends import get_backend, get_voice_backend

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Global voice backend instance
voice_backend = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global voice_backend
    
    logger.info(f"Starting LLM API Server with {settings.model_backend} backend")
    logger.info(f"Default model: {settings.ollama_model if settings.model_backend == 'ollama' else settings.vllm_model}")
    logger.info("Voice models: Whisper (STT) + TTS enabled")
    
    # Initialize voice backend
    try:
        voice_backend = get_voice_backend()
        logger.info("Voice backend initialized")
    except Exception as e:
        logger.warning(f"Voice backend initialization failed: {e}")
    
    yield
    
    logger.info("Shutting down LLM API Server")
    
    # Cleanup voice backend
    if voice_backend:
        try:
            await voice_backend.__aexit__(None, None, None)
        except:
            pass


# Create FastAPI app
app = FastAPI(
    title="LLM + Voice API Server",
    description="Scalable LLM and Voice API Server with VLLM and Voice Models support (24GB VRAM optimized)",
    version="2.0.0",
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
        "message": "LLM + Voice API Server",
        "backend": settings.model_backend,
        "model": settings.ollama_model if settings.model_backend == "ollama" else settings.vllm_model,
        "voice": {
            "whisper": settings.whisper_model,
            "tts": settings.tts_model
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    backend = get_backend()
    
    try:
        is_healthy = await backend.health_check()
        
        # Get GPU info if available
        vram_info = None
        try:
            import torch
            if torch.cuda.is_available():
                vram_info = {
                    "total": f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f}GB",
                    "allocated": f"{torch.cuda.memory_allocated(0) / 1e9:.2f}GB",
                    "reserved": f"{torch.cuda.memory_reserved(0) / 1e9:.2f}GB"
                }
        except:
            pass
        
        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            backend=settings.model_backend,
            model=settings.ollama_model if settings.model_backend == "ollama" else settings.vllm_model,
            gpu_available=True,
            vram_usage=vram_info
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            backend=settings.model_backend,
            model=settings.ollama_model if settings.model_backend == "ollama" else settings.vllm_model,
            gpu_available=False
        )


@app.get("/v1/models", response_model=ModelListResponse)
async def list_models(api_key: str = Depends(verify_api_key)):
    """List available models"""
    backend = get_backend()
    
    try:
        models = await backend.list_models()
        
        # Add voice models
        if voice_backend:
            voice_models = await voice_backend.list_models()
            models.extend(voice_models)
        
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


# Voice Endpoints

@app.post("/v1/audio/transcriptions", response_model=TranscriptionResponse)
async def create_transcription(
    file: UploadFile = File(...),
    model: str = Form(default="whisper-base"),
    language: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    temperature: float = Form(default=0.0),
    api_key: str = Depends(verify_api_key)
):
    """
    OpenAI-compatible audio transcription endpoint
    Transcribes audio to text using Whisper
    """
    if not voice_backend:
        raise HTTPException(status_code=503, detail="Voice backend not available")
    
    try:
        # Read audio file
        audio_data = await file.read()
        audio_file = io.BytesIO(audio_data)
        
        # Transcribe
        result = await voice_backend.transcribe_audio(
            audio_file=audio_file,
            language=language,
            prompt=prompt,
            temperature=temperature
        )
        
        return TranscriptionResponse(**result)
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/audio/speech")
async def create_speech(
    request: SpeechRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    OpenAI-compatible text-to-speech endpoint
    Generates audio from text using TTS
    """
    if not voice_backend:
        raise HTTPException(status_code=503, detail="Voice backend not available")
    
    try:
        # Synthesize speech
        audio_data = await voice_backend.synthesize_speech(
            text=request.input,
            voice=request.voice,
            language=request.language,
            speed=request.speed
        )
        
        # Return audio response
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="speech.wav"'
            }
        )
        
    except Exception as e:
        logger.error(f"Speech synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/audio/voices", response_model=VoiceListResponse)
async def list_voices(api_key: str = Depends(verify_api_key)):
    """List available TTS voices"""
    if not voice_backend:
        raise HTTPException(status_code=503, detail="Voice backend not available")
    
    try:
        voices = await voice_backend.list_voices()
        return VoiceListResponse(voices=voices)
    except Exception as e:
        logger.error(f"Failed to list voices: {str(e)}")
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

