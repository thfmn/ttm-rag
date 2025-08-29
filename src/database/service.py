"""
Service layer for database operations.

This module provides a service layer that abstracts database operations
and provides a clean interface for the rest of the application to interact
with the database.
"""

from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json

from src.database.config import get_db_session, close_db_session
from src.database.repository import (
    SourceRepository, 
    DocumentRepository, 
    KeywordRepository, 
    ProcessingLogRepository
)
from src.database.exceptions import (
    DatabaseError, 
    DatabaseConnectionError, 
    create_database_error_from_sqlalchemy_error
)
from src.models.source import Source as SourceModel
from src.models.document import Document as DocumentModel
from src.models.pubmed import PubmedArticle


class DatabaseService:
    """
    Service layer for database operations.
    
    This service provides a clean interface for database operations
    and handles connection management and error handling.
    """
    
    def __init__(self):
        """Initialize the database service."""
        pass
    
    @contextmanager
    def get_db_session(self):
        """
        Context manager for database sessions.
        
        Yields:
            Database session
        """
        session = get_db_session()
        try:
            yield session
        except SQLAlchemyError as e:
            session.rollback()
            raise create_database_error_from_sqlalchemy_error(e)
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Unexpected error in database session: {e}", original_exception=e)
        finally:
            close_db_session(session)
    
    def save_source(self, source: SourceModel) -> bool:
        """
        Save a source to the database.
        
        Args:
            source: Source model to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with self.get_db_session() as session:
                source_repo = SourceRepository(session)
                source_repo.create_source(source)
                return True
        except DatabaseError:
            # Log the error (in a real implementation, we'd use proper logging)
            return False
    
    def save_document(self, document: DocumentModel, source_id: int) -> Optional[int]:
        """
        Save a document to the database.
        
        Args:
            document: Document model to save
            source_id: Source ID for foreign key relationship
            
        Returns:
            Document ID if saved successfully, None otherwise
        """
        try:
            with self.get_db_session() as session:
                document_repo = DocumentRepository(session)
                db_document = document_repo.create_document_from_model(document, source_id)
                return db_document.id
        except DatabaseError:
            # Log the error (in a real implementation, we'd use proper logging)
            return None
    
    def save_pubmed_article(self, article: PubmedArticle, source_id: int) -> Optional[int]:
        """
        Save a PubMed article to the database.
        
        Args:
            article: PubMed article to save
            source_id: Source ID for foreign key relationship
            
        Returns:
            Document ID if saved successfully, None otherwise
        """
        try:
            with self.get_db_session() as session:
                document_repo = DocumentRepository(session)
                db_document = document_repo.create_document_from_pubmed(article, source_id)
                return db_document.id
        except DatabaseError:
            # Log the error (in a real implementation, we'd use proper logging)
            return None
    
    def get_source_by_id(self, source_id: int) -> Optional[SourceModel]:
        """
        Get a source by ID.
        
        Args:
            source_id: Source ID
            
        Returns:
            Source model or None if not found
        """
        try:
            with self.get_db_session() as session:
                source_repo = SourceRepository(session)
                db_source = source_repo.get_source_by_id(source_id)
                if db_source:
                    # Convert database model to Pydantic model
                    # Convert metadata from JSON string
                    metadata = None
                    if db_source.source_metadata:
                        try:
                            metadata = json.loads(db_source.source_metadata)
                        except json.JSONDecodeError:
                            metadata = None
                    
                    return SourceModel(
                        id=db_source.id,
                        name=db_source.name,
                        type=db_source.type,
                        url=db_source.url,
                        api_endpoint=db_source.api_endpoint,
                        access_method=db_source.access_method,
                        reliability_score=db_source.reliability_score,
                        metadata=metadata
                    )
                return None
        except DatabaseError:
            # Log the error (in a real implementation, we'd use proper logging)
            return None
    
    def get_document_by_id(self, document_id: int) -> Optional[DocumentModel]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document model or None if not found
        """
        try:
            with self.get_db_session() as session:
                document_repo = DocumentRepository(session)
                db_document = document_repo.get_document_by_id(document_id)
                if db_document:
                    # Convert database model to Pydantic model
                    # Convert complex fields from JSON strings
                    authors = None
                    if db_document.authors:
                        try:
                            authors = json.loads(db_document.authors)
                        except json.JSONDecodeError:
                            authors = None
                    
                    metadata = None
                    if db_document.document_metadata:
                        try:
                            metadata = json.loads(db_document.document_metadata)
                        except json.JSONDecodeError:
                            metadata = None
                    
                    return DocumentModel(
                        source_id=db_document.source_id,
                        external_id=db_document.external_id,
                        title=db_document.title,
                        content=db_document.content,
                        abstract=db_document.abstract,
                        authors=authors,
                        publication_date=db_document.publication_date,
                        language=db_document.language,
                        document_type=db_document.document_type,
                        quality_score=db_document.quality_score,
                        metadata=metadata
                    )
                return None
        except DatabaseError:
            # Log the error (in a real implementation, we'd use proper logging)
            return None
    
    def search_documents(self, query: str, limit: int = 50) -> List[DocumentModel]:
        """
        Search documents by query.
        
        Args:
            query: Search query
            limit: Maximum number of documents to return
            
        Returns:
            List of document models
        """
        try:
            with self.get_db_session() as session:
                document_repo = DocumentRepository(session)
                db_documents = document_repo.search_documents(query, limit)
                
                # Convert database models to Pydantic models
                documents = []
                for db_document in db_documents:
                    # Convert complex fields from JSON strings
                    authors = None
                    if db_document.authors:
                        try:
                            authors = json.loads(db_document.authors)
                        except json.JSONDecodeError:
                            authors = None
                    
                    metadata = None
                    if db_document.document_metadata:
                        try:
                            metadata = json.loads(db_document.document_metadata)
                        except json.JSONDecodeError:
                            metadata = None
                    
                    document = DocumentModel(
                        source_id=db_document.source_id,
                        external_id=db_document.external_id,
                        title=db_document.title,
                        content=db_document.content,
                        abstract=db_document.abstract,
                        authors=authors,
                        publication_date=db_document.publication_date,
                        language=db_document.language,
                        document_type=db_document.document_type,
                        quality_score=db_document.quality_score,
                        metadata=metadata
                    )
                    documents.append(document)
                
                return documents
        except DatabaseError:
            # Log the error (in a real implementation, we'd use proper logging)
            return []


# Global database service instance
db_service = DatabaseService()