#!/bin/bash

# Frontend Build Script for Production
echo "🚀 Building React Frontend for Production..."

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend" || exit 1

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Create production environment file if it doesn't exist
if [ ! -f ".env.production" ]; then
    echo "⚠️  Creating .env.production from example..."
    cp ../deployment/frontend-production.env.example .env.production
    echo "⚙️  Please edit frontend/.env.production with your actual EC2 IP/domain"
fi

# Build the React app
echo "🔨 Building React application..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build completed successfully!"
    echo "📁 Built files are in: frontend/build/"
    echo ""
    echo "📋 Next steps:"
    echo "1. Copy the build/ folder to your EC2 instance"
    echo "2. Configure Nginx to serve the static files"
    echo "3. Update .env.production with your actual EC2 IP"
else
    echo "❌ Frontend build failed!"
    exit 1
fi
