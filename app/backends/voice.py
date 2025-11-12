import io
import os
import time
import uuid
import tempfile
import wave
from typing import List, Dict, Any, Optional, BinaryIO
import torch
import numpy as np
from app.backends.base import BaseBackend


class VoiceBackend(BaseBackend):
    """Voice backend for Speech-to-Text (Whisper) and Text-to-Speech (Coqui TTS)"""
    
    def __init__(self, 
                 whisper_model: str = "base",
                 tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2",
                 device: str = "cuda",
                 gpu_memory_fraction: float = 0.3):
        """
        Initialize Voice backend
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large-v3)
            tts_model: Coqui TTS model name
            device: Device to use (cuda or cpu)
            gpu_memory_fraction: Fraction of GPU memory to reserve (0.3 = 30% of 24GB = 7.2GB)
        """
        self.whisper_model_name = whisper_model
        self.tts_model_name = tts_model
        self.device = device
        self.gpu_memory_fraction = gpu_memory_fraction
        
        self.whisper_model = None
        self.tts_model = None
        
        # Set memory limits for torch
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(gpu_memory_fraction)
    
    async def _initialize_whisper(self):
        """Lazy initialization of Whisper model"""
        if self.whisper_model is not None:
            return
            
        try:
            import whisper
            
            # Load Whisper model
            # Model sizes: tiny (~1GB), base (~1GB), small (~2GB), medium (~5GB), large-v3 (~10GB)
            self.whisper_model = whisper.load_model(
                self.whisper_model_name,
                device=self.device
            )
            
        except Exception as e:
            raise Exception(f"Failed to initialize Whisper model: {str(e)}")
    
    async def _initialize_tts(self):
        """Lazy initialization of TTS model"""
        if self.tts_model is not None:
            return
            
        try:
            from TTS.api import TTS
            
            # Load TTS model
            self.tts_model = TTS(
                model_name=self.tts_model_name,
                progress_bar=False,
                gpu=(self.device == "cuda")
            )
            
        except Exception as e:
            raise Exception(f"Failed to initialize TTS model: {str(e)}")
    
    async def transcribe_audio(self, 
                               audio_file: BinaryIO,
                               language: Optional[str] = None,
                               prompt: Optional[str] = None,
                               temperature: float = 0.0) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_file: Audio file binary data
            language: Language code (e.g., 'en', 'vi', 'ja')
            prompt: Optional text to guide the model
            temperature: Sampling temperature (0.0 = greedy)
        
        Returns:
            Dict with transcription text and metadata
        """
        await self._initialize_whisper()
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_path = tmp_file.name
            
            # Transcribe
            result = self.whisper_model.transcribe(
                tmp_path,
                language=language,
                initial_prompt=prompt,
                temperature=temperature,
                fp16=(self.device == "cuda")
            )
            
            # Clean up
            os.unlink(tmp_path)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language"),
                "duration": result.get("duration"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            raise Exception(f"Whisper transcription error: {str(e)}")
    
    async def synthesize_speech(self,
                                text: str,
                                voice: Optional[str] = None,
                                language: str = "en",
                                speed: float = 1.0) -> bytes:
        """
        Synthesize speech from text using TTS
        
        Args:
            text: Text to synthesize
            voice: Voice name or speaker ID
            language: Language code
            speed: Speech speed multiplier
        
        Returns:
            Audio data as bytes (WAV format)
        """
        await self._initialize_tts()
        
        try:
            # Generate speech
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_path = tmp_file.name
            
            # XTTS supports multiple languages and voice cloning
            if "xtts" in self.tts_model_name.lower():
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    language=language,
                    speaker_wav=voice if voice else None,  # Can use reference audio for voice cloning
                    speed=speed
                )
            else:
                # Standard TTS
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    speaker=voice if voice else None
                )
            
            # Read audio file
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(tmp_path)
            
            return audio_data
            
        except Exception as e:
            raise Exception(f"TTS synthesis error: {str(e)}")
    
    async def list_voices(self) -> List[str]:
        """List available voices for TTS"""
        await self._initialize_tts()
        
        try:
            if hasattr(self.tts_model, 'speakers'):
                return self.tts_model.speakers or []
            return []
        except:
            return []
    
    # Backend interface implementations (not applicable for voice)
    async def chat_completion(self, request) -> Dict[str, Any]:
        raise NotImplementedError("Voice backend doesn't support chat completion")
    
    async def chat_completion_stream(self, request):
        raise NotImplementedError("Voice backend doesn't support chat completion streaming")
    
    async def get_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        raise NotImplementedError("Voice backend doesn't support embeddings")
    
    async def list_models(self) -> List[str]:
        """List available models"""
        return [
            f"whisper-{self.whisper_model_name}",
            self.tts_model_name
        ]
    
    async def health_check(self) -> bool:
        """Check if models are healthy"""
        try:
            # Try to initialize at least Whisper
            await self._initialize_whisper()
            return self.whisper_model is not None
        except:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup models if needed
        if self.whisper_model is not None:
            del self.whisper_model
            self.whisper_model = None
        
        if self.tts_model is not None:
            del self.tts_model
            self.tts_model = None
        
        # Clear CUDA cache
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
