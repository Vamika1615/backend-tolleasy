#!/bin/bash

# Ensure we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Running install_dependencies.sh first..."
    ./install_dependencies.sh
fi

# Start the FastAPI server
echo "Starting TollEasy API server..."
uvicorn main:app --reload 