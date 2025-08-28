"""
Pydantic models for PubMed data structures.

These models define the structured representation of PubMed articles
and related data entities, enabling type-safe parsing and validation
of XML data from the PubMed API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PubmedAuthor(BaseModel):
    """
    Represents an author of a PubMed article.
    """
    # Author's full name
    name: Optional[str] = None
    
    # Author's affiliation
    affiliation: Optional[str] = None
    
    # ORCID identifier
    orcid: Optional[str] = None


class PubmedJournal(BaseModel):
    """
    Represents journal information for a PubMed article.
    """
    # Journal title
    title: Optional[str] = None
    
    # ISSN identifier
    issn: Optional[str] = None
    
    # Volume number
    volume: Optional[str] = None
    
    # Issue number
    issue: Optional[str] = None
    
    # Publication date
    publication_date: Optional[datetime] = None


class PubmedArticle(BaseModel):
    """
    Represents a complete PubMed article with all relevant metadata.
    """
    # PubMed ID (PMID)
    pmid: str = Field(..., description="PubMed ID")
    
    # Article title
    title: Optional[str] = None
    
    # Article abstract
    abstract: Optional[str] = None
    
    # List of authors
    authors: List[PubmedAuthor] = Field(default_factory=list)
    
    # Journal information
    journal: Optional[PubmedJournal] = None
    
    # Publication date
    publication_date: Optional[datetime] = None
    
    # Article type (e.g., research article, review, etc.)
    article_type: Optional[str] = None
    
    # Keywords associated with the article
    keywords: List[str] = Field(default_factory=list)
    
    # DOI identifier
    doi: Optional[str] = None
    
    # Language of the article
    language: Optional[str] = "eng"
    
    # Country of publication
    country: Optional[str] = None
    
    # Mesh terms
    mesh_terms: List[str] = Field(default_factory=list)
    
    # Chemical list
    chemicals: List[str] = Field(default_factory=list)
    
    # References (if available)
    references: List[str] = Field(default_factory=list)
    
    # Raw XML content (for debugging/fallback)
    raw_xml: Optional[str] = None
    
    @field_validator('pmid')
    @classmethod
    def validate_pmid(cls, v):
        """Validate that PMID is a valid string representation of a number."""
        if not v.isdigit():
            raise ValueError('PMID must be a numeric string')
        return v
    
    @field_validator('doi')
    @classmethod
    def validate_doi(cls, v):
        """Basic validation for DOI format."""
        if v and not v.startswith('10.'):
            raise ValueError('DOI should start with "10."')
        return v