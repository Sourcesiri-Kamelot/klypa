#!/bin/bash

# Klypa Getting Started Script
# This script helps you set up Klypa quickly

set -e

echo "========================================="
echo "   Klypa Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "✗ requirements.txt not found. Please run this script from the klypa directory."
    exit 1
fi

# Check for FFmpeg
echo ""
echo "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg found"
else
    echo "⚠ FFmpeg not found. Some features may not work."
    echo "  Install FFmpeg:"
    echo "    Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "    macOS: brew install ffmpeg"
    echo "    Windows: Download from https://ffmpeg.org"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate || . venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies (this may take a while)..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Install package
echo ""
echo "Installing Klypa package..."
pip install -e . --quiet
echo "✓ Klypa installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p uploads output temp
echo "✓ Directories created"

# Copy .env.example to .env if not exists
echo ""
echo "Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from .env.example"
    echo "  Please edit .env to configure your settings"
else
    echo "✓ .env file already exists"
fi

# Check for Ollama
echo ""
echo "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found"
    echo "  Start Ollama with: ollama serve"
    echo "  Pull a model with: ollama pull llama2"
else
    echo "⚠ Ollama not found (optional for AI features)"
    echo "  Install from: https://ollama.ai"
fi

# Summary
echo ""
echo "========================================="
echo "   Setup Complete! 🎉"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your settings:"
echo "   Edit .env file with your preferences"
echo ""
echo "2. Start the Streamlit dashboard:"
echo "   streamlit run src/app.py"
echo ""
echo "3. Or run an example:"
echo "   python examples/basic_processing.py"
echo ""
echo "4. Or use Docker:"
echo "   docker-compose up --build"
echo ""
echo "Documentation:"
echo "  - Quick Start: QUICKSTART.md"
echo "  - API Reference: API.md"
echo "  - Deployment: DEPLOYMENT.md"
echo ""
echo "Need help? Visit: https://github.com/Sourcesiri-Kamelot/klypa"
echo ""
