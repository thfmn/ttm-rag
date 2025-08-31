# Thai Traditional Medicine RAG Bot

## Project Documentation and Status
- Authoritative status & roadmap: docs/explanations/project_lifecycle.md
- Diátaxis navigation:
  - Tutorials: docs/tutorials/index.md
  - How-to: docs/how-to/index.md
  - Reference: docs/reference/index.md
  - Explanations: docs/explanations/index.md
  - Policy: docs/explanations/context7_docs_policy.md
  - Docs refresh plan: docs/explanations/docs_refresh_plan.md
- Build/serve docs (uv policy; run manually):
  - uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild
  - uv run sphinx-build -b html docs docs/_build/html
  - uv run sphinx-autobuild -b html docs docs/_build/html

## Fool-Proof Development & Testing Setup Guide

This guide provides step-by-step instructions for setting up a development environment for the Thai Traditional Medicine RAG Bot project. Follow these steps in order for a smooth setup experience.

## Prerequisites

Before starting, ensure you have:
- Python 3.11 or higher
- Git
- Docker (optional, for containerized database)
- curl (for downloading UV package manager)

## Quick Start (Recommended for Beginners)

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd thai-traditional-medicine-rag-bot
```

### Step 2: Run Automated Setup Script
```bash
# Make the setup script executable
chmod +x scripts/setup/install.sh

# Run the automated setup
./scripts/setup/install.sh
```

### Step 3: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
# For development, the defaults should work fine
nano .env  # or use your preferred editor
```

### Step 4: Set Up Database
```bash
# Create database tables and seed with initial data
make db-setup
```

### Step 5: Install Thai Language Resources
```bash
# Install Thai language processing resources
make thai-setup
```

### Step 6: Run Tests
```bash
# Verify everything is working
make test
```

### Step 7: Start Development Server
```bash
# Start the development server
make dev
```

The API will be available at `http://localhost:8005`.

### Starting the webservers (API, Docs, Open WebUI)

All commands are executed manually by you (uv policy). From the repo root:

1) API (FastAPI)
- Purpose: backend REST and RAG endpoints
- Command: make dev
- URL: http://localhost:8005

2) Documentation (Sphinx)
- Purpose: local docs site
- Command: make docs-serve
- URL: http://localhost:8081

3) Open WebUI (backend)
- Purpose: chat UI that integrates with our TTM RAG endpoints and your model connections
- Prepare env (once): cp open-webui/.env.example.override open-webui/.env and edit keys as needed
- Command: make openwebui-dev
- URL: http://localhost:8080

Model visibility in Open WebUI:
- At least one connection must be configured in Admin > Connections (e.g., OpenAI with OPENAI_API_KEY, or Ollama at http://localhost:11434 with a pulled model).
- The custom TTM dropdown calls:
  - GET /api/v1/ttm_rag/models to list adapters (Typhoon HF, OpenAI, Qwen)
  - POST /api/v1/ttm_rag/ with {"query": "...", "model": "adapter-id"} to run a RAG query via the chosen adapter
- If the dropdown shows “No results found”, open browser devtools and check the request to /api/v1/ttm_rag/models; fix any CORS or auth issues (see open-webui/.env).

## Manual Setup (For Advanced Users)

If you prefer to set up the environment manually:

### Step 1: Install UV Package Manager
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment with Python 3.13
uv venv --python 3.13

# Activate virtual environment
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install project dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Step 4: Configure Environment
```bash
# Create .env file from example
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

### Step 5: Set Up Database
```bash
# Create database tables
make db-create

# Seed database with initial data
make db-seed
```

### Step 6: Install Thai Language Resources
```bash
# Install Thai language processing resources
make thai-setup
```

### Step 7: Verify Setup
```bash
# Run tests to verify everything works
make test

# Start development server
make dev
```

## Docker-Based Database Setup (Alternative)

For users who prefer to use Docker for the database:

### Step 1: Start Database Container
```bash
# Start only the database service
docker-compose up -d db
```

### Step 2: Wait for Database to Initialize
```bash
# Wait about 15-30 seconds for the database to be ready
sleep 30
```

### Step 3: Update Environment Variables
```bash
# Edit .env file to use PostgreSQL
nano .env

# Set DATABASE_URL to:
# DATABASE_URL=postgresql://user:password@localhost:5432/thai_medicine_db
```

### Step 4: Initialize Database
```bash
# Create database tables and seed with initial data
make db-setup
```

### Step 5: Continue with Setup
```bash
# Install Thai language resources
make thai-setup

# Run tests
make test

# Start development server
make dev
```

## Development Workflow Commands

Once your environment is set up, use these commands for development:

```bash
# Start development server with auto-reload
make dev

# Run all tests
make test

# Run tests with coverage report
make test-cov

# Run linters
make lint

# Format code
make format

# Reset database (drops and recreates)
make db-reset

# View application logs
make logs

# Clean temporary files
make clean
```

## Documentation

### View Documentation Locally
```bash
# Build and serve documentation
make docs-serve
```

Then open your browser to `http://localhost:8081`

### Rebuild Documentation
```bash
# Rebuild documentation after making changes
make docs-rebuild
```

## Project Structure Overview

```
thai-traditional-medicine-rag-bot/
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   ├── connectors/        # Data source connectors
│   ├── database/          # Database models and utilities
│   ├── models/            # Pydantic data models
│   ├── pipelines/         # Data processing pipelines
│   ├── utils/            # Utility functions
│   └── validators/        # Data validators
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
├── scripts/               # Setup and utility scripts
├── config/                # Configuration files
└── requirements/         # Dependency requirements
```

## Common Issues and Solutions

### Issue: Port Already in Use
If you see "Address already in use" errors:
```bash
# Kill processes using the port
lsof -i :8005 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Issue: Database Connection Errors
If you have database connection issues:
```bash
# Reset the database
make db-reset

# Or drop and recreate manually
make db-drop
make db-create
make db-seed
```

### Issue: Missing Thai Language Resources
If Thai language processing fails:
```bash
# Reinstall Thai language resources
make thai-setup
```

### Issue: Dependency Installation Failures
If dependencies fail to install:
```bash
# Upgrade UV
pip install --upgrade uv

# Reinstall dependencies
uv pip install -e ".[dev]"
```

## Useful Development Tools

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
```bash
# Run pre-commit checks manually
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

### Database Inspection
To inspect the database directly:
```bash
# For SQLite (development default)
sqlite3 thai_medicine.db

# For PostgreSQL (with Docker)
docker-compose exec db psql -U user -d thai_medicine_db
```

## Next Steps

After setting up your development environment:

1. **Explore the Codebase**: Familiarize yourself with the project structure
2. **Run the Tests**: Ensure all tests pass (`make test`)
3. **Start the Development Server**: Run the API locally (`make dev`)
4. **Check Documentation**: Review the documentation at `http://localhost:8081`
5. **Review Contributing Guidelines**: Check for coding standards and contribution processes

## Getting Help

If you encounter any issues during setup:

1. **Check the Documentation**: Many common issues are documented
2. **Review Error Messages**: Carefully read any error messages for clues
3. **Consult Team Members**: Reach out to other developers for assistance
4. **File an Issue**: If you've found a bug, file an issue on GitHub

For internal onboarding, refer to the [Onboarding Guide](http://localhost:8081/onboarding.html) which provides detailed instructions on how to use the security and monitoring features.

## TTM‑MCP Expert Agent (Adapter) — Quick Links

- Docs (Diataxis):
  - Tutorial: docs/tutorials/ttm_mcp_quickstart.md
  - How‑to: docs/how-to/mcp_readiness_checks.md
  - Reference (contracts): docs/reference/mcp_contracts.md
  - Explanations: docs/explanations/mcp_adapter_philosophy.md
- Core facades:
  - gRPC proto: src/api/grpc/ttm_core.proto
  - gRPC server scaffold: src/api/grpc/grpc_server.py
  - GraphQL schema: src/api/graphql/schema.py
- MCP adapter (skeleton):
  - tools/ttm-mcp/config.py
  - tools/ttm-mcp/logging.py (audit + hashing + seed)
  - tools/ttm-mcp/schemas.py (Pydantic I/O)
  - tools/ttm-mcp/adapters/grpc_client.py
  - tools/ttm-mcp/server.py (transport‑agnostic handlers)

Environment keys (edit .env):
- TTM_API_URL, TTM_API_KEY
- EMBED_MODEL_TH, EMBED_MODEL_EN, SEARCH_TOPK, RAG_TOPK
- Optional: FIRECRAWL_API_KEY, LIGHTPANDA_API_KEY, CONTEXT7_API_KEY
- gRPC host/port: GRPC_HOST, GRPC_PORT (defaults 0.0.0.0:50051)

Manual run helpers (documented; run yourself):
- Generate gRPC stubs (see tutorial)
- Start API: make dev
- Start gRPC server: uv run python scripts/run_grpc_server.py
- Validate scaffolding: uv run python scripts/validate_rag_readiness.py

Audit & determinism:
- All MCP tools produce audit records in audit.log with input/output hashes, deterministic seed, latency, and status.
- Policy: “No citation → no answer” enforced in gates (wire as core integration advances).

## Cline Memory Bank

We maintain persistent project context under memory‑bank/ (read these first in each session):
- projectbrief.md, productContext.md, systemPatterns.md, techContext.md, activeContext.md, progress.md

Update policy:
- After implementing features or docs that affect agent behavior or contracts, update memory-bank/activeContext.md with the current focus and decisions.
- After each session or milestone, update memory-bank/progress.md with what works, what’s pending, and next steps.
