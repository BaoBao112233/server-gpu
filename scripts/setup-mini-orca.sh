#!/bin/bash
# Quick setup script for Mini Orca on Orange Pi RV2

set -e

echo "==================================="
echo "Mini Orca Setup - Orange Pi RV2"
echo "==================================="
echo ""

# Check system info
echo "1. Checking system..."
echo "   OS: $(uname -s)"
echo "   Architecture: $(uname -m)"
echo "   Total RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "   Available RAM: $(free -h | grep Mem | awk '{print $7}')"
echo ""

# Check Docker
echo "2. Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "   ✗ Docker not found. Please install Docker first."
    echo "   Installation: curl -fsSL https://get.docker.com | sh"
    exit 1
fi
echo "   ✓ Docker version: $(docker --version)"

if ! command -v docker-compose &> /dev/null; then
    echo "   ✗ Docker Compose not found. Please install Docker Compose."
    exit 1
fi
echo "   ✓ Docker Compose version: $(docker-compose --version)"
echo ""

# Create directories
echo "3. Creating directories..."
mkdir -p models logs
echo "   ✓ Created: models/, logs/"
echo ""

# Setup environment
echo "4. Setting up environment..."
if [ ! -f .env ]; then
    cp .env.mini-orca .env
    echo "   ✓ Created .env from template"
else
    echo "   ⚠ .env already exists, skipping..."
fi
echo ""

# Download model
echo "5. Checking model..."
if [ ! -f models/mini-orca-small-q4_k_m.gguf ]; then
    echo "   Model not found. Would you like to download it now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        chmod +x scripts/download-mini-orca.sh
        ./scripts/download-mini-orca.sh
    else
        echo "   ⚠ Please download model manually to models/mini-orca-small-q4_k_m.gguf"
        echo "   Suggested sources:"
        echo "   - https://huggingface.co/TheBloke/orca_mini_3b-GGUF"
        echo "   - https://huggingface.co/TheBloke/Phi-2-GGUF"
    fi
else
    echo "   ✓ Model found: $(ls -lh models/mini-orca-small-q4_k_m.gguf | awk '{print $5}')"
fi
echo ""

# Build Docker image
echo "6. Building Docker image..."
echo "   This may take 10-20 minutes on Orange Pi..."
docker-compose build
echo "   ✓ Build complete"
echo ""

# Summary
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "  1. Start server:    docker-compose up -d"
echo "  2. View logs:       docker-compose logs -f"
echo "  3. Test API:        curl http://localhost:8000/health"
echo "  4. Stop server:     docker-compose down"
echo ""
echo "For more info, see README.mini-orca.md"
echo ""
