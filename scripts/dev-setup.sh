#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Local Development Setup ===${NC}\n"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}Creating virtual environment...${NC}"
python3 -m venv venv

echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cp .env.example .env
fi

echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
echo -e "\nMake sure Ollama is running, then start the server:"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "  ${BLUE}python main.py${NC}"
echo -e "\nOr with auto-reload:"
echo -e "  ${BLUE}uvicorn app.main:app --reload${NC}"
