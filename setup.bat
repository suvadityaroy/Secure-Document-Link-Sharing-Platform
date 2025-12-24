@echo off
REM Setup script for Windows

echo.
echo 🚀 Setting up Secure Document ^& Link Sharing Platform...
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop.
    exit /b 1
)

REM Create .env from .env.example
if not exist .env (
    echo 📝 Creating .env file from .env.example...
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration
)

REM Start services
echo.
echo 🐳 Starting Docker containers...
docker-compose up -d

REM Wait for services
echo.
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak

REM Check health
echo.
echo 🏥 Checking service health...
docker-compose ps

echo.
echo ✅ Setup complete!
echo.
echo 📍 Access the services:
echo   - API Documentation: http://localhost:8000/docs
echo   - API Root: http://localhost:8000
echo   - File Service Health: http://localhost:8081/api/files/health
echo   - Database: localhost:5432 (user: user, password: password)
echo   - Redis: localhost:6379
echo.
echo 📚 Next steps:
echo   - Read README.md for API documentation
echo   - Register a user: POST /api/auth/register
echo   - Login: POST /api/auth/login
echo   - Upload file: POST /api/files/upload
echo.
echo To view logs: docker-compose logs -f [service_name]
echo To stop services: docker-compose down
