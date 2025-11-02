#!/bin/bash

# Pull additional models for testing
# Usage: ./pull-models.sh

MODELS=(
    "phi3:mini"
    "llama3.2:1b"
    "qwen2.5:1.5b"
    "gemma:2b"
)

echo "Pulling recommended models for GTX 1050 Ti (4GB VRAM)..."
echo ""

for model in "${MODELS[@]}"; do
    echo "Pulling $model..."
    docker exec llm-ollama ollama pull "$model"
    echo ""
done

echo "All models pulled successfully!"
echo ""
echo "To list all models:"
echo "  docker exec llm-ollama ollama list"
