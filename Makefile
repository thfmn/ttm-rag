.PHONY: help install dev test lint format clean docker-build docker-up

# Default target
help:
	@echo "Available commands:"
	@echo "  install          - Install dependencies using UV"
	@echo "  install-prod     - Install production dependencies using UV"
	@echo "  env              - Create .env from .env.example if missing"
	@echo "  dev              - Start development API server (FastAPI, reload) :8005"
	@echo "  api              - Start API server (same as dev, explicit target)"
	@echo "  test             - Run tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-cov         - Run tests with coverage"
	@echo "  lint             - Run linters"
	@echo "  format           - Format code"
	@echo "  clean            - Clean temporary files"
	@echo "  db-setup         - Setup database (create + seed)"
	@echo "  db-create        - Create database tables"
	@echo "  db-drop          - Drop database tables"
	@echo "  db-seed          - Seed database with initial data"
	@echo "  db-reset         - Reset database (drop and recreate)"
	@echo "  docker-up        - Start docker services"
	@echo "  docker-down      - Stop docker services"
	@echo "  docs             - Build documentation"
	@echo "  docs-serve       - Serve documentation locally on :8081"
	@echo "  dagster-dev      - Run Dagster dev server (assets) on :3000"
	@echo "  openwebui-dev    - Run Open WebUI backend locally on :8080"
	@echo "  openwebui-docker - Run Open WebUI via docker compose"
	@echo "  rag-test         - Minimal end-to-end RAG smoke test against API"

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
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8005

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

docs-live:
	@echo "👀 Live-reloading docs (sphinx-autobuild)..."
	uv run sphinx-autobuild -b html docs docs/_build/html

# Dagster (orchestration)
dagster-dev:
	@echo "🛠️ Starting Dagster dev (port 3000)..."
	@echo "Tip: Install Dagster first with: uv pip install \"dagster>=1.7\" \"dagster-webserver>=1.7\""
	@echo "Open: http://localhost:3000"
	@uv run dagster dev -m src.orchestration.dagster_defs

# Environment convenience
env:
	@echo "🔧 Ensuring .env exists..."
	@if [ ! -f .env ]; then cp .env.example .env && echo '.env created from .env.example'; else echo '.env already exists'; fi
	@echo "Open and edit .env to set API keys and DB settings."

# Open WebUI (local dev, backend served on :8080)
openwebui-dev:
	@echo "🖥️ Starting Open WebUI backend (port 8080)..."
	@echo "Tip: Ensure API is running at http://localhost:8005 and CORS allows this origin."
	@echo "Open: http://localhost:8080"
	@cd open-webui/backend && PORT=8080 HOST=0.0.0.0 CORS_ALLOW_ORIGIN='http://localhost:8080;http://localhost:5173;http://localhost:8005' bash ./start.sh

# Open WebUI via Docker compose in subproject
openwebui-docker:
	@echo "🐳 Starting Open WebUI via docker compose..."
	@$(MAKE) -C open-webui install

# Minimal end-to-end RAG smoke test (requires API running on :8005)
rag-test:
	@echo "🧪 RAG smoke test: add doc and query"
	@echo "1) Adding a sample document..."
	@curl -s -X POST "http://localhost:8005/api/v1/rag/documents" -H "Content-Type: application/json" -d '{"id":"doc-smoke","content":"Thai traditional medicine sample text about Plai.","metadata":{"source":"manual","year":2024}}' | jq '.status' || true
	@sleep 1
	@echo "2) Querying the system..."
	@curl -s -X POST "http://localhost:8005/api/v1/rag/query" -H "Content-Type: application/json" -d '{"query":"What is Plai?", "top_k": 3}' | jq '{status, num_results, sources}' || true

# Thai language setup
thai-setup:
	@echo "🇹🇭 Setting up Thai language resources..."
	python -c "import pythainlp; pythainlp.corpus.download('thai2fit_wv')"
	python -m spacy download th_core_news_sm || echo "Thai model not available"
