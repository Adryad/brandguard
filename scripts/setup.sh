#!/bin/bash
# brandguard/scripts/setup.sh

echo "🚀 Setting up BrandGuard Development Environment..."

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

echo "✅ All prerequisites met!"

# Setup backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Setup frontend
echo "Setting up frontend..."
cd ../frontend
npm install

# Copy environment file
cd ..
cp .env.example .env

# Build and start services
echo "Building and starting services..."
docker-compose up -d

echo "✅ Setup complete!"
echo ""
echo "Services are now running:"
echo "• Backend API: http://localhost:8000"
echo "• Frontend: http://localhost:3000"
echo "• PostgreSQL: localhost:5432"
echo "• Redis: localhost:6379"
echo "• Elasticsearch: http://localhost:9200"
echo ""
echo "Run 'docker-compose logs -f' to view logs"