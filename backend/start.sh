#!/bin/bash

echo "🚀 Starting Chatbot API with Redis History..."
echo "📍 Make sure you have:"
echo "   1. Created .env file with your GROQ_API_KEY"
echo "   2. Installed dependencies: pip install -r requirements.txt"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Copy .env.example to .env and add your GROQ_API_KEY"
    echo ""
fi

# Start the server
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo "🔍 Debug endpoints:"
echo "   - Redis status: http://localhost:8000/api/debug/redis"
echo "   - Active sessions: http://localhost:8000/api/debug/sessions"
echo ""

python main.py
