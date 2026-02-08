#!/bin/bash

# LinkedIn Resume Verification API - Local Development Startup Script

echo "=================================================="
echo "LinkedIn Resume Verification API - Setup"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_md

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ Warning: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env and add your GROQ_API_KEY"
    echo ""
fi

# Check if session.json exists
if [ ! -f "session.json" ]; then
    echo ""
    echo "⚠ Warning: session.json not found!"
    echo "LinkedIn scraping will not work without it."
    echo "You can copy session.json.example and add your LinkedIn session."
    echo ""
fi

echo ""
echo "=================================================="
echo "Setup complete!"
echo "=================================================="
echo ""
echo "To start the development server:"
echo "  python app.py"
echo ""
echo "To start with gunicorn (production-like):"
echo "  gunicorn app:app --bind 0.0.0.0:5000 --reload"
echo ""
echo "To run tests:"
echo "  python test_api_local.py"
echo ""
echo "API will be available at: http://localhost:5000"
echo "Health check: http://localhost:5000/health"
echo ""
