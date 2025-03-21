#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Installing dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install fastapi==0.104.1
pip install uvicorn==0.34.0
pip install sqlalchemy==2.0.31
pip install pydantic==2.10.6
pip install pydantic-core==2.27.2
pip install pydantic-extra-types==2.1.0
pip install pydantic-settings==2.1.0
pip install python-jose==3.3.0
pip install passlib==1.7.4
pip install bcrypt==4.0.1
pip install python-multipart==0.0.6
pip install email-validator==2.1.0.post1
pip install python-dotenv==1.0.1
pip install pytz==2023.3

echo "Dependencies installed successfully."
echo "Activate the virtual environment with: source .venv/bin/activate" 