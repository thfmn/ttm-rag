"""
Database models for the Thai Traditional Medicine RAG Bot.

This module defines SQLAlchemy models that map to our database tables.
These models are based on our schema design and include vector embeddings
for RAG functionality.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, Table, Index, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from src.database.config import Base

# Association table for document-keyword many-to-many relationship
document_keyword_association = Table(
    'document_keyword_association',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('keyword_id', Integer, ForeignKey('keywords.id'), primary_key=True),
    extend_existing=True
)

class Source(Base):
    """
    Database model for data sources.
    """
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'government', 'academic', 'clinical', etc.
    url = Column(Text)
    api_endpoint = Column(Text)
    access_method = Column(String(50))  # 'api', 'scraping', 'manual'
    reliability_score = Column(Integer, nullable=False)  # 1-5 scale
    language = Column(String(10), default='th')
    is_active = Column(Boolean, default=True)
    source_metadata = Column(Text)  # Store as JSON string for compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="source")

class Document(Base):
    """
    Database model for documents.
    """
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)
    external_id = Column(String(255), index=True)  # Original document ID from source
    title = Column(Text)
    content = Column(Text)
    abstract = Column(Text)
    authors = Column(Text)  # Store as JSON string for compatibility
    publication_date = Column(DateTime(timezone=True))
    language = Column(String(10))
    document_type = Column(String(50))  # 'research_paper', 'clinical_study', 'book_chapter', etc.
    file_path = Column(Text)
    file_type = Column(String(20))
    file_size = Column(Integer)
    processing_status = Column(String(20), default='pending')
    quality_score = Column(Float)
    validation_status = Column(String(20), default='pending')
    document_metadata = Column(Text)  # Store as JSON string for compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Vector embedding for RAG functionality (using pgvector)
    # This will store the document embedding as a vector of floats
    embedding = Column(LargeBinary)  # Will store as bytea in PostgreSQL
    
    # Relationships
    source = relationship("Source", back_populates="documents")
    keywords = relationship(
        "Keyword", 
        secondary=document_keyword_association, 
        back_populates="documents"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_documents_source_id', 'source_id'),
        Index('idx_documents_external_id', 'external_id'),
        Index('idx_documents_title_gin', 'title'),
        Index('idx_documents_publication_date', 'publication_date'),
    )

class Keyword(Base):
    """
    Database model for keywords and topics.
    """
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(255), nullable=False, unique=True, index=True)
    term_thai = Column(String(255), index=True)
    category = Column(String(100))  # 'herb', 'treatment', 'condition', 'technique'
    frequency = Column(Integer, default=0)
    validated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    documents = relationship(
        "Document", 
        secondary=document_keyword_association, 
        back_populates="keywords"
    )

class ProcessingLog(Base):
    """
    Database model for processing logs.
    """
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), index=True)
    process_type = Column(String(50))  # 'ingestion', 'validation', 'extraction', 'indexing'
    status = Column(String(20))  # 'success', 'failed', 'warning'
    message = Column(Text)
    execution_time = Column(String)  # Interval as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    log_metadata = Column(Text)  # Store as JSON string for compatibility
    
    # Relationships
    document = relationship("Document")
    source = relationship("Source")

# Create indexes for full-text search
# Note: In PostgreSQL, we would typically use pg_trgm or full-text search extensions
# For now, we're using basic indexes. In production, you might want to add:
# CREATE EXTENSION IF NOT EXISTS pg_trgm;
# CREATE INDEX idx_documents_title_trgm ON documents USING gin(title gin_trgm_ops);