# Development Environment Setup Guide

This guide provides detailed instructions for setting up a development environment for the Thai Traditional Medicine RAG Bot project. Whether you're a new team member or setting up the project on a new machine, this guide will walk you through the process step by step.

## Prerequisites

Before beginning the setup process, ensure you have the following installed on your system:

1. **Python 3.11 or higher** - The project uses modern Python features
2. **Git** - For version control and repository management
3. **Docker** (optional) - For containerized database services
4. **curl** - For downloading the UV package manager

## Quick Start Setup

The fastest way to get started is to use the automated setup script:

```bash
# Clone the repository
git clone <your-repo-url>
cd thai-traditional-medicine-rag-bot

# Make the setup script executable
chmod +x scripts/setup/install.sh

# Run the automated setup
./scripts/setup/install.sh
```

This script will:
1. Install UV package manager if not already present
2. Create a virtual environment
3. Install all project dependencies
4. Set up pre-commit hooks
5. Create a default `.env` file
6. Install Thai language processing resources

## Manual Setup Process

For users who prefer manual control over the setup process, follow these steps:

### Step 1: Install UV Package Manager

UV is a fast Python package installer and resolver:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Step 2: Create Virtual Environment

Create an isolated Python environment for the project:

```bash
# Create virtual environment with Python 3.13
uv venv --python 3.13

# Activate the virtual environment
source .venv/bin/activate

# Verify activation (you should see (.venv) in your prompt)
which python
```

### Step 3: Install Project Dependencies

Install all required dependencies using UV:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Install production dependencies (if needed)
uv pip install -e ".[prod]"
```

### Step 4: Set Up Pre-commit Hooks

Pre-commit hooks help maintain code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit checks on all files
pre-commit run --all-files
```

## Environment Configuration

### Step 1: Create Environment File

Create a `.env` file with your configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env  # or use your preferred editor
```

The default configuration should work for development, but you may want to customize:

- Database connection settings
- API keys for data sources
- Application settings
- Security configurations

### Step 2: Environment Variables Overview

Key environment variables include:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./thai_medicine.db  # SQLite for development
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=thai_medicine_db
DATABASE_USER=user
DATABASE_PASSWORD=password

# Redis Configuration (for caching and task queues)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Keys (for data sources)
PUBMED_API_KEY=your_pubmed_api_key
WHO_API_KEY=your_who_api_key
DTAM_API_KEY=your_dtam_api_key

# Application Settings
APP_NAME=Thai Traditional Medicine RAG Bot
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development

# Processing Settings
MAX_WORKERS=4
BATCH_SIZE=100
VALIDATION_THRESHOLD=0.8

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Database Setup

The project supports both SQLite (for development) and PostgreSQL (for production).

### Option 1: SQLite Setup (Recommended for Development)

SQLite is the default database for development and requires no additional setup:

```bash
# Create database tables and seed with initial data
make db-setup

# Or run individual commands:
make db-create  # Create tables
make db-seed    # Seed with initial data
```

### Option 2: PostgreSQL Setup (For Advanced Development)

For a more production-like environment, you can use PostgreSQL:

```bash
# Start PostgreSQL container
docker-compose up -d db

# Wait for database to initialize (15-30 seconds)
sleep 30

# Update .env file to use PostgreSQL
nano .env
# Set: DATABASE_URL=postgresql://user:password@localhost:5432/thai_medicine_db

# Create database tables and seed with initial data
make db-setup
```

### Database Management Commands

The project provides several Makefile commands for database management:

```bash
# Create database tables
make db-create

# Drop database tables (WARNING: Deletes all data!)
make db-drop

# Seed database with initial data
make db-seed

# Reset database (drop, create, and seed)
make db-reset

# Setup database (create and seed)
make db-setup
```

## Thai Language Resources Setup

The project uses Thai language processing libraries that require additional resources:

```bash
# Install Thai language processing resources
make thai-setup
```

This command installs:
- Thai word vectors (thai2fit_wv)
- Thai embeddings (thai2vec)
- Thai spaCy model (if available)

## Testing the Setup

After completing the setup, verify everything works correctly:

```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov

# Run only unit tests
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v
```

All tests should pass before proceeding with development.

## Development Workflow

### Starting the Development Server

Start the FastAPI development server with auto-reload:

```bash
# Start development server
make dev

# The server will be available at http://localhost:8005
```

The development server automatically reloads when you make code changes.

### Code Quality Checks

Maintain code quality with these commands:

```bash
# Run linters
make lint

# Format code
make format

# Run both linters and formatters
make lint && make format
```

### Running Specific Tests

During development, you may want to run specific tests:

```bash
# Run tests for a specific module
pytest tests/unit/test_pubmed_connector.py

# Run tests with a specific marker
pytest -m "integration"

# Run tests matching a pattern
pytest -k "test_search"

# Run tests with verbose output
pytest -v
```

## Documentation Development

The project uses Sphinx for documentation:

```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve

# Rebuild and serve documentation
make docs-rebuild
```

Documentation will be available at `http://localhost:8081`.

## Docker Development Environment

For a containerized development environment:

```bash
# Build Docker images
make docker-build

# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## Common Development Tasks

### Adding New Dependencies

When adding new dependencies:

```bash
# Add to pyproject.toml and install
uv pip install new-package-name

# Add to development dependencies
uv pip install new-dev-package-name

# Update lock file
uv pip compile pyproject.toml -o requirements.txt
```

### Database Migration

When changing database models:

```bash
# After modifying models, recreate database tables
make db-reset
```

### Code Generation

Some parts of the project are generated:

```bash
# Regenerate any auto-generated code
# (Specific commands depend on what needs to be generated)
```

## Troubleshooting

### Common Issues and Solutions

1. **Port Already in Use**
   ```bash
   # Kill processes using the port
   lsof -i :8005 | grep LISTEN | awk '{print $2}' | xargs kill -9
   ```

2. **Database Connection Errors**
   ```bash
   # Reset the database
   make db-reset
   ```

3. **Missing Thai Language Resources**
   ```bash
   # Reinstall Thai language resources
   make thai-setup
   ```

4. **Dependency Installation Failures**
   ```bash
   # Upgrade UV and reinstall dependencies
   pip install --upgrade uv
   uv pip install -e ".[dev]"
   ```

5. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   uv venv --python 3.13
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

### Debugging Tips

1. **Enable Debug Mode**
   Set `DEBUG=True` in your `.env` file

2. **View Application Logs**
   ```bash
   # View logs in real-time
   tail -f logs/app.log
   
   # Or use the Makefile command
   make logs
   ```

3. **Database Inspection**
   ```bash
   # For SQLite
   sqlite3 thai_medicine.db
   
   # For PostgreSQL with Docker
   docker-compose exec db psql -U user -d thai_medicine_db
   ```

## IDE and Editor Setup

### VS Code Recommended Extensions

1. **Python** - Official Python extension
2. **Pylance** - Rich Python language support
3. **Black Formatter** - Code formatter
4. **isort** - Import sorting
5. **Flake8** - Linting
6. **Docker** - Dockerfile support
7. **Sphinx** - Documentation support

### PyCharm Configuration

1. **Interpreter Setup**
   - Set interpreter to `.venv/bin/python`

2. **Code Formatting**
   - Configure Black as external tool
   - Configure isort for import sorting

3. **Run Configurations**
   - Create run configuration for `make dev`
   - Create test configuration for `make test`

## Best Practices

### Code Organization

1. **Follow Project Structure**
   - Place new modules in appropriate directories
   - Follow existing naming conventions

2. **Write Tests**
   - Write unit tests for new functionality
   - Write integration tests for complex workflows

3. **Documentation**
   - Document new functions and classes
   - Update README and docs when adding major features

### Git Workflow

1. **Branch Naming**
   - Use descriptive branch names: `feature/new-feature-name`
   - Use `fix/` prefix for bug fixes
   - Use `docs/` prefix for documentation changes

2. **Commit Messages**
   - Use present tense ("Add feature" not "Added feature")
   - Be descriptive but concise
   - Reference issues when applicable

3. **Pull Requests**
   - Keep PRs focused on a single feature or fix
   - Include tests for new functionality
   - Update documentation as needed

This comprehensive setup guide should help you quickly get started with development on the Thai Traditional Medicine RAG Bot project. If you encounter any issues during setup, refer to the troubleshooting section or reach out to the team for assistance.