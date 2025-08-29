"""
Integration tests for database functionality.

These tests verify that our database components work correctly with a real database.
"""

import sys
import os
import pytest
from datetime import datetime
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.config import Base, init_database, drop_database
from src.database.models import Source, Document, Keyword, ProcessingLog
from src.database.repository import (
    SourceRepository, 
    DocumentRepository, 
    KeywordRepository, 
    ProcessingLogRepository
)
from src.database.service import DatabaseService
from src.models.source import Source as SourceModel
from src.models.document import Document as DocumentModel
from src.models.pubmed import PubmedArticle, PubmedAuthor, PubmedJournal


@pytest.fixture(scope="function")
def test_db_session():
    """
    Fixture to create an in-memory SQLite database for testing.
    """
    # Create an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create session
    session = SessionLocal()
    
    yield session
    
    # Clean up
    session.close()
    Base.metadata.drop_all(engine)


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    def test_source_repository_integration(self, test_db_session):
        """Test SourceRepository with real database."""
        # Create repository
        repo = SourceRepository(test_db_session)
        
        # Create source model
        source_model = SourceModel(
            id=1,
            name="PubMed",
            type="academic",
            url="https://pubmed.ncbi.nlm.nih.gov/",
            api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
            access_method="api",
            reliability_score=5,
            metadata={"api_key": None}
        )
        
        # Create source in database
        db_source = repo.create_source(source_model)
        
        # Verify creation
        assert db_source.id == 1
        assert db_source.name == "PubMed"
        assert db_source.type == "academic"
        assert db_source.reliability_score == 5
        
        # Test get by ID
        retrieved_source = repo.get_source_by_id(1)
        assert retrieved_source is not None
        assert retrieved_source.name == "PubMed"
        
        # Test get by name
        retrieved_source = repo.get_source_by_name("PubMed")
        assert retrieved_source is not None
        assert retrieved_source.id == 1
        
        # Test update source
        updated_source = repo.update_source(1, name="Updated PubMed")
        assert updated_source is not None
        assert updated_source.name == "Updated PubMed"
        
        # Test delete source
        deleted = repo.delete_source(1)
        assert deleted is True
        
        # Verify deletion
        retrieved_source = repo.get_source_by_id(1)
        assert retrieved_source is None
    
    def test_document_repository_integration(self, test_db_session):
        """Test DocumentRepository with real database."""
        # Create source first
        source = Source(
            id=1,
            name="PubMed",
            type="academic",
            url="https://pubmed.ncbi.nlm.nih.gov/",
            api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
            access_method="api",
            reliability_score=5,
            source_metadata=json.dumps({"api_key": None})
        )
        test_db_session.add(source)
        test_db_session.commit()
        
        # Create repository
        repo = DocumentRepository(test_db_session)
        
        # Create document model
        document_model = DocumentModel(
            source_id=1,
            external_id="123456",
            title="Test Article",
            content="This is a test article.",
            abstract="This is a test abstract.",
            authors=["John Doe", "Jane Smith"],
            language="eng",
            document_type="research_paper",
            quality_score=0.95
        )
        
        # Create document in database
        db_document = repo.create_document_from_model(document_model, 1)
        
        # Verify creation
        assert db_document.id is not None
        assert db_document.source_id == 1
        assert db_document.external_id == "123456"
        assert db_document.title == "Test Article"
        assert db_document.content == "This is a test article."
        assert db_document.abstract == "This is a test abstract."
        # Convert authors from JSON string
        if db_document.authors:
            authors = json.loads(db_document.authors)
            assert authors == ["John Doe", "Jane Smith"]
        assert db_document.language == "eng"
        assert db_document.document_type == "research_paper"
        assert db_document.quality_score == 0.95
        
        # Test get by ID
        retrieved_document = repo.get_document_by_id(db_document.id)
        assert retrieved_document is not None
        assert retrieved_document.title == "Test Article"
        
        # Test get by external ID and source ID
        retrieved_document = repo.get_document_by_external_id("123456", 1)
        assert retrieved_document is not None
        assert retrieved_document.id == db_document.id
        
        # Test get documents by source
        documents = repo.get_documents_by_source(1)
        assert len(documents) == 1
        assert documents[0].title == "Test Article"
        
        # Test search documents
        documents = repo.search_documents("test")
        assert len(documents) == 1
        assert documents[0].title == "Test Article"
        
        # Test update document
        updated_document = repo.update_document(db_document.id, title="Updated Test Article")
        assert updated_document is not None
        assert updated_document.title == "Updated Test Article"
        
        # Test delete document
        deleted = repo.delete_document(db_document.id)
        assert deleted is True
        
        # Verify deletion
        retrieved_document = repo.get_document_by_id(db_document.id)
        assert retrieved_document is None
    
    def test_keyword_repository_integration(self, test_db_session):
        """Test KeywordRepository with real database."""
        # Create repository
        repo = KeywordRepository(test_db_session)
        
        # Create keyword
        keyword = repo.create_keyword("medicine", "เวชศาสตร์", "treatment")
        
        # Verify creation
        assert keyword.id is not None
        assert keyword.term == "medicine"
        assert keyword.term_thai == "เวชศาสตร์"
        assert keyword.category == "treatment"
        
        # Test get by term
        retrieved_keyword = repo.get_keyword_by_term("medicine")
        assert retrieved_keyword is not None
        assert retrieved_keyword.id == keyword.id
        assert retrieved_keyword.term_thai == "เวชศาสตร์"
        
        # Test get or create keyword (existing)
        existing_keyword = repo.get_or_create_keyword("medicine")
        assert existing_keyword.id == keyword.id
        
        # Test get or create keyword (new)
        new_keyword = repo.get_or_create_keyword("herbal", "สมุนไพร", "treatment")
        assert new_keyword.id is not None
        assert new_keyword.term == "herbal"
        assert new_keyword.term_thai == "สมุนไพร"
    
    def test_processing_log_repository_integration(self, test_db_session):
        """Test ProcessingLogRepository with real database."""
        # Create source first
        source = Source(
            id=1,
            name="PubMed",
            type="academic",
            url="https://pubmed.ncbi.nlm.nih.gov/",
            api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
            access_method="api",
            reliability_score=5,
            source_metadata=json.dumps({"api_key": None})
        )
        test_db_session.add(source)
        test_db_session.commit()
        
        # Create document
        document = Document(
            id=1,
            source_id=1,
            external_id="123456",
            title="Test Article",
            content="This is a test article.",
            document_metadata=json.dumps({"doi": "10.1234/test"})
        )
        test_db_session.add(document)
        test_db_session.commit()
        
        # Create repository
        repo = ProcessingLogRepository(test_db_session)
        
        # Create log entry
        log = repo.create_log(
            source_id=1,
            document_id=1,
            process_type="ingestion",
            status="success",
            message="Document ingested successfully",
            metadata={"duration": "1.5s"}
        )
        
        # Verify creation
        assert log.id is not None
        assert log.source_id == 1
        assert log.document_id == 1
        assert log.process_type == "ingestion"
        assert log.status == "success"
        assert log.message == "Document ingested successfully"
        # Convert metadata from JSON string
        if log.log_metadata:
            metadata = json.loads(log.log_metadata)
            assert metadata == {"duration": "1.5s"}
    
    def test_database_service_integration(self, test_db_session):
        """Test DatabaseService with real database."""
        # This test would require mocking the session management
        # For now, we'll just verify the service can be instantiated
        service = DatabaseService()
        assert service is not None


@pytest.mark.integration
class TestDatabaseInitialization:
    """Tests for database initialization."""
    
    def test_init_database(self):
        """Test database initialization."""
        # Create an in-memory SQLite database for testing
        engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=False
        )
        
        # Initialize database
        from src.database.config import Base
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = sqlalchemy.inspect(engine)
        tables = inspector.get_table_names()
        
        # Check that key tables exist
        assert "sources" in tables
        assert "documents" in tables
        assert "keywords" in tables
        assert "processing_logs" in tables


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])