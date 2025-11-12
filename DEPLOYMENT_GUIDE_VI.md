# Hướng Dẫn Triển Khai LLM + Voice Server trên GPU 24GB VRAM

## Tổng Quan

Repo này đã được tối ưu hóa để chạy đồng thời:
- **LLM Models** (vLLM hoặc Ollama) - ~12GB VRAM
- **Whisper STT** (Speech-to-Text) - ~1-2GB VRAM
- **TTS** (Text-to-Speech) - ~4-5GB VRAM

Tổng cộng sử dụng ~17-19GB VRAM, còn lại ~5-7GB buffer cho CUDA operations.

## Bước 1: Chuẩn Bị Môi Trường

### Kiểm Tra GPU

```bash
nvidia-smi
```

Đảm bảo GPU có 24GB VRAM và CUDA version 12.4+

### Clone Repo

```bash
cd /home/baobao
git clone <your-repo>
cd server-gpu
```

## Bước 2: Cài Đặt

### Chạy Script Setup

```bash
chmod +x scripts/setup-24gb.sh
./scripts/setup-24gb.sh
```

Script này sẽ:
- Tạo file `.env` với cấu hình mặc định
- Tạo các thư mục cần thiết
- Kiểm tra GPU

### Cài Đặt Dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python3.11 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Bước 3: Cấu Hình

### Chỉnh Sửa File `.env`

```bash
nano .env
```

Cấu hình quan trọng:

```bash
# Backend: vllm hoặc ollama
MODEL_BACKEND=vllm

# Model LLM (chọn 1 trong số này)
VLLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct  # Khuyến nghị
# VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.3
# VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct

# Memory allocation cho LLM
VLLM_GPU_MEMORY_UTILIZATION=0.50  # 50% = ~12GB

# Voice models
WHISPER_MODEL=base    # tiny, base, small, medium, large-v3
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2

# Memory allocation cho Voice
VOICE_GPU_MEMORY_FRACTION=0.30  # 30% = ~7GB
```

## Bước 4: Chạy Server

### Option 1: Chạy Trực Tiếp (Development)

```bash
python main.py
```

Server sẽ chạy tại: `http://localhost:8000`

### Option 2: Docker (Production - Khuyến Nghị)

```bash
# Build image
docker-compose build

# Chạy server
docker-compose up -d

# Xem logs
docker-compose logs -f api-server

# Dừng server
docker-compose down
```

## Bước 5: Kiểm Tra

### Health Check

```bash
curl http://localhost:8000/health
```

Response mong đợi:
```json
{
  "status": "healthy",
  "backend": "vllm",
  "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
  "gpu_available": true,
  "vram_usage": {
    "total": "24.00GB",
    "allocated": "15.23GB",
    "reserved": "16.50GB"
  }
}
```

### Test Chat API

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### Test Voice API

```bash
# Test Speech-to-Text
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@test_audio.mp3" \
  -F "model=whisper-base"

# Test Text-to-Speech
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "Hello World", "language": "en"}' \
  --output output.wav
```

## Bước 6: Giám Sát GPU

### Chạy GPU Monitor

```bash
./scripts/gpu-monitor.sh
```

Hoặc với interval tùy chỉnh:

```bash
./scripts/gpu-monitor.sh 2 90  # Check mỗi 2s, cảnh báo khi >90%
```

Monitor sẽ hiển thị:
- VRAM usage real-time
- GPU utilization
- Temperature
- Running processes
- Memory allocation breakdown

## Tối Ưu Hóa

### Nếu Gặp Lỗi OOM (Out of Memory)

1. **Giảm memory allocation cho LLM:**

```bash
VLLM_GPU_MEMORY_UTILIZATION=0.40  # Giảm từ 0.50 xuống 0.40
```

2. **Dùng Whisper model nhỏ hơn:**

```bash
WHISPER_MODEL=tiny  # Hoặc base
```

3. **Giảm context length:**

```bash
VLLM_MAX_MODEL_LEN=4096  # Giảm từ 8192
```

### Tăng Hiệu Suất LLM

Nếu không dùng voice models nhiều:

```bash
VLLM_GPU_MEMORY_UTILIZATION=0.70  # Tăng lên 70%
VOICE_GPU_MEMORY_FRACTION=0.15    # Giảm xuống 15%
```

### Tối Ưu Cho Voice

Nếu voice là ưu tiên:

```bash
WHISPER_MODEL=medium              # Dùng model chính xác hơn
VLLM_GPU_MEMORY_UTILIZATION=0.40  # Giảm LLM xuống
VOICE_GPU_MEMORY_FRACTION=0.40    # Tăng voice lên
```

## Sử Dụng API

### Với Python

```python
from openai import OpenAI

# Chat
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    messages=[
        {"role": "user", "content": "Giải thích machine learning"}
    ]
)
print(response.choices[0].message.content)

# Voice (transcription)
audio_file = open("audio.mp3", "rb")
transcript = client.audio.transcriptions.create(
    model="whisper-base",
    file=audio_file,
    language="vi"
)
print(transcript.text)

# Voice (speech)
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Xin chào, đây là demo text to speech",
    response_format="wav"
)
response.stream_to_file("output.wav")
```

### Với cURL

Xem file README.md chính để biết thêm ví dụ.

## Troubleshooting

### Server Không Start

```bash
# Kiểm tra logs
docker-compose logs api-server

# Kiểm tra GPU
nvidia-smi

# Kiểm tra CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### VRAM Đầy

```bash
# Clear CUDA cache
docker-compose restart api-server

# Hoặc nếu chạy trực tiếp
# Restart Python process
```

### Voice Models Không Load

```bash
# Kiểm tra TTS cache
ls -la ~/.local/share/tts/

# Download lại models
rm -rf ~/.local/share/tts/
docker-compose restart api-server
```

### Hiệu Suất Chậm

1. Kiểm tra GPU utilization:
```bash
./scripts/gpu-monitor.sh
```

2. Kiểm tra model size trong memory:
```bash
nvidia-smi
```

3. Thử giảm batch size hoặc context length

## Cấu Trúc Files Quan Trọng

```
server-gpu/
├── .env                    # Cấu hình chính
├── config.yaml             # Model configs
├── docker-compose.yml      # Docker setup
├── main.py                 # Entry point
├── app/
│   ├── main.py            # FastAPI app
│   ├── config.py          # Settings
│   ├── models.py          # Pydantic models
│   └── backends/
│       ├── vllm.py        # vLLM backend
│       ├── ollama.py      # Ollama backend
│       └── voice.py       # Voice backend
└── scripts/
    ├── setup-24gb.sh      # Setup script
    └── gpu-monitor.sh     # GPU monitor
```

## Kết Luận

Server đã được tối ưu hóa để:
- Chạy LLM models mạnh (7-8B parameters)
- Hỗ trợ speech-to-text chất lượng cao
- Hỗ trợ text-to-speech đa ngôn ngữ
- Tất cả trên 1 GPU 24GB VRAM

Để có hiệu suất tốt nhất, theo dõi VRAM usage thường xuyên và điều chỉnh allocation theo nhu cầu sử dụng thực tế.
