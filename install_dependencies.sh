#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}=== TollEasy Backend Dependencies Setup ===${NC}"
echo -e "${GREEN}=============================================${NC}"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}Python is installed.${NC}"
    python3 --version
else
    echo -e "${RED}Python is not installed. Please install Python 3.8 or later.${NC}"
    exit 1
fi

# Check if a virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Make sure python3-venv is installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
else
    echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Activate the virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies.${NC}"
    echo -e "${YELLOW}Trying to install with specific versions...${NC}"
    
    # Additional fallback installations
    pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart python-dotenv email-validator googlemaps requests
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies with fallback method.${NC}"
        exit 1
    else
        echo -e "${GREEN}Dependencies installed successfully with fallback method.${NC}"
    fi
else
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
fi

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo -e "${GREEN}=============================================${NC}"
echo -e "${YELLOW}To activate the virtual environment, run:${NC}"
echo -e "${GREEN}source .venv/bin/activate${NC}"
echo -e "${YELLOW}To start the server, run:${NC}"
echo -e "${GREEN}./run.sh${NC}" 