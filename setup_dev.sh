#!/bin/bash
set -e

echo "🚀 Starting Parallax AI Development Setup..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker could not be found. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose could not be found. Please install Docker Compose."
    exit 1
fi

# 1. Environment Variables
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please update it with your secrets if necessary."
else
    echo "ℹ️  .env file already exists. Skipping creation."
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# 2. Python Virtual Environment (Project Root)
echo "------------------------------------------------"
echo "🐍 Setting up Python Virtual Environment..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Create Virtual Environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment (venv)..."
    python3 -m venv venv
else
    echo "ℹ️  Virtual environment already exists."
fi

# Activate and Install Dependencies
echo "⬇️  Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install development dependencies (invoke, etc.)
echo "Installing development tools (invoke, etc.)..."
pip install -r requirements-dev.txt

echo "✅ Python dependencies installed."

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

# 4. Initialize Database
echo "------------------------------------------------"
echo "🗄️  Initializing Database..."
echo "Starting PostgreSQL container..."

# Start only postgres to initialize the database
if docker compose version &> /dev/null; then
    docker compose up -d postgres
else
    docker-compose up -d postgres
fi

echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Check if postgres is ready
until docker exec $(docker ps -qf "name=postgres") pg_isready -U parallax &> /dev/null; do
    echo "Waiting for database to be ready..."
    sleep 2
done

echo "✅ Database initialized."

# 5. Final Instructions
echo "------------------------------------------------"
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "  2. Activate venv: source venv/bin/activate"
echo "  3. Generate secrets: inv dev.secrets --update-env"
echo "  4. Verify setup: inv dev.check"
echo ""
echo "Using invoke commands (with venv activated):"
echo "  source venv/bin/activate"
echo "  inv --list           # List all commands"
echo "  inv docker.up        # Start services"
echo "  inv db.status        # Check database"
echo "  inv docker.logs      # View logs"
echo ""
echo "Traditional Docker commands still work:"
if docker compose version &> /dev/null; then
    echo "  docker compose up --build"
else
    echo "  docker-compose up --build"
fi
echo ""
echo "See docs/DEVELOPER_COMMANDS.md for complete command reference."
echo ""
