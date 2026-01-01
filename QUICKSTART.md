# 🚀 QUICK START - Mini Orca trên Orange Pi RV2

## Cài đặt trong 5 phút

```bash
# 1. Setup tự động
./scripts/setup-mini-orca.sh

# 2. Start server
./mini-orca.sh start

# 3. Kiểm tra
./mini-orca.sh test
```

## Hoặc Setup thủ công

```bash
# 1. Tạo thư mục và cấu hình
mkdir -p models logs
cp .env.mini-orca .env

# 2. Download model (chọn 1 trong các options)

# Option A: Script tự động
./scripts/download-mini-orca.sh

# Option B: Download thủ công (TinyLlama - nhỏ nhất, nhanh nhất)
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
  -O models/mini-orca-small-q4_k_m.gguf

# Option C: Phi-2 (tốt hơn, hơi lớn)
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf \
  -O models/mini-orca-small-q4_k_m.gguf

# 3. Build và chạy
docker-compose build
docker-compose up -d

# 4. Test
curl http://localhost:8000/health
```

## Các lệnh thường dùng

```bash
./mini-orca.sh start      # Khởi động
./mini-orca.sh stop       # Dừng
./mini-orca.sh logs       # Xem logs
./mini-orca.sh status     # Xem trạng thái
./mini-orca.sh test       # Test API
```

## Test API nhanh

```bash
# Health check
curl http://localhost:8000/health

# Chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mini-orca-small",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

## Troubleshooting

### Server không start
```bash
# Xem logs
docker-compose logs

# Kiểm tra RAM
free -h

# Kiểm tra model file
ls -lh models/
```

### Out of Memory
Edit `.env`:
```bash
N_CTX=1024        # Giảm từ 2048
MAX_TOKENS=256    # Giảm từ 512
```

### Quá chậm
Edit `.env`:
```bash
N_THREADS=6       # Tăng theo CPU cores
MAX_TOKENS=100    # Giảm để response nhanh hơn
```

## Recommended Models cho 4GB RAM

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| TinyLlama 1.1B Q4 | ~650MB | ⚡⚡⚡ | ⭐⭐ |
| Phi-2 Q4 | ~1.6GB | ⚡⚡ | ⭐⭐⭐⭐ |
| Orca Mini 3B Q4 | ~2GB | ⚡ | ⭐⭐⭐ |

## Chi tiết đầy đủ

Xem [README.mini-orca.md](README.mini-orca.md)

## Hỗ trợ

- Logs: `./mini-orca.sh logs`
- Status: `./mini-orca.sh status`
- Test: `python3 scripts/test_mini_orca.py`
