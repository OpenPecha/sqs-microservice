.PHONY: help build up down logs restart clean test shell health

# Default target
help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start services"
	@echo "  make down     - Stop services"
	@echo "  make logs     - View logs"
	@echo "  make restart  - Restart services"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make shell    - Open shell in web container"
	@echo "  make health   - Check service health"
	@echo "  make test     - Run tests (if available)"

# Build Docker images
build:
	@echo "🏗️  Building Docker images..."
	docker-compose build

# Start services
up:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "🌐 Application: http://localhost:8080"
	@echo "📊 Health check: http://localhost:8080/health"

# Start services with logs
up-logs:
	@echo "🚀 Starting services with logs..."
	docker-compose up

# Stop services
down:
	@echo "🛑 Stopping services..."
	docker-compose down

# View logs
logs:
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	docker-compose logs -f web

# Restart services
restart: down up
	@echo "🔄 Services restarted"

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers, images, and volumes..."
	docker-compose down -v --rmi local
	@echo "✅ Cleanup complete"

# Open shell in web container
shell:
	@echo "🐚 Opening shell in web container..."
	docker-compose exec web /bin/bash

# Check service health
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8080/health || echo "❌ Service is not healthy"

# Run tests (placeholder - add your test command)
test:
	@echo "🧪 Running tests..."
	@echo "⚠️  No tests configured yet"

# Development: Build and start with logs
dev: build up-logs

# Production: Build and start in background
prod: build up
	@echo "🎉 Production deployment complete!"
	@echo "Monitor logs with: make logs"

# Check Docker and docker-compose installation
check:
	@echo "🔍 Checking dependencies..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "❌ docker-compose is not installed"; exit 1; }
	@echo "✅ All dependencies are installed"

# Initialize .env file
init:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env from env.example..."; \
		cp env.example .env; \
		echo "✅ .env file created"; \
		echo "⚠️  Please edit .env with your credentials"; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi

# Full setup: check dependencies, init env, build, and start
setup: check init build up
	@echo "🎉 Setup complete!"

