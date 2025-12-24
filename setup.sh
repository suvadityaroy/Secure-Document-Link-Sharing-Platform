#!/bin/bash
# Setup script for local development

set -e

echo "🚀 Setting up Secure Document & Link Sharing Platform..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access the services:"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - API Root: http://localhost:8000"
echo "  - File Service Health: http://localhost:8081/api/files/health"
echo "  - Database: localhost:5432 (user: user, password: password)"
echo "  - Redis: localhost:6379"
echo ""
echo "📚 Next steps:"
echo "  - Read README.md for API documentation"
echo "  - Register a user: POST /api/auth/register"
echo "  - Login: POST /api/auth/login"
echo "  - Upload file: POST /api/files/upload"
echo ""
echo "To view logs: docker-compose logs -f [service_name]"
echo "To stop services: docker-compose down"
