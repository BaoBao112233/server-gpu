# 🤖 LLM + Voice API Server (24GB VRAM Optimized)

Self-hosted LLM, VLLM, and Voice Model server optimized for single GPU with 24GB VRAM. Supports high-performance text generation, speech-to-text (Whisper), and text-to-speech (TTS).

## ✨ Features

- 🚀 **High-Performance LLM Inference** with vLLM
- 🗣️ **Speech-to-Text** using OpenAI Whisper (multiple model sizes)
- 🎤 **Text-to-Speech** using Coqui TTS/XTTS v2 (multilingual, voice cloning)
- 🔄 **Multiple Backend Support** (vLLM recommended, Ollama optional)
- 🌐 **OpenAI-Compatible API** for easy integration
- 📊 **GPU Memory Management** optimized for 24GB VRAM
- 🐳 **Docker Support** with GPU acceleration
- 💬 **Streaming Support** for real-time responses

## � GPU Memory Allocation (24GB)

| Component | Allocation | VRAM | Use Case |
|-----------|-----------|------|----------|
| LLM (vLLM) | 50% | ~12GB | Text generation, chat |
| Voice Models | 30% | ~7GB | STT (Whisper) + TTS |
| Buffer/Shared | 20% | ~5GB | CUDA operations, cache |

## 🎯 Supported Models

### LLM Models (vLLM - Recommended)
### LLM Models (vLLM - Recommended)
- **Llama 3.1 8B Instruct** ✅ (~10GB) - Best general purpose
- **Mistral 7B Instruct** (~9GB) - Excellent instruction following
- **Qwen 2.5 7B Instruct** (~9GB) - Multilingual support

### LLM Models (Ollama - Alternative)
- **Llama 3.1 8B** (~8GB)
- **Mistral 7B** (~7GB)
- **Qwen 2.5 14B** (~12GB) - Larger model option
- **Gemma2 9B** (~10GB)

### Voice Models
- **Whisper STT**: tiny, base ✅, small, medium, large-v3
- **TTS**: XTTS v2 ✅ (multilingual, 16+ languages), Tacotron2

## 📋 Requirements

- **GPU**: NVIDIA GPU with 24GB VRAM (RTX 3090, RTX 4090, A5000, etc.)
- **RAM**: 32GB+ recommended
- **CUDA**: 12.4+
- **Storage**: 50GB+ for models
- **OS**: Linux (Ubuntu 22.04+ recommended)

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and setup
chmod +x scripts/setup-24gb.sh
./scripts/setup-24gb.sh
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 3. Run Server

#### Option A: Docker (Recommended)

```bash
# Using vLLM backend (recommended)
docker-compose build
docker-compose up -d

# Using Ollama backend (optional)
docker-compose --profile ollama up -d

# View logs
docker-compose logs -f api-server
```

#### Option B: Local Development

```bash
# Start server
python main.py
```

### 4. Monitor GPU Usage

```bash
# Monitor VRAM in real-time
./scripts/gpu-monitor.sh

# Check every 2 seconds with 95% alert threshold
./scripts/gpu-monitor.sh 2 95
```

### 5. Access API

- **API Server**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>

## ⚙️ Configuration

Create or edit `.env` file:

```bash
# Backend: vllm (recommended) or ollama
MODEL_BACKEND=vllm

# vLLM Configuration (Recommended for 24GB)
VLLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
VLLM_GPU_MEMORY_UTILIZATION=0.50  # 50% for LLM (~12GB)
VLLM_MAX_MODEL_LEN=8192

# Voice Configuration
WHISPER_MODEL=base              # tiny, base, small, medium, large-v3
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
VOICE_GPU_MEMORY_FRACTION=0.30  # 30% for Voice (~7GB)

# Server Settings
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## 📖 API Usage

### Chat Completion (LLM)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Speech-to-Text (Whisper)

```bash
# Transcribe audio file
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@audio.mp3" \
  -F "model=whisper-base" \
  -F "language=en"

# Auto-detect language
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=whisper-base"
```

### Text-to-Speech (TTS)

```bash
# Generate speech from text
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello, how are you today?",
    "voice": "alloy",
    "language": "en",
    "speed": 1.0
  }' \
  --output speech.wav

# Vietnamese TTS
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Xin chào, bạn khỏe không?",
    "language": "vi"
  }' \
  --output speech_vi.wav
```

### Python SDK Usage

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "phi3:mini",
        "messages": [{"role": "user", "content": "Tell me a story"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if data != '[DONE]':
                print(data['choices'][0]['delta'].get('content', ''), end='')
```

### Using with OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # if API key auth is disabled
)

response = client.chat.completions.create(
    model="phi3:mini",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Model Backend (ollama, vllm, llamacpp)
MODEL_BACKEND=ollama

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=1

# API Security (optional)
ENABLE_API_KEY=false
API_KEY=your-secret-key-here

# Generation Defaults
MAX_TOKENS=2048
TEMPERATURE=0.7
TOP_P=0.9
```

### Changing Models

Edit `.env` file:
```bash
OLLAMA_MODEL=llama3.2:1b  # or any other model
```

Or use the chat UI to switch models dynamically.

## 🔧 Managing Models

### Pull new models:
```bash
# Using Docker
docker exec llm-ollama ollama pull llama3.2:1b

# Or use the script
./scripts/pull-models.sh
```

### List available models:
```bash
docker exec llm-ollama ollama list
```

### Remove models:
```bash
docker exec llm-ollama ollama rm model-name
```

## 🧪 Testing

Run the test suite:
```bash
python scripts/test_api.py
```

Or test individual endpoints:
```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/v1/models

# Chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 📁 Project Structure

```
server-gpu/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   └── backends/
│       ├── __init__.py
│       ├── base.py          # Abstract base class
│       ├── ollama.py        # Ollama implementation
│       ├── vllm.py          # vLLM implementation (TODO)
│       └── llamacpp.py      # llama.cpp implementation (TODO)
├── static/
│   └── index.html           # Chat UI
├── scripts/
│   ├── setup.sh             # Docker setup
│   ├── dev-setup.sh         # Local development setup
│   ├── pull-models.sh       # Pull recommended models
│   └── test_api.py          # API test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── config.yaml              # Model configurations
├── .env.example
└── README.md
```

## 🚢 Deployment

### Docker Compose (Production)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Systemd Service (Linux)

Create `/etc/systemd/system/llm-server.service`:
```ini
[Unit]
Description=LLM API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/server-gpu
Environment="PATH=/path/to/server-gpu/venv/bin"
ExecStart=/path/to/server-gpu/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable llm-server
sudo systemctl start llm-server
```

## 🔄 Migrating to More Powerful Server

When upgrading to a server with more GPU memory:

1. **Update the model** in `.env`:
```bash
OLLAMA_MODEL=llama3.1:8b  # or larger
```

2. **Pull the new model**:
```bash
docker exec llm-ollama ollama pull llama3.1:8b
```

3. **Restart the service**:
```bash
docker-compose restart api-server
```

That's it! The architecture is designed to scale seamlessly.

## 📊 Performance Tips

1. **For GTX 1050 Ti (4GB)**:
   - Use quantized models (4-bit, 8-bit)
   - Stick to models < 4B parameters
   - Consider CPU offloading for larger context

2. **Optimize GPU Memory**:
   ```bash
   # Reduce context length
   LLAMACPP_N_CTX=2048
   ```

3. **Concurrent Requests**:
   - Current config handles 1-5 concurrent requests
   - Adjust `max_concurrent_requests` in `config.yaml`

## 🐛 Troubleshooting

### Server won't start
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check logs
docker-compose logs api-server
```

### Out of memory errors
- Use smaller models
- Reduce `max_tokens` and `n_ctx`
- Enable CPU offloading

### Slow responses
- Try smaller models (1B-2B)
- Reduce `max_tokens`
- Check GPU utilization: `nvidia-smi`

## 📝 License

MIT License - feel free to use this for any purpose.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Implement vLLM backend
- [ ] Implement llama.cpp backend
- [ ] Add embeddings support
- [ ] Add model caching
- [ ] Add request queue management
- [ ] Add metrics and monitoring

## 🔗 Resources

- [Ollama Documentation](https://ollama.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

Built with ❤️ for scalable LLM deployment
