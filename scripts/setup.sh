#!/bin/bash
# Setup script for GDPR RAG system

set -e

echo "=================================="
echo "GDPR RAG System Setup"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8+ required. Found: $python_version"
    exit 1
fi
echo "Python version OK: $python_version"

# Check if Ollama is installed
echo ""
echo "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Please install from https://ollama.ai/"
    echo "After installation, run: ollama pull llama2"
    exit 1
fi
echo "Ollama found"

# Check if Ollama is running
echo "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Ollama is not running. Starting Ollama..."
    echo "Please run 'ollama serve' in another terminal"
    exit 1
fi
echo "Ollama is running"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Build the database:"
echo "   python main.py setup"
echo ""
echo "3. Start using the system:"
echo "   python main.py interactive"
echo ""
echo "Or run examples:"
echo "   python examples.py"
echo ""
