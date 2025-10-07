#!/bin/bash

# SNI Laptops Backend Startup Script

echo "🚀 Starting SNI Laptops Backend API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please update .env file with your SendGrid API key and other settings."
    echo "   Edit .env file and then run this script again."
    exit 1
fi

# Start the application
echo "🌟 Starting Flask application..."
python app.py
