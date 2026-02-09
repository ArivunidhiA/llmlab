#!/bin/bash

# LLMLab Backend Startup Script

echo "🚀 LLMLab Backend Startup"
echo "========================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✏️  Please update .env with your configuration"
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --break-system-packages -q

# Run tests (optional)
read -p "Run tests before starting? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
fi

# Start server
echo "✅ Starting server..."
python main.py
