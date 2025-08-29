"""
Repository pattern implementations for database operations.

This module provides repository classes that encapsulate database operations
for our models, following the repository pattern for better separation of concerns.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import json

from src.database.models import Source, Document, Keyword, ProcessingLog
from src.models.source import Source as SourceModel
from src.models.document import Document as DocumentModel
from src.models.pubmed import PubmedArticle


class SourceRepository:
    """
    Repository for Source model operations.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_source(self, source: SourceModel) -> Source:
        """
        Create a new source in the database.
        
        Args:
            source: Source model to create
            
        Returns:
            Created Source database model
        """
        # Convert metadata to JSON string
        metadata_str = json.dumps(source.metadata) if source.metadata else None
        
        db_source = Source(
            id=source.id,
            name=source.name,
            type=source.type,
            url=source.url,
            api_endpoint=source.api_endpoint,
            access_method=source.access_method,
            reliability_score=source.reliability_score,
            source_metadata=metadata_str
        )
        self.db_session.add(db_source)
        self.db_session.commit()
        self.db_session.refresh(db_source)
        return db_source
    
    def get_source_by_id(self, source_id: int) -> Optional[Source]:
        """
        Get a source by ID.
        
        Args:
            source_id: Source ID
            
        Returns:
            Source database model or None if not found
        """
        return self.db_session.query(Source).filter(Source.id == source_id).first()
    
    def get_source_by_name(self, name: str) -> Optional[Source]:
        """
        Get a source by name.
        
        Args:
            name: Source name
            
        Returns:
            Source database model or None if not found
        """
        return self.db_session.query(Source).filter(Source.name == name).first()
    
    def get_all_sources(self) -> List[Source]:
        """
        Get all sources.
        
        Returns:
            List of Source database models
        """
        return self.db_session.query(Source).all()
    
    def update_source(self, source_id: int, **kwargs) -> Optional[Source]:
        """
        Update a source.
        
        Args:
            source_id: Source ID
            **kwargs: Fields to update
            
        Returns:
            Updated Source database model or None if not found
        """
        source = self.get_source_by_id(source_id)
        if source:
            for key, value in kwargs.items():
                # Handle metadata conversion
                if key == "metadata":
                    setattr(source, "source_metadata", json.dumps(value) if value else None)
                else:
                    setattr(source, key, value)
            self.db_session.commit()
            self.db_session.refresh(source)
        return source
    
    def delete_source(self, source_id: int) -> bool:
        """
        Delete a source.
        
        Args:
            source_id: Source ID
            
        Returns:
            True if deleted, False if not found
        """
        source = self.get_source_by_id(source_id)
        if source:
            self.db_session.delete(source)
            self.db_session.commit()
            return True
        return False


class DocumentRepository:
    """
    Repository for Document model operations.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_document_from_model(self, document: DocumentModel, source_id: int) -> Document:
        """
        Create a new document in the database from a Document model.
        
        Args:
            document: Document model to create
            source_id: Source ID for foreign key relationship
            
        Returns:
            Created Document database model
        """
        # Convert complex fields to JSON strings
        authors_str = json.dumps(document.authors) if document.authors else None
        metadata_str = json.dumps(document.metadata) if document.metadata else None
        
        db_document = Document(
            source_id=source_id,
            external_id=document.external_id,
            title=document.title,
            content=document.content,
            abstract=document.abstract,
            authors=authors_str,
            publication_date=document.publication_date,
            language=document.language,
            document_type=document.document_type,
            quality_score=document.quality_score,
            document_metadata=metadata_str
        )
        self.db_session.add(db_document)
        self.db_session.commit()
        self.db_session.refresh(db_document)
        return db_document
    
    def create_document_from_pubmed(self, article: PubmedArticle, source_id: int) -> Document:
        """
        Create a new document in the database from a PubmedArticle.
        
        Args:
            article: PubmedArticle to create
            source_id: Source ID for foreign key relationship
            
        Returns:
            Created Document database model
        """
        # Extract authors
        authors = [author.name for author in article.authors] if article.authors else None
        authors_str = json.dumps(authors) if authors else None
        
        # Extract journal
        journal = article.journal.title if article.journal else None
        
        # Create metadata
        metadata = {
            "doi": article.doi,
            "journal": journal,
            "mesh_terms": article.mesh_terms,
            "chemicals": article.chemicals,
            "country": article.country,
            "pmid": article.pmid
        }
        metadata_str = json.dumps(metadata) if metadata else None
        
        db_document = Document(
            source_id=source_id,
            external_id=article.pmid,
            title=article.title,
            content=article.raw_xml,
            abstract=article.abstract,
            authors=authors_str,
            publication_date=None,  # Would need to parse from article.publication_date
            language=article.language,
            document_type=article.article_type or "research_paper",
            document_metadata=metadata_str
        )
        self.db_session.add(db_document)
        self.db_session.commit()
        self.db_session.refresh(db_document)
        return db_document
    
    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document database model or None if not found
        """
        return self.db_session.query(Document).filter(Document.id == document_id).first()
    
    def get_document_by_external_id(self, external_id: str, source_id: int) -> Optional[Document]:
        """
        Get a document by external ID and source ID.
        
        Args:
            external_id: External document ID
            source_id: Source ID
            
        Returns:
            Document database model or None if not found
        """
        return self.db_session.query(Document).filter(
            and_(
                Document.external_id == external_id,
                Document.source_id == source_id
            )
        ).first()
    
    def get_documents_by_source(self, source_id: int, limit: int = 100) -> List[Document]:
        """
        Get documents by source ID.
        
        Args:
            source_id: Source ID
            limit: Maximum number of documents to return
            
        Returns:
            List of Document database models
        """
        return self.db_session.query(Document).filter(
            Document.source_id == source_id
        ).limit(limit).all()
    
    def search_documents(self, query: str, limit: int = 50) -> List[Document]:
        """
        Search documents by title or content.
        
        Args:
            query: Search query
            limit: Maximum number of documents to return
            
        Returns:
            List of Document database models
        """
        return self.db_session.query(Document).filter(
            or_(
                Document.title.ilike(f"%{query}%"),
                Document.abstract.ilike(f"%{query}%")
            )
        ).limit(limit).all()
    
    def get_recent_documents(self, days: int = 30, limit: int = 50) -> List[Document]:
        """
        Get recently created documents.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of documents to return
            
        Returns:
            List of Document database models
        """
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)
        return self.db_session.query(Document).filter(
            Document.created_at >= cutoff_date
        ).order_by(desc(Document.created_at)).limit(limit).all()
    
    def update_document(self, document_id: int, **kwargs) -> Optional[Document]:
        """
        Update a document.
        
        Args:
            document_id: Document ID
            **kwargs: Fields to update
            
        Returns:
            Updated Document database model or None if not found
        """
        document = self.get_document_by_id(document_id)
        if document:
            for key, value in kwargs.items():
                # Handle complex field conversions
                if key == "authors":
                    setattr(document, key, json.dumps(value) if value else None)
                elif key == "metadata":
                    setattr(document, "document_metadata", json.dumps(value) if value else None)
                else:
                    setattr(document, key, value)
            self.db_session.commit()
            self.db_session.refresh(document)
        return document
    
    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        document = self.get_document_by_id(document_id)
        if document:
            self.db_session.delete(document)
            self.db_session.commit()
            return True
        return False


class KeywordRepository:
    """
    Repository for Keyword model operations.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_keyword(self, term: str, term_thai: Optional[str] = None, 
                       category: Optional[str] = None) -> Keyword:
        """
        Create a new keyword in the database.
        
        Args:
            term: Keyword term
            term_thai: Thai translation of the term
            category: Category of the keyword
            
        Returns:
            Created Keyword database model
        """
        keyword = Keyword(
            term=term,
            term_thai=term_thai,
            category=category
        )
        self.db_session.add(keyword)
        self.db_session.commit()
        self.db_session.refresh(keyword)
        return keyword
    
    def get_keyword_by_term(self, term: str) -> Optional[Keyword]:
        """
        Get a keyword by term.
        
        Args:
            term: Keyword term
            
        Returns:
            Keyword database model or None if not found
        """
        return self.db_session.query(Keyword).filter(Keyword.term == term).first()
    
    def get_or_create_keyword(self, term: str, term_thai: Optional[str] = None, 
                              category: Optional[str] = None) -> Keyword:
        """
        Get a keyword by term or create it if it doesn't exist.
        
        Args:
            term: Keyword term
            term_thai: Thai translation of the term
            category: Category of the keyword
            
        Returns:
            Keyword database model
        """
        keyword = self.get_keyword_by_term(term)
        if not keyword:
            keyword = self.create_keyword(term, term_thai, category)
        return keyword
    
    def get_keywords_by_category(self, category: str) -> List[Keyword]:
        """
        Get keywords by category.
        
        Args:
            category: Keyword category
            
        Returns:
            List of Keyword database models
        """
        return self.db_session.query(Keyword).filter(Keyword.category == category).all()


class ProcessingLogRepository:
    """
    Repository for ProcessingLog model operations.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_log(self, source_id: int, process_type: str, status: str, 
                   message: str, document_id: Optional[int] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> ProcessingLog:
        """
        Create a new processing log entry.
        
        Args:
            source_id: Source ID
            process_type: Type of process
            status: Status of the process
            message: Log message
            document_id: Document ID (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Created ProcessingLog database model
        """
        # Convert metadata to JSON string
        metadata_str = json.dumps(metadata) if metadata else None
        
        log = ProcessingLog(
            source_id=source_id,
            document_id=document_id,
            process_type=process_type,
            status=status,
            message=message,
            log_metadata=metadata_str
        )
        self.db_session.add(log)
        self.db_session.commit()
        self.db_session.refresh(log)
        return log