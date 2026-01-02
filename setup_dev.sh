#!/bin/bash
set -e

echo "🚀 Starting Parallax AI Development Setup..."

# 1. Environment Variables
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please update it with your secrets if necessary."
else
    echo "ℹ️  .env file already exists. Skipping creation."
fi

# 2. Backend Setup (Python)
echo "------------------------------------------------"
echo "🐍 Setting up Backend (Python)..."
cd backend

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Create Virtual Environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "ℹ️  Virtual environment already exists."
fi

# Activate and Install Dependencies
echo "⬇️  Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend dependencies installed."
cd ..

# 3. Frontend Setup (Node.js)
echo "------------------------------------------------"
echo "⚛️  Setting up Frontend (Next.js)..."
cd frontend

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm could not be found. Please install Node.js."
    exit 1
fi

echo "⬇️  Installing Node.js dependencies..."
npm install
echo "✅ Frontend dependencies installed."
cd ..

# 4. Final Instructions
echo "------------------------------------------------"
echo "🎉 Setup Complete!"
echo ""
echo "To start the application with Docker (Recommended):"
echo "  docker-compose up --build"
echo ""
echo "To run services individually (for debugging):"
echo "  Backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
