#!/bin/bash

# Environment setup script for 24GB GPU server
# Configures optimal settings for running LLM + VLLM + Voice models

set -e

echo "=================================="
echo "24GB GPU Server Setup"
echo "=================================="
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Backend Configuration
# Options: vllm (recommended), ollama
MODEL_BACKEND=vllm

# Ollama Settings (if using ollama backend)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# vLLM Settings (recommended for 24GB VRAM)
VLLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
VLLM_GPU_MEMORY_UTILIZATION=0.50
VLLM_MAX_MODEL_LEN=8192
VLLM_TENSOR_PARALLEL_SIZE=1

# Voice Model Settings
WHISPER_MODEL=base
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
VOICE_DEVICE=cuda
VOICE_GPU_MEMORY_FRACTION=0.30

# Server Settings
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# API Security (optional)
ENABLE_API_KEY=false
# API_KEY=your-secret-key-here

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p models logs
echo "✓ Directories created"

# Make scripts executable
echo ""
echo "Setting script permissions..."
chmod +x scripts/*.sh
echo "✓ Scripts are now executable"

# Check for NVIDIA GPU
echo ""
echo "Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    
    # Get VRAM size
    vram_mb=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    vram_gb=$(echo "scale=0; $vram_mb/1024" | bc)
    
    echo ""
    if [ "$vram_gb" -ge 20 ]; then
        echo "✓ GPU has sufficient VRAM (${vram_gb}GB)"
    else
        echo "⚠️  Warning: GPU has only ${vram_gb}GB VRAM"
        echo "   This configuration is optimized for 24GB"
        echo "   You may need to adjust memory allocations"
    fi
else
    echo "⚠️  nvidia-smi not found"
    echo "   Please install NVIDIA drivers"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Review and edit .env file if needed:"
echo "   nano .env"
echo ""
echo "2. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "3. For Docker deployment:"
echo "   docker-compose up -d"
echo ""
echo "4. For local development:"
echo "   python main.py"
echo ""
echo "5. Monitor GPU usage:"
echo "   ./scripts/gpu-monitor.sh"
echo ""
echo "6. Pull Ollama models (if using ollama):"
echo "   ./scripts/pull-models.sh"
echo ""
echo "API Documentation:"
echo "- Local: http://localhost:8000/docs"
echo "- Chat: POST /v1/chat/completions"
echo "- Voice: POST /v1/audio/transcriptions"
echo "- TTS: POST /v1/audio/speech"
echo ""
