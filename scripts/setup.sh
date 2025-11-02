#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== LLM Server Quick Setup ===${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "✓ Created .env file\n"
else
    echo -e "${GREEN}.env file already exists${NC}\n"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${BLUE}Starting services with Docker Compose...${NC}"
docker-compose up -d

echo -e "\n${GREEN}Waiting for Ollama to start...${NC}"
sleep 5

echo -e "\n${GREEN}Pulling default model (phi3:mini)...${NC}"
docker exec llm-ollama ollama pull phi3:mini

echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
echo -e "\nServices:"
echo -e "  • API Server: ${BLUE}http://localhost:8000${NC}"
echo -e "  • API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  • Ollama: ${BLUE}http://localhost:11434${NC}"
echo -e "\nTo view logs:"
echo -e "  ${BLUE}docker-compose logs -f${NC}"
echo -e "\nTo stop services:"
echo -e "  ${BLUE}docker-compose down${NC}"
echo -e "\nTo pull more models:"
echo -e "  ${BLUE}docker exec llm-ollama ollama pull <model-name>${NC}"
echo -e "\nAvailable models for your GPU (GTX 1050 Ti 4GB):"
echo -e "  • phi3:mini (3.8B) - Recommended"
echo -e "  • llama3.2:1b (1B) - Very fast"
echo -e "  • qwen2.5:1.5b (1.5B) - Good balance"
echo -e "  • gemma:2b (2B) - Compact"
