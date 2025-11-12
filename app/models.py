from typing import Optional, List, Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (system, user, assistant)")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    max_tokens: Optional[int] = Field(2048, ge=1, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "llama3.1:8b",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False
            }
        }


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Usage] = None


class ChatCompletionStreamChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]


class EmbeddingRequest(BaseModel):
    model: str = Field(..., description="Model to use for embeddings")
    input: str | List[str] = Field(..., description="Input text(s) to embed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "nomic-embed-text",
                "input": "Hello, world!"
            }
        }


class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: Usage


# Voice Models

class TranscriptionRequest(BaseModel):
    """OpenAI-compatible transcription request"""
    file: bytes = Field(..., description="Audio file to transcribe")
    model: str = Field(default="whisper-base", description="Whisper model to use")
    language: Optional[str] = Field(None, description="Language code (e.g., 'en', 'vi', 'ja')")
    prompt: Optional[str] = Field(None, description="Optional text to guide the model")
    temperature: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Sampling temperature")
    response_format: Optional[str] = Field("json", description="Response format: json, text, srt, vtt")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "whisper-base",
                "language": "en",
                "response_format": "json"
            }
        }


class TranscriptionResponse(BaseModel):
    """OpenAI-compatible transcription response"""
    text: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(None, description="Detected language")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed segments with timestamps")


class SpeechRequest(BaseModel):
    """OpenAI-compatible text-to-speech request"""
    model: str = Field(..., description="TTS model to use")
    input: str = Field(..., description="Text to synthesize", max_length=4096)
    voice: Optional[str] = Field("alloy", description="Voice name or speaker ID")
    language: Optional[str] = Field("en", description="Language code")
    speed: Optional[float] = Field(1.0, ge=0.25, le=4.0, description="Speech speed")
    response_format: Optional[str] = Field("mp3", description="Audio format: mp3, opus, aac, flac, wav")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "tts-1",
                "input": "Hello, how are you today?",
                "voice": "alloy",
                "language": "en",
                "speed": 1.0
            }
        }


class VoiceListResponse(BaseModel):
    """List of available voices"""
    voices: List[str] = Field(..., description="Available voice names")


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "system"
    permission: List[Dict[str, Any]] = []


class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


class HealthResponse(BaseModel):
    status: str
    backend: str
    model: str
    gpu_available: bool
    vram_usage: Optional[Dict[str, Any]] = None

