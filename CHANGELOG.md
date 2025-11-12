# CHANGELOG - 24GB GPU Optimization

## Version 2.0.0 - GPU 24GB VRAM Optimization (2024-11-12)

### 🎯 Major Changes

#### New Features
- ✅ **vLLM Backend Integration**: High-performance LLM inference with memory optimization
- ✅ **Voice Models Support**: 
  - Whisper (Speech-to-Text) with multiple model sizes
  - Coqui TTS/XTTS v2 (Text-to-Speech) with multilingual support
- ✅ **GPU Memory Management**: Optimized allocation strategy for 24GB VRAM
- ✅ **Real-time GPU Monitoring**: New monitoring script with detailed metrics
- ✅ **OpenAI-Compatible Voice API**: `/v1/audio/transcriptions` and `/v1/audio/speech`

#### Backend Improvements
- ✅ `app/backends/vllm.py`: New vLLM backend with tensor parallelism
- ✅ `app/backends/voice.py`: New voice backend (Whisper + TTS)
- ✅ `app/backends/__init__.py`: Updated factory with voice backend support
- ✅ Memory optimization with lazy loading
- ✅ CUDA graphs enabled for better performance
- ✅ KV cache optimization

#### API Enhancements
- ✅ `app/main.py`: 
  - Added voice endpoints
  - Updated health check with VRAM info
  - Global voice backend management
  - Improved error handling
- ✅ `app/models.py`: 
  - New voice request/response models
  - TranscriptionRequest, TranscriptionResponse
  - SpeechRequest, VoiceListResponse
- ✅ `app/config.py`: 
  - Added voice configuration
  - Updated default models for 24GB

#### Configuration
- ✅ `config.yaml`: 
  - Reorganized for 24GB VRAM
  - Added model categories (LLM Ollama, LLM vLLM, Voice)
  - GPU memory allocation strategy
  - Voice model configurations
- ✅ `.env.example`: Complete template with all options
- ✅ `docker-compose.yml`: 
  - GPU resource limits
  - Memory management
  - Separate profiles (vllm, ollama)
  - Volume mounts for caching

#### Docker & Deployment
- ✅ `Dockerfile`: 
  - Updated to NVIDIA CUDA 12.4 base
  - Python 3.11
  - PyTorch with CUDA support
  - Health check added
- ✅ Better layer caching
- ✅ Optimized for build time

#### Scripts
- ✅ `scripts/setup-24gb.sh`: Complete setup automation
- ✅ `scripts/gpu-monitor.sh`: Real-time GPU monitoring
- ✅ `scripts/test-24gb.sh`: Comprehensive API testing
- ✅ `start.sh`: Quick start script

#### Documentation
- ✅ `README.md`: Updated with 24GB focus
- ✅ `DEPLOYMENT_GUIDE_VI.md`: Vietnamese deployment guide
- ✅ `SETUP_SUMMARY.md`: Complete setup documentation
- ✅ API examples for all endpoints
- ✅ Troubleshooting guides

#### Dependencies
- ✅ `requirements.txt`:
  - Added vLLM 0.6.3
  - Added PyTorch 2.5.1 with CUDA 12.4
  - Added Transformers 4.46.2
  - Added OpenAI Whisper
  - Added Coqui TTS
  - Added audio libraries (soundfile, librosa, pydub)
  - Added GPU monitoring tools

### 📊 Memory Allocation Strategy

**Before (4GB GPU):**
- LLM only: ~3-4GB
- No voice support

**After (24GB GPU):**
- LLM (vLLM): 12GB (50%)
- Voice Models: 7GB (30%)
- Buffer: 5GB (20%)

### 🎯 Supported Models

#### LLM Models (New)
- Llama 3.1 8B Instruct (10GB)
- Mistral 7B Instruct (9GB)
- Qwen 2.5 7B/14B (9-12GB)

#### Voice Models (New)
- Whisper: tiny, base, small, medium, large-v3
- XTTS v2: Multilingual TTS with voice cloning

### 🚀 Performance Improvements
- 🔥 **vLLM**: 2-3x faster than Ollama
- 🔥 **CUDA Graphs**: Reduced latency
- 🔥 **KV Cache**: Better memory efficiency
- 🔥 **Prefix Caching**: Faster repeated queries

### 🐛 Bug Fixes
- Fixed memory leaks in backend initialization
- Improved error handling for OOM situations
- Better cleanup on shutdown

### 📝 Breaking Changes
- Default backend changed from `ollama` to `vllm`
- Default model changed from `phi3:mini` to `llama3.1:8b`
- New environment variables required for voice models
- Docker Compose profiles added (requires explicit activation for Ollama)

### 🔄 Migration Guide

#### From Version 1.x to 2.0.0

1. **Update .env file:**
```bash
# Add new variables
MODEL_BACKEND=vllm
VLLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
VLLM_GPU_MEMORY_UTILIZATION=0.50
WHISPER_MODEL=base
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
VOICE_GPU_MEMORY_FRACTION=0.30
```

2. **Update dependencies:**
```bash
pip install -r requirements.txt
```

3. **Rebuild Docker image:**
```bash
docker-compose build
```

4. **Update model paths:**
- Old: `ollama pull phi3:mini`
- New: Model auto-downloads from HuggingFace

### 📈 Metrics & Monitoring

New monitoring capabilities:
- Real-time VRAM usage
- GPU temperature
- Process listing
- Memory allocation breakdown
- Alert thresholds

### 🎨 New API Endpoints

```
POST /v1/audio/transcriptions  - Speech-to-Text
POST /v1/audio/speech          - Text-to-Speech
GET  /v1/audio/voices          - List available voices
GET  /health                   - Enhanced with VRAM info
```

### 🔐 Security
- API key authentication (optional)
- CORS configuration
- Input validation
- Rate limiting ready

### 🧪 Testing
- New comprehensive test suite
- Health check tests
- LLM endpoint tests
- Voice endpoint tests
- Streaming tests

### 📚 Documentation
- Complete API documentation
- Vietnamese deployment guide
- Troubleshooting guides
- Performance tuning guides
- Example code in multiple languages

### 🎯 Next Version Preview (2.1.0)
- [ ] Batch processing for voice
- [ ] Model caching improvements
- [ ] Multi-GPU support
- [ ] Load balancing
- [ ] Metrics dashboard
- [ ] Request queue management

---

## Version 1.0.0 - Initial Release

### Features
- Basic LLM server with Ollama
- OpenAI-compatible API
- Docker support
- Simple chat UI

### Models
- Phi-3 Mini (3.8B)
- Llama 3.2 1B
- Qwen 2.5 1.5B

---

**Contributors**: BaoBao112233
**GPU Tested**: NVIDIA GPUs with 24GB VRAM (RTX 3090, RTX 4090, A5000)
**Python Version**: 3.11+
**CUDA Version**: 12.4+
