#!/bin/bash
# Simple Setup Script for GDPR Compliance Assistant

echo "🛡️  GDPR Compliance Assistant - Setup"
echo "====================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi
echo "✓ Python 3 found"

# Check Ollama
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "❌ Ollama is not running on localhost:11434"
    echo "   Install from: https://ollama.ai"
    echo "   Then run: ollama serve"
    exit 1
fi
echo "✓ Ollama is running"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate and install dependencies
echo ""
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p data/raw data/processed vectorstore logs
echo "✓ Directories created"

# Build database
echo ""
echo "Would you like to build the GDPR database now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Building GDPR database (this takes 2-3 minutes)..."
    python main.py collect --sources eur-lex --languages EN
    python main.py process
    python main.py build
    echo ""
    echo "✓ Database built successfully!"
fi

echo ""
echo "====================================="
echo "✅ Setup Complete!"
echo "====================================="
echo ""
echo "Try it now:"
echo "  python main.py query --query 'What are data subject rights?'"
echo "  python main.py interactive"
echo ""
echo "Need help? Check README.md"
echo ""
