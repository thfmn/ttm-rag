# Deployment Guide

This guide explains how to deploy the Thai Traditional Medicine RAG Bot application in different environments.

## Prerequisites

Before deploying the application, ensure you have the following:

1. Python 3.11 or higher
2. UV package manager
3. Docker (for containerized deployment)
4. Access to a PostgreSQL database with pgvector extension
5. API keys for data sources (e.g., PubMed)

## Local Development Deployment

### 1. Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd thai-traditional-medicine-rag-bot

# Install dependencies using UV
make install
```

### 2. Set Up Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env to add your API keys and database credentials
```

### 3. Start Database Services

The application uses Docker Compose to manage database services:

```bash
# Start the database container
docker-compose up -d db

# Wait for the database to be ready (about 15-30 seconds)
```

### 4. Initialize Database Tables

Once the database is running, initialize the tables:

```bash
# Copy the initialization script to the container
docker cp scripts/database/init.sql thai-traditional-medicine-rag-bot-db-1:/tmp/init.sql

# Run the initialization script
docker-compose exec db psql -U user -d thai_medicine_db -f /tmp/init.sql
```

### 5. Run Database Migrations

```bash
# Create database tables
make db-setup

# Or run the migration scripts directly
python scripts/database/migrate.py create
python scripts/database/migrate.py seed
```

### 6. Install Thai Language Resources

```bash
# Install Thai language processing resources
make thai-setup
```

### 7. Run the Application

```bash
# Start the FastAPI server
make api
```

The API will be available at `http://localhost:8000`.

## Docker Deployment

### 1. Build Docker Images

```bash
# Build the Docker images
make docker-build
```

### 2. Start Services

```bash
# Start all services using Docker Compose
make docker-up
```

### 3. Set Up Database

```bash
# Copy the initialization script to the container
docker cp scripts/database/init.sql thai-traditional-medicine-rag-bot-db-1:/tmp/init.sql

# Run the initialization script
docker-compose exec db psql -U user -d thai_medicine_db -f /tmp/init.sql

# Set up the database tables
make db-setup
```

### 4. Install Thai Language Resources

```bash
# Install Thai language processing resources
make thai-setup
```

The application will be available at `http://localhost:8000`.

## Production Deployment

### 1. Environment Configuration

For production deployment, you should:

1. Set up a production database with proper security measures
2. Configure SSL/TLS for secure communication
3. Set up proper logging and monitoring
4. Configure backup and disaster recovery procedures
5. Set up authentication and authorization (when implemented)

### 2. Database Configuration

In production, use a managed PostgreSQL database with pgvector extension:

```bash
# Set database connection string in .env
DATABASE_URL=postgresql://user:password@host:port/database
```

### 3. API Keys

Set up API keys for data sources in environment variables:

```bash
# Set API keys in .env
PUBMED_API_KEY=your_pubmed_api_key
```

### 4. Reverse Proxy

Use a reverse proxy like Nginx for:

1. SSL termination
2. Load balancing
3. Rate limiting
4. Caching

### 5. Monitoring and Logging

Set up monitoring with:

1. Prometheus for metrics collection
2. Grafana for dashboard visualization
3. ELK stack for log aggregation (when implemented)

## Health Checks

The application provides health check endpoints:

- `/health` - Basic health check
- `/metrics` - Prometheus metrics

## Scaling

For high availability and scaling:

1. Run multiple instances behind a load balancer
2. Use a managed database service
3. Implement caching with Redis
4. Use a CDN for static assets (documentation)

## Backup and Recovery

Implement regular backups for:

1. Database
2. Configuration files
3. Application code

Test recovery procedures regularly.