# ESG Sentiment Scorer - Makefile
.PHONY: help install dev clean test lint format docker-build docker-run setup

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup          - Initial project setup"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Setup development environment"  
	@echo "  make run-api        - Run FastAPI server"
	@echo "  make run-dashboard  - Run Streamlit dashboard"
	@echo "  make run-jupyter    - Run Jupyter lab"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run with Docker Compose"
	@echo "  make docker-stop    - Stop Docker services"
	@echo "  make clean          - Clean up temporary files"

# Project setup
setup: install
	@echo "Setting up ESG Sentiment Scorer project..."
	cp .env.example .env
	@echo "⚠️  Please edit .env file with your API keys"
	@echo "✅ Project setup complete!"

# Install dependencies
install:
	@echo "Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Development environment setup
dev: install
	@echo "Setting up development environment..."
	pip install -e .
	pre-commit install || echo "pre-commit not available"
	@echo "✅ Development environment ready!"

# Run FastAPI server
run-api:
	@echo "🚀 Starting FastAPI server..."
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run Streamlit dashboard
run-dashboard:
	@echo "📊 Starting Streamlit dashboard..."
	streamlit run src/dashboard/app.py --server.address 0.0.0.0 --server.port 8501

# Run Jupyter Lab
run-jupyter:
	@echo "📓 Starting Jupyter Lab..."
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v --cov=src --cov-report=html
	@echo "✅ Tests completed!"

# Lint code
lint:
	@echo "🔍 Running code linting..."
	flake8 src/ tests/
	mypy src/ || echo "Type checking completed with warnings"
	@echo "✅ Linting completed!"

# Format code
format:
	@echo "🎨 Formatting code..."
	black src/ tests/
	@echo "✅ Code formatted!"

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t esg-sentiment-scorer .
	@echo "✅ Docker image built!"

docker-run:
	@echo "🐳 Starting services with Docker Compose..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "🌐 API: http://localhost:8000"
	@echo "📊 Dashboard: http://localhost:8501"
	@echo "📓 Jupyter: http://localhost:8888"

docker-stop:
	@echo "🛑 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped!"

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	@echo "✅ Cleanup completed!"

# Database setup (if using PostgreSQL locally)
db-setup:
	@echo "🗄️ Setting up database..."
	createdb esg_sentiment_db || echo "Database may already exist"
	@echo "✅ Database setup completed!"

# Quick start for development
quickstart: setup run-api

# Full development environment
dev-full: setup
	@echo "🚀 Starting full development environment..."
	@echo "Starting in tmux sessions..."
	tmux new-session -d -s esg-api 'make run-api' || echo "tmux not available, run manually"
	tmux new-session -d -s esg-dashboard 'make run-dashboard' || echo "tmux not available, run manually"
	tmux new-session -d -s esg-jupyter 'make run-jupyter' || echo "tmux not available, run manually"
	@echo "✅ Development environment started!"
	@echo "📋 Use 'tmux list-sessions' to see running sessions"

# Show project status
status:
	@echo "📊 ESG Sentiment Scorer Project Status"
	@echo "======================================="
	@echo "Python version: $(shell python --version)"
	@echo "Pip packages: $(shell pip list | wc -l) installed"
	@echo "Project size: $(shell du -sh . | cut -f1)"
	@echo "Git status: $(shell git status --porcelain | wc -l) files changed"
	@echo "Last commit: $(shell git log -1 --pretty=format:'%h - %s (%cr)')"
