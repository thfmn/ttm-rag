"""
Unit tests for database components.

These tests verify that our database models, repositories, and services work correctly.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.models import Source, Document, Keyword, ProcessingLog
from src.database.repository import (
    SourceRepository, 
    DocumentRepository, 
    KeywordRepository, 
    ProcessingLogRepository
)
from src.database.service import DatabaseService
from src.database.exceptions import DatabaseError, DatabaseConnectionError
from src.models.source import Source as SourceModel
from src.models.document import Document as DocumentModel
from src.models.pubmed import PubmedArticle, PubmedAuthor, PubmedJournal


class TestDatabaseModels:
    """Tests for database models."""
    
    def test_source_model_creation(self):
        """Test creating a Source model."""
        source = Source(
            id=1,
            name="PubMed",
            type="academic",
            url="https://pubmed.ncbi.nlm.nih.gov/",
            api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
            access_method="api",
            reliability_score=5,
            metadata={"api_key": None}
        )
        
        assert source.id == 1
        assert source.name == "PubMed"
        assert source.type == "academic"
        assert source.reliability_score == 5
        assert source.metadata == {"api_key": None}
    
    def test_document_model_creation(self):
        """Test creating a Document model."""
        document = Document(
            id=1,
            source_id=1,
            external_id="123456",
            title="Test Article",
            content="This is a test article.",
            abstract="This is a test abstract.",
            authors=["John Doe", "Jane Smith"],
            language="eng",
            document_type="research_paper",
            metadata={"doi": "10.1234/test"}
        )
        
        assert document.id == 1
        assert document.source_id == 1
        assert document.external_id == "123456"
        assert document.title == "Test Article"
        assert document.content == "This is a test article."
        assert document.abstract == "This is a test abstract."
        assert document.authors == ["John Doe", "Jane Smith"]
        assert document.language == "eng"
        assert document.document_type == "research_paper"
        assert document.metadata == {"doi": "10.1234/test"}
    
    def test_keyword_model_creation(self):
        """Test creating a Keyword model."""
        keyword = Keyword(
            id=1,
            term="medicine",
            term_thai="เวชศาสตร์",
            category="treatment"
        )
        
        assert keyword.id == 1
        assert keyword.term == "medicine"
        assert keyword.term_thai == "เวชศาสตร์"
        assert keyword.category == "treatment"
    
    def test_processing_log_model_creation(self):
        """Test creating a ProcessingLog model."""
        log = ProcessingLog(
            id=1,
            document_id=1,
            source_id=1,
            process_type="ingestion",
            status="success",
            message="Document ingested successfully",
            execution_time="00:00:01"
        )
        
        assert log.id == 1
        assert log.document_id == 1
        assert log.source_id == 1
        assert log.process_type == "ingestion"
        assert log.status == "success"
        assert log.message == "Document ingested successfully"
        assert log.execution_time == "00:00:01"


class TestSourceRepository:
    """Tests for SourceRepository."""
    
    @patch('src.database.repository.Session')
    def test_create_source(self, mock_session_class):
        """Test creating a source."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = SourceRepository(mock_session)
        
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
        
        # Call method
        result = repo.create_source(source_model)
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called
        assert isinstance(result, Source)
    
    @patch('src.database.repository.Session')
    def test_get_source_by_id(self, mock_session_class):
        """Test getting a source by ID."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = SourceRepository(mock_session)
        
        # Mock query result
        mock_source = Source(id=1, name="PubMed")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_source
        
        # Call method
        result = repo.get_source_by_id(1)
        
        # Verify
        assert result == mock_source
        mock_session.query.assert_called_once_with(Source)
        mock_session.query.return_value.filter.assert_called_once()
    
    @patch('src.database.repository.Session')
    def test_get_source_by_name(self, mock_session_class):
        """Test getting a source by name."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = SourceRepository(mock_session)
        
        # Mock query result
        mock_source = Source(id=1, name="PubMed")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_source
        
        # Call method
        result = repo.get_source_by_name("PubMed")
        
        # Verify
        assert result == mock_source
        mock_session.query.assert_called_once_with(Source)
        mock_session.query.return_value.filter.assert_called_once()


class TestDocumentRepository:
    """Tests for DocumentRepository."""
    
    @patch('src.database.repository.Session')
    def test_create_document_from_model(self, mock_session_class):
        """Test creating a document from a Document model."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = DocumentRepository(mock_session)
        
        # Create document model
        document_model = DocumentModel(
            source_id=1,
            external_id="123456",
            title="Test Article",
            content="This is a test article.",
            abstract="This is a test abstract.",
            authors=["John Doe"],
            language="eng",
            document_type="research_paper"
        )
        
        # Call method
        result = repo.create_document_from_model(document_model, 1)
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called
        assert isinstance(result, Document)
    
    @patch('src.database.repository.Session')
    def test_create_document_from_pubmed(self, mock_session_class):
        """Test creating a document from a PubMed article."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = DocumentRepository(mock_session)
        
        # Create PubMed article
        author = PubmedAuthor(name="John Doe")
        journal = PubmedJournal(title="Test Journal")
        article = PubmedArticle(
            pmid="123456",
            title="Test Article",
            abstract="This is a test abstract.",
            authors=[author],
            journal=journal,
            doi="10.1234/test",
            language="eng",
            article_type="research_paper",
            raw_xml="<xml>Test XML</xml>"
        )
        
        # Call method
        result = repo.create_document_from_pubmed(article, 1)
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called
        assert isinstance(result, Document)
    
    @patch('src.database.repository.Session')
    def test_get_document_by_id(self, mock_session_class):
        """Test getting a document by ID."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = DocumentRepository(mock_session)
        
        # Mock query result
        mock_document = Document(id=1, source_id=1, external_id="123456")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_document
        
        # Call method
        result = repo.get_document_by_id(1)
        
        # Verify
        assert result == mock_document
        mock_session.query.assert_called_once_with(Document)
        mock_session.query.return_value.filter.assert_called_once()


class TestKeywordRepository:
    """Tests for KeywordRepository."""
    
    @patch('src.database.repository.Session')
    def test_create_keyword(self, mock_session_class):
        """Test creating a keyword."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = KeywordRepository(mock_session)
        
        # Call method
        result = repo.create_keyword("medicine", "เวชศาสตร์", "treatment")
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called
        assert isinstance(result, Keyword)
        assert result.term == "medicine"
        assert result.term_thai == "เวชศาสตร์"
        assert result.category == "treatment"
    
    @patch('src.database.repository.Session')
    def test_get_keyword_by_term(self, mock_session_class):
        """Test getting a keyword by term."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = KeywordRepository(mock_session)
        
        # Mock query result
        mock_keyword = Keyword(id=1, term="medicine")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_keyword
        
        # Call method
        result = repo.get_keyword_by_term("medicine")
        
        # Verify
        assert result == mock_keyword
        mock_session.query.assert_called_once_with(Keyword)
        mock_session.query.return_value.filter.assert_called_once()


class TestProcessingLogRepository:
    """Tests for ProcessingLogRepository."""
    
    @patch('src.database.repository.Session')
    def test_create_log(self, mock_session_class):
        """Test creating a processing log."""
        # Create mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create repository
        repo = ProcessingLogRepository(mock_session)
        
        # Call method
        result = repo.create_log(
            source_id=1,
            process_type="ingestion",
            status="success",
            message="Document ingested successfully"
        )
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called
        assert isinstance(result, ProcessingLog)
        assert result.source_id == 1
        assert result.process_type == "ingestion"
        assert result.status == "success"
        assert result.message == "Document ingested successfully"


class TestDatabaseService:
    """Tests for DatabaseService."""
    
    @patch('src.database.service.get_db_session')
    @patch('src.database.service.close_db_session')
    def test_save_source_success(self, mock_close_session, mock_get_session):
        """Test saving a source successfully."""
        # Create mock session
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Create service
        service = DatabaseService()
        
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
        
        # Call method
        result = service.save_source(source_model)
        
        # Verify
        assert result is True
        mock_get_session.assert_called_once()
        mock_close_session.assert_called_once_with(mock_session)
    
    @patch('src.database.service.get_db_session')
    @patch('src.database.service.close_db_session')
    def test_save_source_failure(self, mock_close_session, mock_get_session):
        """Test saving a source with failure."""
        # Create mock session that raises an exception
        mock_session = Mock()
        mock_session.add.side_effect = Exception("Database error")
        mock_get_session.return_value = mock_session
        
        # Create service
        service = DatabaseService()
        
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
        
        # Call method
        result = service.save_source(source_model)
        
        # Verify
        assert result is False
        mock_get_session.assert_called_once()
        mock_close_session.assert_called_once_with(mock_session)
    
    @patch('src.database.service.get_db_session')
    @patch('src.database.service.close_db_session')
    def test_save_document_success(self, mock_close_session, mock_get_session):
        """Test saving a document successfully."""
        # Create mock session
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock repository create_document_from_model to return a document with ID
        with patch('src.database.service.DocumentRepository') as mock_repo_class:
            mock_repo_instance = Mock()
            mock_repo_instance.create_document_from_model.return_value = Mock(id=1)
            mock_repo_class.return_value = mock_repo_instance
            
            # Create service
            service = DatabaseService()
            
            # Create document model
            document_model = DocumentModel(
                source_id=1,
                external_id="123456",
                title="Test Article",
                content="This is a test article.",
                abstract="This is a test abstract.",
                authors=["John Doe"],
                language="eng",
                document_type="research_paper"
            )
            
            # Call method
            result = service.save_document(document_model, 1)
            
            # Verify
            assert result == 1
            mock_get_session.assert_called_once()
            mock_close_session.assert_called_once_with(mock_session)
    
    @patch('src.database.service.get_db_session')
    @patch('src.database.service.close_db_session')
    def test_save_document_failure(self, mock_close_session, mock_get_session):
        """Test saving a document with failure."""
        # Create mock session that raises an exception
        mock_session = Mock()
        mock_session.add.side_effect = Exception("Database error")
        mock_get_session.return_value = mock_session
        
        # Create service
        service = DatabaseService()
        
        # Create document model
        document_model = DocumentModel(
            source_id=1,
            external_id="123456",
            title="Test Article",
            content="This is a test article.",
            abstract="This is a test abstract.",
            authors=["John Doe"],
            language="eng",
            document_type="research_paper"
        )
        
        # Call method
        result = service.save_document(document_model, 1)
        
        # Verify
        assert result is None
        mock_get_session.assert_called_once()
        mock_close_session.assert_called_once_with(mock_session)
    
    @patch('src.database.service.get_db_session')
    @patch('src.database.service.close_db_session')
    def test_save_pubmed_article_success(self, mock_close_session, mock_get_session):
        """Test saving a PubMed article successfully."""
        # Create mock session
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock repository create_document_from_pubmed to return a document with ID
        with patch('src.database.service.DocumentRepository') as mock_repo_class:
            mock_repo_instance = Mock()
            mock_repo_instance.create_document_from_pubmed.return_value = Mock(id=1)
            mock_repo_class.return_value = mock_repo_instance
            
            # Create service
            service = DatabaseService()
            
            # Create PubMed article
            author = PubmedAuthor(name="John Doe")
            journal = PubmedJournal(title="Test Journal")
            article = PubmedArticle(
                pmid="123456",
                title="Test Article",
                abstract="This is a test abstract.",
                authors=[author],
                journal=journal,
                doi="10.1234/test",
                language="eng",
                article_type="research_paper",
                raw_xml="<xml>Test XML</xml>"
            )
            
            # Call method
            result = service.save_pubmed_article(article, 1)
            
            # Verify
            assert result == 1
            mock_get_session.assert_called_once()
            mock_close_session.assert_called_once_with(mock_session)
    
    @patch('src.database.service.get_db_session')
    @patch('src.database.service.close_db_session')
    def test_save_pubmed_article_failure(self, mock_close_session, mock_get_session):
        """Test saving a PubMed article with failure."""
        # Create mock session that raises an exception
        mock_session = Mock()
        mock_session.add.side_effect = Exception("Database error")
        mock_get_session.return_value = mock_session
        
        # Create service
        service = DatabaseService()
        
        # Create PubMed article
        author = PubmedAuthor(name="John Doe")
        journal = PubmedJournal(title="Test Journal")
        article = PubmedArticle(
            pmid="123456",
            title="Test Article",
            abstract="This is a test abstract.",
            authors=[author],
            journal=journal,
            doi="10.1234/test",
            language="eng",
            article_type="research_paper",
            raw_xml="<xml>Test XML</xml>"
        )
        
        # Call method
        result = service.save_pubmed_article(article, 1)
        
        # Verify
        assert result is None
        mock_get_session.assert_called_once()
        mock_close_session.assert_called_once_with(mock_session)