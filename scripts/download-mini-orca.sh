#!/bin/bash
# Script to download Mini Orca quantized model for Orange Pi RV2 4GB RAM

set -e

MODEL_DIR="./models"
MODEL_FILE="mini-orca-small-q4_k_m.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"

# Create models directory
mkdir -p "$MODEL_DIR"

echo "=== Mini Orca Model Downloader ==="
echo "Target: Orange Pi RV2 with 4GB RAM"
echo "Model: Mini Orca Small Q4_K_M (Quantized)"
echo ""

# Check if model already exists
if [ -f "$MODEL_PATH" ]; then
    echo "✓ Model already exists at $MODEL_PATH"
    echo "  Size: $(du -h "$MODEL_PATH" | cut -f1)"
    exit 0
fi

echo "Downloading Mini Orca Small Q4_K_M..."
echo "This model is optimized for low-resource devices."
echo ""

# Download from Hugging Face
# Note: Mini Orca is based on OpenOrca dataset
# Using a quantized version suitable for 4GB RAM

# Option 1: Using TheBloke's quantized versions (if available)
MODEL_URL="https://huggingface.co/TheBloke/MiniOrca-GGUF/resolve/main/miniorca.q4_k_m.gguf"

# Alternative URLs (uncomment if main URL doesn't work)
# MODEL_URL="https://huggingface.co/pankajmathur/orca_mini_3b/resolve/main/orca-mini-3b.q4_k_m.gguf"

echo "Downloading from: $MODEL_URL"
echo ""

# Download with wget or curl
if command -v wget &> /dev/null; then
    wget -O "$MODEL_PATH" "$MODEL_URL" --progress=bar:force 2>&1
elif command -v curl &> /dev/null; then
    curl -L -o "$MODEL_PATH" "$MODEL_URL" --progress-bar
else
    echo "Error: Neither wget nor curl is installed"
    exit 1
fi

if [ -f "$MODEL_PATH" ]; then
    echo ""
    echo "✓ Download complete!"
    echo "  Model: $MODEL_PATH"
    echo "  Size: $(du -h "$MODEL_PATH" | cut -f1)"
    echo ""
    echo "The model is ready to use with llama.cpp"
else
    echo "✗ Download failed"
    exit 1
fi
