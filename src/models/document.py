from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date

@dataclass
class Document:
    """
    Data class representing a document
    """
    id: Optional[int] = None
    source_id: Optional[int] = None
    external_id: Optional[str] = None  # Original document ID from source
    title: Optional[str] = None
    content: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[date] = None
    language: Optional[str] = None
    document_type: str = "research_paper"  # 'research_paper', 'clinical_study', 'book_chapter', etc.
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    processing_status: str = "pending"
    quality_score: Optional[float] = None
    validation_status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None