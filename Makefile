.PHONY: help install dev test lint format clean docker-build docker-up

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies using UV"
	@echo "  dev         - Start development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linters"
	@echo "  format      - Format code"
	@echo "  clean       - Clean temporary files"
	@echo "  db-setup    - Setup database"
	@echo "  db-create   - Create database tables"
	@echo "  db-drop     - Drop database tables"
	@echo "  db-seed     - Seed database with initial data"
	@echo "  db-reset    - Reset database (drop and recreate)"
	@echo "  docker-up   - Start docker services"
	@echo "  api         - Start FastAPI server"
	@echo "  docs        - Build documentation"
	@echo "  docs-serve  - Serve documentation locally"

# Environment setup
install:
	@echo "📦 Installing dependencies with UV..."
	uv pip install -e ".[dev]"
	pre-commit install

install-prod:
	@echo "🏭 Installing production dependencies..."
	uv pip install -e ".[prod]"

# Development
dev:
	@echo "🚀 Starting development server..."
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8005

dev-worker:
	@echo "👷 Starting Celery worker..."
	uv run celery -A src.tasks.celery worker --loglevel=info

dev-flower:
	@echo "🌸 Starting Flower (Celery monitor)..."
	uv run celery -A src.tasks.celery flower

# API
api:
	@echo "📡 Starting FastAPI server..."
	@echo "Activating virtual environment and starting server..."
	bash -c "source .venv/bin/activate && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8005"

# Testing
test:
	@echo "🧪 Running tests..."
	pytest

test-cov:
	@echo "📊 Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term

test-integration:
	@echo "🔗 Running integration tests..."
	pytest tests/integration -v

# Code quality
lint:
	@echo "🔍 Running linters..."
	flake8 src tests
	mypy src
	black --check src tests
	isort --check-only src tests

format:
	@echo "🎨 Formatting code..."
	black src tests
	isort src tests

# Database
db-setup:
	@echo "🗄️ Setting up database..."
	python scripts/database/migrate.py create
	python scripts/database/migrate.py seed

db-create:
	@echo "🗄️ Creating database tables..."
	python scripts/database/migrate.py create

db-drop:
	@echo "💣 Dropping database tables..."
	python scripts/database/migrate.py drop

db-seed:
	@echo "🌱 Seeding database with initial data..."
	python scripts/database/migrate.py seed

db-reset:
	@echo "🔄 Resetting database..."
	python scripts/database/migrate.py reset

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🚀 Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# Pipeline commands
pipeline-start:
	@echo "⚡ Starting data pipeline..."
	python -m src.pipelines.main start

pipeline-stop:
	@echo "🛑 Stopping data pipeline..."
	python -m src.pipelines.main stop

pipeline-status:
	@echo "📊 Pipeline status..."
	python -m src.pipelines.main status

# Monitoring
dashboard:
	@echo "📊 Opening monitoring dashboard..."
	open http://localhost:3000

logs:
	@echo "📋 Showing application logs..."
	tail -f logs/app.log

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +

# Documentation
docs:
	@echo "📚 Building documentation..."
	cd docs && sphinx-build -b html . _build/html

docs-serve:
	@echo "🌐 Serving documentation..."
	python serve_docs.py

docs-rebuild:
	@echo "🔄 Rebuilding and serving documentation..."
	make docs && python serve_docs.py

# Thai language setup
thai-setup:
	@echo "🇹🇭 Setting up Thai language resources..."
	python -c "import pythainlp; pythainlp.corpus.download('thai2fit_wv')"
	python -c "import pythainlp; pythainlp.corpus.download('thai2vec')"
	python -m spacy download th_core_news_sm || echo "Thai model not available"