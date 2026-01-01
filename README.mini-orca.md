# Mini Orca Server - Orange Pi RV2 4GB RAM Edition

Server LLM tự host với **Mini Orca Small** (quantized) chạy trên **llama.cpp**, được tối ưu hóa cho Orange Pi RV2 với 4GB RAM.

## Đặc điểm

- ✅ **Model**: Mini Orca Small Q4_K_M (quantized ~2GB)
- ✅ **Inference Engine**: llama.cpp với OpenBLAS optimization
- ✅ **RAM Usage**: ~2.5-3GB (phù hợp cho 4GB RAM)
- ✅ **CPU Only**: Không cần GPU, chạy hoàn toàn trên CPU ARM
- ✅ **Docker**: Containerized để dễ triển khai
- ✅ **API Compatible**: OpenAI-compatible API endpoints

## Yêu cầu hệ thống

- **Hardware**: Orange Pi RV2 hoặc tương tự (ARM64 architecture)
- **RAM**: 4GB (khuyến nghị), tối thiểu 3GB available
- **Storage**: ~5GB (cho Docker image và model)
- **OS**: Linux với Docker và Docker Compose

## Cài đặt nhanh

### 1. Clone repository và chuẩn bị

```bash
cd /home/baobao/server-gpu
mkdir -p models logs
```

### 2. Download Mini Orca model

```bash
chmod +x scripts/download-mini-orca.sh
./scripts/download-mini-orca.sh
```

**Lưu ý**: Nếu script download không hoạt động, bạn có thể download thủ công:

```bash
# Option 1: Download từ Hugging Face (TheBloke's quantized models)
wget https://huggingface.co/TheBloke/orca_mini_3b-GGUF/resolve/main/orca_mini_3b.q4_k_m.gguf \
  -O models/mini-orca-small-q4_k_m.gguf

# Option 2: Hoặc dùng model tương tự khác (3B parameters, Q4_K_M quantization)
# Tìm kiếm trên https://huggingface.co/models?search=orca%20gguf
```

### 3. Cấu hình environment

```bash
# Copy env file mẫu
cp .env.mini-orca .env

# Chỉnh sửa nếu cần (tùy chọn)
nano .env
```

### 4. Build và chạy Docker container

```bash
# Build Docker image (có thể mất 10-20 phút trên Orange Pi)
docker-compose build

# Chạy container
docker-compose up -d

# Xem logs
docker-compose logs -f
```

### 5. Kiểm tra server

```bash
# Health check
curl http://localhost:8000/health

# Test chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mini-orca-small",
    "messages": [
      {"role": "user", "content": "Hello, who are you?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

## Cấu hình tùy chỉnh

### Tối ưu hóa RAM

Nếu gặp lỗi Out of Memory, điều chỉnh trong file `.env`:

```bash
# Giảm context window
N_CTX=1024              # Mặc định: 2048

# Giảm max tokens
MAX_TOKENS=256          # Mặc định: 512

# Giảm max RAM
MAX_RAM_MB=2560         # Mặc định: 3072
```

### Tối ưu hóa Performance

```bash
# Tăng threads (theo số CPU cores)
N_THREADS=6             # Mặc định: 4 (tùy Orange Pi model)

# Nếu có iGPU và muốn test (không khuyến nghị)
N_GPU_LAYERS=1          # Mặc định: 0
```

## API Endpoints

Server tương thích với OpenAI API:

### Chat Completion

```bash
POST /v1/chat/completions
```

### Streaming Chat

```bash
POST /v1/chat/completions
{
  "model": "mini-orca-small",
  "messages": [...],
  "stream": true
}
```

### List Models

```bash
GET /v1/models
```

### Health Check

```bash
GET /health
```

## Quản lý Docker

```bash
# Xem logs
docker-compose logs -f llama-cpp-server

# Stop server
docker-compose down

# Restart server
docker-compose restart

# Xem resource usage
docker stats mini-orca-server

# Update và rebuild
git pull
docker-compose up -d --build
```

## Performance trên Orange Pi RV2

Dự kiến performance:

- **Load time**: ~30-60 giây (lần đầu)
- **Inference speed**: ~2-5 tokens/giây (tùy context length)
- **RAM usage**: ~2.5-3GB
- **CPU usage**: 100% khi inference (normal)

**Tips**:
- Lần đầu load model sẽ chậm, sau đó sẽ nhanh hơn nhờ memory cache
- Giữ N_CTX nhỏ (1024-2048) để tiết kiệm RAM
- Không chạy quá nhiều ứng dụng khác cùng lúc
- Đảm bảo có swap space (~2GB) để tránh crash

## Troubleshooting

### Container không start

```bash
# Xem logs chi tiết
docker-compose logs llama-cpp-server

# Kiểm tra RAM available
free -h

# Kiểm tra model file
ls -lh models/
```

### Out of Memory

```bash
# Giảm N_CTX và MAX_RAM_MB trong .env
# Thêm swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Inference quá chậm

```bash
# Tăng N_THREADS theo số CPU cores
# Giảm MAX_TOKENS để response nhanh hơn
# Sử dụng temperature thấp (0.5-0.7)
```

### Model không download được

Download thủ công từ Hugging Face:
- Tìm "orca mini 3b gguf" hoặc "phi-2 gguf" 
- Chọn quantization Q4_K_M (cân bằng giữa size và quality)
- Download về thư mục `models/` và đổi tên phù hợp

## Alternatives Models (nếu Mini Orca không có)

Các model tương đương phù hợp cho 4GB RAM:

1. **Phi-2 Q4_K_M** (~1.6GB) - Microsoft, rất tốt
2. **TinyLlama Q4_K_M** (~650MB) - Nhỏ nhất, nhanh nhất
3. **Orca Mini 3B Q4_K_M** (~2GB) - Tương tự Mini Orca
4. **StableLM 3B Q4_K_M** (~2GB) - Stability AI

Download URL patterns:
```
https://huggingface.co/TheBloke/{MODEL_NAME}-GGUF/resolve/main/{model_file}.q4_k_m.gguf
```

## License

Xem LICENSE file. Model Mini Orca tuân theo license của OpenOrca dataset và base model.

## Support

- Issues: GitHub Issues
- Docs: [llama-cpp-python docs](https://llama-cpp-python.readthedocs.io/)
- Models: [Hugging Face GGUF models](https://huggingface.co/models?search=gguf)
