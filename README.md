# 🤖 LLM API Server

Scalable LLM hosting server with support for multiple backends (Ollama, vLLM, llama.cpp). Built with FastAPI and designed to be easily deployed across different hardware configurations.

## ✨ Features

- **🔄 Multiple Backend Support**: Ollama, vLLM, llama.cpp (easily switchable)
- **🚀 OpenAI-Compatible API**: Drop-in replacement for OpenAI API
- **💬 Streaming Support**: Real-time response streaming
- **🎯 Model Flexibility**: Easy to change models for different server configurations
- **🐳 Docker Support**: Containerized deployment with GPU support
- **📊 Built-in Chat UI**: Simple web interface for testing
- **🔐 API Key Authentication**: Optional security layer

## 📋 Requirements

### Current Configuration (GTX 1050 Ti - 4GB VRAM)
- **CPU**: Intel i3-10105F (4 cores, 8 threads)
- **RAM**: 16GB
- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM)
- **CUDA**: 12.9

### Recommended Models for This Configuration
- `phi3:mini` (3.8B) - **Recommended** ⭐
- `llama3.2:1b` (1B) - Very fast
- `qwen2.5:1.5b` (1.5B) - Good balance
- `gemma:2b` (2B) - Compact

### For Upgraded Servers (8GB+ VRAM)
- `llama3.1:8b`
- `mistral:7b`
- `gemma2:9b`

### For High-End Servers (24GB+ VRAM)
- `llama3.1:70b`
- `mixtral:8x7b`

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone and setup**:
```bash
cd /home/baobao/Projects/server-gpu
chmod +x scripts/*.sh
./scripts/setup.sh
```

2. **Access the services**:
- API Server: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Chat UI: Open `static/index.html` in browser

### Option 2: Local Development

1. **Setup environment**:
```bash
./scripts/dev-setup.sh
source venv/bin/activate
```

2. **Install and start Ollama** (if not using Docker):
```bash
# Install Ollama from https://ollama.ai
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull phi3:mini

# Run Ollama (in separate terminal)
ollama serve
```

3. **Start the API server**:
```bash
python main.py
```

## 📖 API Usage

### Chat Completion

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "phi3:mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
)

print(response.json())
```

### Streaming

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
