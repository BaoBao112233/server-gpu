#!/bin/bash

# Quick start script for 24GB GPU Server

echo "🚀 Starting LLM + Voice Server..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Running setup..."
    ./scripts/setup-24gb.sh
    echo ""
    echo "📝 Please review .env file and run this script again."
    echo "   nano .env"
    exit 0
fi

# Check if running in Docker or local
if [ "$1" == "--docker" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose build
    docker-compose up -d
    
    echo ""
    echo "✅ Server started!"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f api-server"
    echo ""
    echo "🔍 Monitor GPU:"
    echo "   ./scripts/gpu-monitor.sh"
    echo ""
    echo "🧪 Test API:"
    echo "   ./scripts/test-24gb.sh"
    
else
    echo "💻 Starting locally..."
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3.11 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    echo ""
    echo "Starting server..."
    python main.py &
    SERVER_PID=$!
    
    echo ""
    echo "✅ Server started (PID: $SERVER_PID)"
    echo ""
    echo "🔍 Monitor GPU:"
    echo "   ./scripts/gpu-monitor.sh"
    echo ""
    echo "🧪 Test API:"
    echo "   ./scripts/test-24gb.sh"
    echo ""
    echo "⏹️  Stop server:"
    echo "   kill $SERVER_PID"
fi

echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
