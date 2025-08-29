#!/bin/bash
# init-postgres.sh - Initialize PostgreSQL database for Thai Traditional Medicine RAG Bot

# Database connection parameters
DB_HOST=${DATABASE_HOST:-localhost}
DB_PORT=${DATABASE_PORT:-5432}
DB_NAME=${DATABASE_NAME:-thai_medicine_db}
DB_USER=${DATABASE_USER:-user}
DB_PASSWORD=${DATABASE_PASSWORD:-password}

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done

echo "PostgreSQL is ready!"

# Create database and extensions
echo "Creating database and extensions..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" 2>/dev/null || true
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" 2>/dev/null || true

echo "Database initialization complete!"