#!/bin/bash

# AI Research Assistant - Development Environment Setup
# This script sets up the development environment with live reloading

set -e

echo "🔧 Setting up AI Research Assistant Development Environment..."

# Create data directory if it doesn't exist
mkdir -p ./data

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build images
echo "🔨 Building Docker images..."
docker-compose build

# Start services in development mode
echo "🚀 Starting services in development mode..."
docker-compose up

echo ""
echo "ℹ️  Development mode includes:"
echo "   • Live reloading for both frontend and backend"
echo "   • Volume mounts for instant code changes"
echo "   • PostgreSQL with persistent data"
echo "   • Redis disabled (using PostgreSQL directly)"
echo ""
