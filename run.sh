#!/bin/bash

# Create a Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/Scripts/activate

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start uvicorn in the background
echo "Starting backend..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "Backend running at http://localhost:8000 (PID: $BACKEND_PID)"
echo "Open frontend/index.html in browser"

# Optional: Add a cleanup trap for when the script exits
# trap "kill $BACKEND_PID" EXIT
