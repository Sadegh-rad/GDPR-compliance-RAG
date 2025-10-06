#!/bin/bash

# GDPR Compliance Dashboard - Startup Script
# This script starts the Flask web server

echo "=================================="
echo "GDPR Compliance Dashboard"
echo "=================================="
echo ""

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    echo "Please run this script from the web_ui directory:"
    echo "  cd web_ui"
    echo "  ./start.sh"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "../venv" ] && [ ! -d "venv" ]; then
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
if [ -d "../venv" ]; then
    echo "🔧 Activating virtual environment (parent directory)..."
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if ! ollama list &> /dev/null; then
    echo "⚠️  Ollama not found or not running"
    echo "   Please install Ollama: https://ollama.ai"
else
    echo "✅ Ollama is running"
fi
echo ""

# Check if FAISS index exists
if [ -f "../vectorstore/gdpr_faiss_index.faiss" ]; then
    echo "✅ FAISS index found"
else
    echo "⚠️  FAISS index not found at ../vectorstore/"
    echo "   Please build the index first:"
    echo "   python scripts/build_index.py"
fi
echo ""

# Start Flask server
echo "=================================="
echo "🚀 Starting Flask server..."
echo "=================================="
echo ""
echo "📱 Dashboard will be available at:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
