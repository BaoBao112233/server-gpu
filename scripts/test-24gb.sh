#!/bin/bash

# Test script for LLM + Voice API Server

set -e

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=================================="
echo "Testing LLM + Voice API Server"
echo "=================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
response=$(curl -s "$BASE_URL/health")
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$response" | python3 -m json.tool
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "$response"
fi
echo ""

# Test 2: List Models
echo "Test 2: List Models"
response=$(curl -s "$BASE_URL/v1/models")
if echo "$response" | grep -q "data"; then
    echo -e "${GREEN}✓ List models passed${NC}"
    echo "$response" | python3 -m json.tool | head -20
else
    echo -e "${RED}✗ List models failed${NC}"
    echo "$response"
fi
echo ""

# Test 3: Chat Completion
echo "Test 3: Chat Completion (Non-streaming)"
response=$(curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "messages": [
      {"role": "user", "content": "Say hello in one sentence."}
    ],
    "max_tokens": 50,
    "temperature": 0.7
  }')

if echo "$response" | grep -q "choices"; then
    echo -e "${GREEN}✓ Chat completion passed${NC}"
    echo "$response" | python3 -m json.tool
else
    echo -e "${RED}✗ Chat completion failed${NC}"
    echo "$response"
fi
echo ""

# Test 4: Chat Completion Streaming
echo "Test 4: Chat Completion (Streaming)"
echo "Starting stream..."
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "messages": [
      {"role": "user", "content": "Count from 1 to 5."}
    ],
    "stream": true,
    "max_tokens": 100
  }' | head -20

echo -e "\n${GREEN}✓ Streaming test completed${NC}\n"

# Test 5: Voice - Transcription (if test audio exists)
if [ -f "test_audio.mp3" ] || [ -f "test_audio.wav" ]; then
    echo "Test 5: Speech-to-Text (Transcription)"
    
    audio_file="test_audio.mp3"
    if [ ! -f "$audio_file" ]; then
        audio_file="test_audio.wav"
    fi
    
    response=$(curl -s -X POST "$BASE_URL/v1/audio/transcriptions" \
      -F "file=@$audio_file" \
      -F "model=whisper-base" \
      -F "language=en")
    
    if echo "$response" | grep -q "text"; then
        echo -e "${GREEN}✓ Transcription passed${NC}"
        echo "$response" | python3 -m json.tool
    else
        echo -e "${RED}✗ Transcription failed${NC}"
        echo "$response"
    fi
    echo ""
else
    echo "Test 5: Speech-to-Text (Transcription)"
    echo "⊘ Skipped (no test audio file found)"
    echo "  Create test_audio.mp3 or test_audio.wav to test"
    echo ""
fi

# Test 6: Text-to-Speech
echo "Test 6: Text-to-Speech"
curl -s -X POST "$BASE_URL/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello, this is a test.",
    "voice": "alloy",
    "language": "en"
  }' \
  --output test_output.wav

if [ -f "test_output.wav" ] && [ -s "test_output.wav" ]; then
    file_size=$(stat -f%z "test_output.wav" 2>/dev/null || stat -c%s "test_output.wav")
    echo -e "${GREEN}✓ TTS passed${NC}"
    echo "  Generated: test_output.wav (${file_size} bytes)"
    rm test_output.wav
else
    echo -e "${RED}✗ TTS failed${NC}"
fi
echo ""

# Test 7: List Voices
echo "Test 7: List Available Voices"
response=$(curl -s "$BASE_URL/v1/audio/voices")
if echo "$response" | grep -q "voices"; then
    echo -e "${GREEN}✓ List voices passed${NC}"
    echo "$response" | python3 -m json.tool
else
    echo -e "${RED}✗ List voices failed or no voices available${NC}"
    echo "$response"
fi
echo ""

# Summary
echo "=================================="
echo "Test Summary"
echo "=================================="
echo "All basic tests completed!"
echo ""
echo "Next steps:"
echo "1. Check GPU usage: ./scripts/gpu-monitor.sh"
echo "2. View API docs: $BASE_URL/docs"
echo "3. Monitor logs: docker-compose logs -f api-server"
echo ""
