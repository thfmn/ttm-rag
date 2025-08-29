"""
Database migration script for the Thai Traditional Medicine RAG Bot.

This script provides functions to initialize and migrate the database schema.
"""

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.config import DATABASE_URL, init_database, drop_database
from src.database.models import Source, Document, Keyword, ProcessingLog


def create_database():
    """
    Create the database and all tables.
    """
    print("Creating database and tables...")
    try:
        init_database()
        print("Database and tables created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    return True


def drop_database_tables():
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    """
    print("Dropping all database tables...")
    try:
        drop_database()
        print("Database tables dropped successfully!")
    except Exception as e:
        print(f"Error dropping database tables: {e}")
        return False
    return True


def seed_database():
    """
    Seed the database with initial data.
    """
    print("Seeding database with initial data...")
    try:
        # Import here to avoid circular imports
        from src.database.config import get_db_session, close_db_session
        from src.database.repository import SourceRepository
        
        # Get database session
        session = get_db_session()
        
        # Create source repository
        source_repo = SourceRepository(session)
        
        # Create initial sources
        sources = [
            {
                "id": 1,
                "name": "PubMed",
                "type": "academic",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "api_endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
                "access_method": "api",
                "reliability_score": 5,
                "metadata": {"api_key": None}
            },
            {
                "id": 2,
                "name": "PMC Open Access",
                "type": "academic",
                "url": "https://www.ncbi.nlm.nih.gov/pmc/",
                "api_endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
                "access_method": "api",
                "reliability_score": 5,
                "metadata": {"api_key": None}
            }
        ]
        
        # Create sources
        for source_data in sources:
            try:
                # Check if source already exists
                existing_source = source_repo.get_source_by_id(source_data["id"])
                if not existing_source:
                    # Create source model
                    from src.models.source import Source as SourceModel
                    source_model = SourceModel(**source_data)
                    
                    # Create source in database
                    source_repo.create_source(source_model)
                    print(f"Created source: {source_data['name']}")
                else:
                    print(f"Source already exists: {source_data['name']}")
            except Exception as e:
                print(f"Error creating source {source_data['name']}: {e}")
        
        # Close session
        close_db_session(session)
        
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False
    return True


def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    WARNING: This will delete all data!
    """
    print("Resetting database...")
    try:
        # Drop all tables
        drop_database_tables()
        
        # Recreate all tables
        create_database()
        
        # Seed with initial data
        seed_database()
        
        print("Database reset completed successfully!")
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False
    return True


def main():
    """
    Main function to run database migrations.
    """
    parser = argparse.ArgumentParser(description="Database migration script")
    parser.add_argument(
        "action", 
        choices=["create", "drop", "seed", "reset"],
        help="Action to perform: create, drop, seed, or reset"
    )
    
    args = parser.parse_args()
    
    if args.action == "create":
        success = create_database()
    elif args.action == "drop":
        success = drop_database_tables()
    elif args.action == "seed":
        success = seed_database()
    elif args.action == "reset":
        success = reset_database()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()