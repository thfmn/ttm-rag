# Thai Traditional Medicine RAG Bot

## Project Documentation

You can view the project documentation by running:

```bash
python serve_docs.py
```

Then opening your browser to http://localhost:8081

For internal onboarding, refer to the [Onboarding Guide](http://localhost:8081/onboarding.html) which provides detailed instructions on how to use the security and monitoring features.

## Quick Start with Dockerized PostgreSQL

### 1. Start Database Services
```bash
# Start the database container
docker-compose up -d db

# Wait for the database to be ready (about 15-30 seconds)
```

### 2. Initialize Database Tables
```bash
# Copy the initialization script to the container
docker cp scripts/database/init.sql thai-traditional-medicine-rag-bot-db-1:/tmp/init.sql

# Run the initialization script
docker-compose exec db psql -U user -d thai_medicine_db -f /tmp/init.sql
```

### 3. Run Database Migrations
```bash
# Create database tables and seed initial data
python scripts/database/migrate.py create
python scripts/database/migrate.py seed
```

### 4. Start the Application
```bash
# Start the FastAPI server
make api
```

The API will be available at `http://localhost:8005`.

## Quick Start Commands

### 1. Clone and setup
git clone # Todo
cd thai-traditional-medicine-rag-bot

### 2. Run setup script
chmod +x scripts/setup/install.sh
./scripts/setup/install.sh

### 3. Start services
make docker-up

### 4. Setup database
make db-setup

### 5. Install Thai language resources
make thai-setup

### 6. Run tests
make test

### 7. Start development
make dev

## Verification Commands

### 1. Clone and setup
git clone <your-repo-url>
cd thai-traditional-medicine-rag-bot

### 2. Run setup script
chmod +x scripts/setup/install.sh
./scripts/setup/install.sh

### 3. Start services
make docker-up

### 4. Setup database
make db-setup

### 5. Install Thai language resources
make thai-setup

### 6. Run tests
make test

### 7. Start development
make dev

## Current Project Status

The project has made significant progress in implementing security and monitoring features:

### ✅ Security Enhancements
- Input sanitization using nh3 (Python binding for ammonia) to prevent XSS attacks
- HTTPS enforcement middleware for production environments
- CORS configuration for cross-origin requests
- Audit logging for compliance tracking
- Data encryption utilities for sensitive metadata

### ✅ Monitoring & Health Checks
- Prometheus monitoring middleware with request metrics
- Health check endpoints (`/health`, `/metrics`)
- Comprehensive error tracking and logging

### ✅ CI/CD Pipeline
- GitHub Actions workflow for testing and building
- Support for multiple Python versions (3.11, 3.12)
- Automated linting and testing steps

### ✅ Documentation
- Comprehensive deployment guide
- Internal onboarding guide for team members
- Updated documentation with all recent enhancements
- Sphinx-based documentation system

For detailed information about the current status and future steps, please refer to the project documentation, particularly the "Project Status" section.