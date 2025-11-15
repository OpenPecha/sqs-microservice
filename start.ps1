# Quick Start Script for Celery Microservice (Windows PowerShell)
# This script helps you get the application up and running quickly

$ErrorActionPreference = "Stop"

Write-Host "🚀 Celery Microservice - Quick Start" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "📝 Creating .env from env.example..." -ForegroundColor Yellow
    Copy-Item env.example .env
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env file with your actual credentials before continuing!" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue after editing .env"
}

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop for Windows first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ docker-compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ docker-compose is not installed. Please install docker-compose first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host "1) Build and start the application"
Write-Host "2) Stop the application"
Write-Host "3) View logs"
Write-Host "4) Rebuild from scratch"
Write-Host "5) Exit"
Write-Host ""
$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🏗️  Building and starting the application..." -ForegroundColor Cyan
        docker-compose up --build -d
        Write-Host ""
        Write-Host "✅ Application started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Service Status:" -ForegroundColor Cyan
        docker-compose ps
        Write-Host ""
        Write-Host "🌐 Application is running at: http://localhost:8080" -ForegroundColor Green
        Write-Host "📊 Health check: http://localhost:8080/health" -ForegroundColor Green
        Write-Host ""
        Write-Host "To view logs, run: docker-compose logs -f web" -ForegroundColor Yellow
    }
    "2" {
        Write-Host ""
        Write-Host "🛑 Stopping the application..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "✅ Application stopped" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "📋 Viewing logs (Press Ctrl+C to exit)..." -ForegroundColor Cyan
        docker-compose logs -f web
    }
    "4" {
        Write-Host ""
        Write-Host "🔄 Rebuilding from scratch..." -ForegroundColor Cyan
        docker-compose down -v
        docker-compose build --no-cache
        docker-compose up -d
        Write-Host ""
        Write-Host "✅ Application rebuilt and started!" -ForegroundColor Green
        Write-Host "🌐 Application is running at: http://localhost:8080" -ForegroundColor Green
    }
    "5" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
        exit 1
    }
}

