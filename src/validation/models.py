"""
Data validation models for the Thai Traditional Medicine RAG Bot.

This module defines Pydantic models for data validation results and quality scoring.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ValidationStatus(str, Enum):
    """Enumeration of validation statuses."""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    SUSPECT = "suspect"
    NEEDS_REVIEW = "needs_review"


class QualityScoreCategory(str, Enum):
    """Enumeration of quality score categories."""
    TITLE = "title"
    ABSTRACT = "abstract"
    AUTHORS = "authors"
    PUBLICATION_DATE = "publication_date"
    LANGUAGE = "language"
    DOCUMENT_TYPE = "document_type"
    CONTENT = "content"
    METADATA = "metadata"


class ValidationResult(BaseModel):
    """
    Model for individual validation results.
    """
    field_name: str = Field(..., description="Name of the field being validated")
    status: ValidationStatus = Field(..., description="Validation status")
    message: Optional[str] = Field(None, description="Validation message")
    score: Optional[float] = Field(None, description="Quality score for this field", ge=0.0, le=1.0)
    details: Optional[Dict[str, Any]] = Field(None, description="Additional validation details")


class QualityScore(BaseModel):
    """
    Model for document quality scores.
    """
    overall_score: float = Field(..., description="Overall quality score", ge=0.0, le=1.0)
    category_scores: Dict[QualityScoreCategory, float] = Field(
        ..., 
        description="Scores for different categories",
        example={
            QualityScoreCategory.TITLE: 0.95,
            QualityScoreCategory.ABSTRACT: 0.85,
            QualityScoreCategory.AUTHORS: 0.90,
            QualityScoreCategory.PUBLICATION_DATE: 0.95,
            QualityScoreCategory.LANGUAGE: 1.0,
            QualityScoreCategory.DOCUMENT_TYPE: 0.90,
            QualityScoreCategory.CONTENT: 0.80,
            QualityScoreCategory.METADATA: 0.75
        }
    )
    weighted_scores: Optional[Dict[QualityScoreCategory, float]] = Field(
        None, 
        description="Weighted scores for different categories"
    )
    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Timestamp when validation was performed"
    )


class DocumentValidationResult(BaseModel):
    """
    Model for complete document validation results.
    """
    document_id: int = Field(..., description="ID of the document being validated")
    source_id: int = Field(..., description="ID of the source")
    external_id: str = Field(..., description="External ID from the source")
    status: ValidationStatus = Field(..., description="Overall validation status")
    validation_results: List[ValidationResult] = Field(
        ..., 
        description="Individual validation results for each field"
    )
    quality_score: QualityScore = Field(..., description="Quality score for the document")
    recommendations: Optional[List[str]] = Field(
        None, 
        description="Recommendations for improving document quality"
    )
    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Timestamp when validation was performed"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata about the validation process"
    )


class DeduplicationResult(BaseModel):
    """
    Model for deduplication results.
    """
    document_id: int = Field(..., description="ID of the document being checked")
    is_duplicate: bool = Field(..., description="Whether the document is a duplicate")
    duplicate_of: Optional[int] = Field(None, description="ID of the document it duplicates")
    similarity_score: Optional[float] = Field(
        None, 
        description="Similarity score with the duplicate document", 
        ge=0.0, 
        le=1.0
    )
    checked_documents: List[int] = Field(
        ..., 
        description="List of document IDs that were checked for duplication"
    )
    deduplication_timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Timestamp when deduplication was performed"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata about the deduplication process"
    )


class DataCleaningResult(BaseModel):
    """
    Model for data cleaning results.
    """
    document_id: int = Field(..., description="ID of the document being cleaned")
    fields_cleaned: List[str] = Field(..., description="List of fields that were cleaned")
    cleaning_operations: List[str] = Field(..., description="List of cleaning operations performed")
    cleaned_timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Timestamp when cleaning was performed"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata about the cleaning process"
    )


class ValidationError(Exception):
    """Base exception for validation errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}


class DocumentValidationError(ValidationError):
    """Exception for document validation errors."""
    pass


class QualityScoringError(ValidationError):
    """Exception for quality scoring errors."""
    pass


class DeduplicationError(ValidationError):
    """Exception for deduplication errors."""
    pass


class DataCleaningError(ValidationError):
    """Exception for data cleaning errors."""
    pass