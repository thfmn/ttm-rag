"""
Database configuration for the Thai Traditional Medicine RAG Bot.

This module provides database configuration and connection management.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.engine import Engine

# Database configuration
# Use SQLite for development and testing by default
# Set DATABASE_URL environment variable to use PostgreSQL in production
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./thai_medicine.db"  # SQLite database file
)

# Check if we're using SQLite
IS_SQLITE = DATABASE_URL.startswith("sqlite://")

# Database connection pool configuration
if IS_SQLITE:
    # SQLite-specific configuration
    DB_POOL_SIZE = 1
    DB_MAX_OVERFLOW = 0
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = -1
else:
    # PostgreSQL-specific configuration
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create database engine with connection pooling
if IS_SQLITE:
    # SQLite engine with thread-local connections
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
        echo=False  # Set to True for SQL debugging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db_session() -> Session:
    """
    Get a database session.
    
    Returns:
        Database session
    """
    return SessionLocal()

def close_db_session(session: Session) -> None:
    """
    Close a database session.
    
    Args:
        session: Database session to close
    """
    session.close()

def init_database() -> None:
    """
    Initialize the database by creating all tables.
    """
    from src.database.models import Source, Document, Keyword, ProcessingLog
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def drop_database() -> None:
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    """
    from src.database.models import Source, Document, Keyword, ProcessingLog
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)

# Enable query logging for debugging (optional)
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Event listener for SQL query execution."""
    pass

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Event listener for SQL query execution completion."""
    pass