"""
Validation service for the Thai Traditional Medicine RAG Bot.

This module provides validation services for documents fetched from data sources,
including quality scoring, deduplication, and data cleaning.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import re
import hashlib

from src.validation.models import (
    ValidationResult, 
    QualityScore, 
    DocumentValidationResult, 
    ValidationStatus,
    QualityScoreCategory,
    DeduplicationResult,
    DataCleaningResult,
    DocumentValidationError,
    QualityScoringError,
    DeduplicationError,
    DataCleaningError
)
from src.models.document import Document
from src.models.pubmed import PubmedArticle
from src.database.models import Document as DBDocument
from src.database.repository import DocumentRepository
from src.utils.text_processing import (
    calculate_text_quality_score,
    detect_language,
    extract_keywords,
    normalize_text,
    remove_html_tags
)

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Service for validating documents and ensuring data quality.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the validation service.
        
        Args:
            db_session: Optional database session for accessing existing documents
        """
        self.db_session = db_session
        self.document_repository = DocumentRepository(db_session) if db_session else None
    
    def validate_document(self, document: Document) -> DocumentValidationResult:
        """
        Validate a document and calculate its quality score.
        
        Args:
            document: Document to validate
            
        Returns:
            DocumentValidationResult with validation results and quality score
            
        Raises:
            DocumentValidationError: If validation fails
        """
        try:
            logger.debug(f"Validating document {document.external_id}")
            
            # Perform individual field validations
            validation_results = self._validate_document_fields(document)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(document, validation_results)
            
            # Determine overall status
            status = self._determine_validation_status(validation_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(document, validation_results)
            
            # Create validation result
            result = DocumentValidationResult(
                document_id=document.id or 0,
                source_id=document.source_id,
                external_id=document.external_id,
                status=status,
                validation_results=validation_results,
                quality_score=quality_score,
                recommendations=recommendations,
                metadata={
                    "validation_timestamp": datetime.utcnow().isoformat(),
                    "validation_service_version": "1.0.0"
                }
            )
            
            logger.info(f"Document {document.external_id} validation completed with status: {status}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating document {document.external_id}: {e}")
            raise DocumentValidationError(
                f"Error validating document {document.external_id}: {e}",
                context={"document_id": document.external_id, "error": str(e)}
            )
    
    def validate_pubmed_article(self, article: PubmedArticle) -> DocumentValidationResult:
        """
        Validate a PubMed article and calculate its quality score.
        
        Args:
            article: PubMed article to validate
            
        Returns:
            DocumentValidationResult with validation results and quality score
            
        Raises:
            DocumentValidationError: If validation fails
        """
        try:
            logger.debug(f"Validating PubMed article {article.pmid}")
            
            # Convert to Document model for validation
            document = self._convert_pubmed_to_document(article)
            
            # Validate the document
            return self.validate_document(document)
            
        except Exception as e:
            logger.error(f"Error validating PubMed article {article.pmid}: {e}")
            raise DocumentValidationError(
                f"Error validating PubMed article {article.pmid}: {e}",
                context={"pmid": article.pmid, "error": str(e)}
            )
    
    def _validate_document_fields(self, document: Document) -> List[ValidationResult]:
        """
        Validate individual fields of a document.
        
        Args:
            document: Document to validate
            
        Returns:
            List of ValidationResult objects
        """
        validation_results = []
        
        # Validate title
        title_result = self._validate_title(document.title)
        validation_results.append(title_result)
        
        # Validate abstract
        abstract_result = self._validate_abstract(document.abstract)
        validation_results.append(abstract_result)
        
        # Validate authors
        authors_result = self._validate_authors(document.authors)
        validation_results.append(authors_result)
        
        # Validate publication date
        pub_date_result = self._validate_publication_date(document.publication_date)
        validation_results.append(pub_date_result)
        
        # Validate language
        language_result = self._validate_language(document.language)
        validation_results.append(language_result)
        
        # Validate document type
        doc_type_result = self._validate_document_type(document.document_type)
        validation_results.append(doc_type_result)
        
        # Validate content
        content_result = self._validate_content(document.content)
        validation_results.append(content_result)
        
        # Validate metadata
        metadata_result = self._validate_metadata(document.metadata)
        validation_results.append(metadata_result)
        
        return validation_results
    
    def _validate_title(self, title: Optional[str]) -> ValidationResult:
        """
        Validate document title.
        
        Args:
            title: Document title
            
        Returns:
            ValidationResult for title validation
        """
        if not title:
            return ValidationResult(
                field_name="title",
                status=ValidationStatus.INVALID,
                message="Title is missing",
                score=0.0
            )
        
        # Check title length
        title_length = len(title.strip())
        if title_length < 5:
            return ValidationResult(
                field_name="title",
                status=ValidationStatus.INVALID,
                message="Title is too short",
                score=0.0
            )
        
        if title_length > 500:
            return ValidationResult(
                field_name="title",
                status=ValidationStatus.INVALID,
                message="Title is too long",
                score=0.0
            )
        
        # Calculate quality score based on length and content
        quality_score = min(1.0, title_length / 100.0)  # Normalize to 0-1 scale
        
        return ValidationResult(
            field_name="title",
            status=ValidationStatus.VALID,
            message="Title is valid",
            score=quality_score,
            details={"title_length": title_length}
        )
    
    def _validate_abstract(self, abstract: Optional[str]) -> ValidationResult:
        """
        Validate document abstract.
        
        Args:
            abstract: Document abstract
            
        Returns:
            ValidationResult for abstract validation
        """
        if not abstract:
            return ValidationResult(
                field_name="abstract",
                status=ValidationStatus.INVALID,
                message="Abstract is missing",
                score=0.0
            )
        
        # Check abstract length
        abstract_length = len(abstract.strip())
        if abstract_length < 50:
            return ValidationResult(
                field_name="abstract",
                status=ValidationStatus.INVALID,
                message="Abstract is too short",
                score=0.0
            )
        
        if abstract_length > 10000:
            return ValidationResult(
                field_name="abstract",
                status=ValidationStatus.INVALID,
                message="Abstract is too long",
                score=0.0
            )
        
        # Calculate quality score based on length and content
        quality_score = min(1.0, abstract_length / 1000.0)  # Normalize to 0-1 scale
        
        return ValidationResult(
            field_name="abstract",
            status=ValidationStatus.VALID,
            message="Abstract is valid",
            score=quality_score,
            details={"abstract_length": abstract_length}
        )
    
    def _validate_authors(self, authors: Optional[List[str]]) -> ValidationResult:
        """
        Validate document authors.
        
        Args:
            authors: List of document authors
            
        Returns:
            ValidationResult for authors validation
        """
        if not authors or len(authors) == 0:
            return ValidationResult(
                field_name="authors",
                status=ValidationStatus.INVALID,
                message="Authors are missing",
                score=0.0
            )
        
        # Check number of authors
        if len(authors) > 100:
            return ValidationResult(
                field_name="authors",
                status=ValidationStatus.INVALID,
                message="Too many authors",
                score=0.0
            )
        
        # Calculate quality score based on number of authors
        quality_score = min(1.0, len(authors) / 10.0)  # Normalize to 0-1 scale
        
        return ValidationResult(
            field_name="authors",
            status=ValidationStatus.VALID,
            message="Authors are valid",
            score=quality_score,
            details={"author_count": len(authors)}
        )
    
    def _validate_publication_date(self, pub_date: Optional[datetime]) -> ValidationResult:
        """
        Validate document publication date.
        
        Args:
            pub_date: Document publication date
            
        Returns:
            ValidationResult for publication date validation
        """
        if not pub_date:
            return ValidationResult(
                field_name="publication_date",
                status=ValidationStatus.INVALID,
                message="Publication date is missing",
                score=0.0
            )
        
        # Check if date is in the future
        if pub_date > datetime.utcnow():
            return ValidationResult(
                field_name="publication_date",
                status=ValidationStatus.INVALID,
                message="Publication date is in the future",
                score=0.0
            )
        
        # Check if date is too old (before 1900)
        if pub_date.year < 1900:
            return ValidationResult(
                field_name="publication_date",
                status=ValidationStatus.INVALID,
                message="Publication date is too old",
                score=0.0
            )
        
        # Calculate quality score based on recency
        years_since_publication = (datetime.utcnow() - pub_date).days / 365.25
        quality_score = max(0.0, min(1.0, 1.0 - (years_since_publication / 50.0)))
        
        return ValidationResult(
            field_name="publication_date",
            status=ValidationStatus.VALID,
            message="Publication date is valid",
            score=quality_score,
            details={"publication_year": pub_date.year, "years_since_publication": years_since_publication}
        )
    
    def _validate_language(self, language: Optional[str]) -> ValidationResult:
        """
        Validate document language.
        
        Args:
            language: Document language code
            
        Returns:
            ValidationResult for language validation
        """
        if not language:
            return ValidationResult(
                field_name="language",
                status=ValidationStatus.INVALID,
                message="Language is missing",
                score=0.0
            )
        
        # Check if language is a valid ISO 639-1 code
        valid_languages = {"th", "en", "eng", "tha"}  # Add more as needed
        if language.lower() not in valid_languages:
            return ValidationResult(
                field_name="language",
                status=ValidationStatus.INVALID,
                message=f"Language '{language}' is not supported",
                score=0.0
            )
        
        # Calculate quality score (1.0 for supported languages)
        quality_score = 1.0
        
        return ValidationResult(
            field_name="language",
            status=ValidationStatus.VALID,
            message="Language is valid",
            score=quality_score,
            details={"language_code": language}
        )
    
    def _validate_document_type(self, doc_type: Optional[str]) -> ValidationResult:
        """
        Validate document type.
        
        Args:
            doc_type: Document type
            
        Returns:
            ValidationResult for document type validation
        """
        if not doc_type:
            return ValidationResult(
                field_name="document_type",
                status=ValidationStatus.INVALID,
                message="Document type is missing",
                score=0.0
            )
        
        # Check if document type is valid
        valid_types = {
            "research_paper", "clinical_study", "review", "case_report", 
            "book_chapter", "conference_paper", "thesis", "other"
        }
        if doc_type.lower() not in valid_types:
            return ValidationResult(
                field_name="document_type",
                status=ValidationStatus.INVALID,
                message=f"Document type '{doc_type}' is not supported",
                score=0.0
            )
        
        # Calculate quality score (1.0 for supported types)
        quality_score = 1.0
        
        return ValidationResult(
                field_name="document_type",
                status=ValidationStatus.VALID,
                message="Document type is valid",
                score=quality_score,
                details={"document_type": doc_type}
            )
    
    def _validate_content(self, content: Optional[str]) -> ValidationResult:
        """
        Validate document content.
        
        Args:
            content: Document content
            
        Returns:
            ValidationResult for content validation
        """
        if not content:
            return ValidationResult(
                field_name="content",
                status=ValidationStatus.INVALID,
                message="Content is missing",
                score=0.0
            )
        
        # Check content length
        content_length = len(content.strip())
        if content_length < 100:
            return ValidationResult(
                field_name="content",
                status=ValidationStatus.INVALID,
                message="Content is too short",
                score=0.0
            )
        
        # Calculate quality score based on length
        quality_score = min(1.0, content_length / 10000.0)  # Normalize to 0-1 scale
        
        return ValidationResult(
            field_name="content",
            status=ValidationStatus.VALID,
            message="Content is valid",
            score=quality_score,
            details={"content_length": content_length}
        )
    
    def _validate_metadata(self, metadata: Optional[Dict[str, Any]]) -> ValidationResult:
        """
        Validate document metadata.
        
        Args:
            metadata: Document metadata
            
        Returns:
            ValidationResult for metadata validation
        """
        if not metadata:
            return ValidationResult(
                field_name="metadata",
                status=ValidationStatus.INVALID,
                message="Metadata is missing",
                score=0.0
            )
        
        # Check if metadata has required fields
        required_fields = {"doi", "journal"}
        missing_fields = required_fields - set(metadata.keys())
        
        if missing_fields:
            return ValidationResult(
                field_name="metadata",
                status=ValidationStatus.INVALID,
                message=f"Metadata is missing required fields: {missing_fields}",
                score=0.0
            )
        
        # Check DOI format
        doi = metadata.get("doi")
        if doi and not doi.startswith("10."):
            return ValidationResult(
                field_name="metadata",
                status=ValidationStatus.INVALID,
                message="DOI format is invalid",
                score=0.0,
                details={"doi": doi}
            )
        
        # Calculate quality score based on completeness
        total_fields = len(metadata)
        quality_score = min(1.0, total_fields / 10.0)  # Normalize to 0-1 scale
        
        return ValidationResult(
            field_name="metadata",
            status=ValidationStatus.VALID,
            message="Metadata is valid",
            score=quality_score,
            details={"metadata_fields": list(metadata.keys()), "field_count": total_fields}
        )
    
    def _calculate_quality_score(self, document: Document, validation_results: List[ValidationResult]) -> QualityScore:
        """
        Calculate overall quality score for a document.
        
        Args:
            document: Document to score
            validation_results: Individual validation results
            
        Returns:
            QualityScore with overall and category scores
        """
        try:
            # Calculate category scores
            category_scores = {}
            
            # Extract scores from validation results
            for result in validation_results:
                if result.score is not None:
                    # Map field names to categories
                    field_to_category = {
                        "title": QualityScoreCategory.TITLE,
                        "abstract": QualityScoreCategory.ABSTRACT,
                        "authors": QualityScoreCategory.AUTHORS,
                        "publication_date": QualityScoreCategory.PUBLICATION_DATE,
                        "language": QualityScoreCategory.LANGUAGE,
                        "document_type": QualityScoreCategory.DOCUMENT_TYPE,
                        "content": QualityScoreCategory.CONTENT,
                        "metadata": QualityScoreCategory.METADATA
                    }
                    
                    category = field_to_category.get(result.field_name)
                    if category:
                        category_scores[category] = result.score
            
            # Calculate overall score as average of category scores
            if category_scores:
                overall_score = sum(category_scores.values()) / len(category_scores)
            else:
                overall_score = 0.0
            
            # Create quality score object
            quality_score = QualityScore(
                overall_score=overall_score,
                category_scores=category_scores
            )
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating quality score for document {document.external_id}: {e}")
            raise QualityScoringError(
                f"Error calculating quality score for document {document.external_id}: {e}",
                context={"document_id": document.external_id, "error": str(e)}
            )
    
    def _determine_validation_status(self, validation_results: List[ValidationResult]) -> ValidationStatus:
        """
        Determine overall validation status based on individual results.
        
        Args:
            validation_results: Individual validation results
            
        Returns:
            Overall validation status
        """
        # Check if any results are invalid
        invalid_results = [r for r in validation_results if r.status == ValidationStatus.INVALID]
        if invalid_results:
            return ValidationStatus.INVALID
        
        # Check if any results need review
        review_results = [r for r in validation_results if r.status == ValidationStatus.NEEDS_REVIEW]
        if review_results:
            return ValidationStatus.NEEDS_REVIEW
        
        # Check if any results are suspect
        suspect_results = [r for r in validation_results if r.status == ValidationStatus.SUSPECT]
        if suspect_results:
            return ValidationStatus.SUSPECT
        
        # All results are valid
        return ValidationStatus.VALID
    
    def _generate_recommendations(self, document: Document, validation_results: List[ValidationResult]) -> List[str]:
        """
        Generate recommendations for improving document quality.
        
        Args:
            document: Document to generate recommendations for
            validation_results: Individual validation results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Add recommendations based on validation results
        for result in validation_results:
            if result.status in [ValidationStatus.INVALID, ValidationStatus.SUSPECT, ValidationStatus.NEEDS_REVIEW]:
                if result.message:
                    recommendations.append(f"Field '{result.field_name}': {result.message}")
        
        # Add general recommendations
        if document.title and len(document.title.strip()) < 20:
            recommendations.append("Consider providing a more descriptive title")
        
        if document.abstract and len(document.abstract.strip()) < 200:
            recommendations.append("Consider providing a more detailed abstract")
        
        if not document.authors or len(document.authors) == 0:
            recommendations.append("Consider adding author information")
        
        if not document.publication_date:
            recommendations.append("Consider adding publication date")
        
        return recommendations
    
    def _convert_pubmed_to_document(self, article: PubmedArticle) -> Document:
        """
        Convert a PubMed article to a Document model.
        
        Args:
            article: PubMed article to convert
            
        Returns:
            Document model
        """
        # Extract authors
        authors = [author.name for author in article.authors] if article.authors else None
        
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
        
        # Remove None values from metadata
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        # Create document
        document = Document(
            source_id=1,  # PubMed source ID
            external_id=article.pmid,
            title=article.title,
            content=article.raw_xml,  # Store raw XML for now, could be full text later
            abstract=article.abstract,
            authors=authors,
            publication_date=None,  # Would need to parse datetime from article.publication_date
            language=article.language,
            document_type=article.article_type or "research_paper",
            quality_score=0.95,  # Default quality score, would be calculated in a full implementation
            metadata=metadata if metadata else None
        )
        
        return document
    
    def deduplicate_document(self, document: Document) -> DeduplicationResult:
        """
        Check if a document is a duplicate of an existing document.
        
        Args:
            document: Document to check for duplication
            
        Returns:
            DeduplicationResult with duplication check results
            
        Raises:
            DeduplicationError: If deduplication fails
        """
        try:
            logger.debug(f"Deduplicating document {document.external_id}")
            
            # If we don't have a database session, we can't check for duplicates
            if not self.db_session or not self.document_repository:
                return DeduplicationResult(
                    document_id=document.id or 0,
                    is_duplicate=False,
                    checked_documents=[],
                    metadata={"reason": "No database session available"}
                )
            
            # Generate content hash for comparison
            content_hash = self._generate_content_hash(document)
            
            # Check for existing documents with similar content
            existing_documents = self.document_repository.search_documents(document.title or "", 100)
            
            # Compare with existing documents
            for existing_doc in existing_documents:
                # Skip the same document
                if existing_doc.id == document.id:
                    continue
                
                # Generate hash for existing document
                existing_hash = self._generate_content_hash_from_db(existing_doc)
                
                # Compare hashes
                if content_hash == existing_hash:
                    # Exact duplicate found
                    return DeduplicationResult(
                        document_id=document.id or 0,
                        is_duplicate=True,
                        duplicate_of=existing_doc.id,
                        similarity_score=1.0,
                        checked_documents=[doc.id for doc in existing_documents],
                        metadata={"reason": "Exact content match"}
                    )
                
                # Calculate similarity score
                similarity = self._calculate_similarity(document, existing_doc)
                if similarity > 0.95:  # Threshold for near-duplicates
                    return DeduplicationResult(
                        document_id=document.id or 0,
                        is_duplicate=True,
                        duplicate_of=existing_doc.id,
                        similarity_score=similarity,
                        checked_documents=[doc.id for doc in existing_documents],
                        metadata={"reason": "High similarity content", "threshold": 0.95}
                    )
            
            # No duplicates found
            return DeduplicationResult(
                document_id=document.id or 0,
                is_duplicate=False,
                checked_documents=[doc.id for doc in existing_documents],
                metadata={"reason": "No duplicates found"}
            )
            
        except Exception as e:
            logger.error(f"Error deduplicating document {document.external_id}: {e}")
            raise DeduplicationError(
                f"Error deduplicating document {document.external_id}: {e}",
                context={"document_id": document.external_id, "error": str(e)}
            )
    
    def _generate_content_hash(self, document: Document) -> str:
        """
        Generate a hash of the document content for comparison.
        
        Args:
            document: Document to hash
            
        Returns:
            Hash of the document content
        """
        # Combine key fields for hashing
        content_to_hash = f"{document.title or ''}{document.abstract or ''}{document.content or ''}"
        return hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()
    
    def _generate_content_hash_from_db(self, db_document: DBDocument) -> str:
        """
        Generate a hash of a database document content for comparison.
        
        Args:
            db_document: Database document to hash
            
        Returns:
            Hash of the document content
        """
        # Combine key fields for hashing
        content_to_hash = f"{db_document.title or ''}{db_document.abstract or ''}{db_document.content or ''}"
        return hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()
    
    def _calculate_similarity(self, document1: Document, document2: DBDocument) -> float:
        """
        Calculate similarity between two documents.
        
        Args:
            document1: First document
            document2: Second document (database document)
            
        Returns:
            Similarity score between 0 and 1
        """
        # For now, we'll use a simple approach based on title similarity
        # In a full implementation, we'd use more sophisticated techniques
        
        title1 = document1.title or ""
        title2 = document2.title or ""
        
        # Convert to lowercase and remove punctuation
        title1_clean = re.sub(r'[^\w\s]', '', title1.lower())
        title2_clean = re.sub(r'[^\w\s]', '', title2.lower())
        
        # Split into words
        words1 = set(title1_clean.split())
        words2 = set(title2_clean.split())
        
        # Calculate Jaccard similarity
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def clean_document(self, document: Document) -> DataCleaningResult:
        """
        Clean a document by removing HTML tags, normalizing text, etc.
        
        Args:
            document: Document to clean
            
        Returns:
            DataCleaningResult with cleaning results
            
        Raises:
            DataCleaningError: If cleaning fails
        """
        try:
            logger.debug(f"Cleaning document {document.external_id}")
            
            fields_cleaned = []
            cleaning_operations = []
            
            # Clean title
            if document.title:
                original_title = document.title
                document.title = remove_html_tags(normalize_text(document.title))
                if document.title != original_title:
                    fields_cleaned.append("title")
                    cleaning_operations.append("remove_html_tags")
                    cleaning_operations.append("normalize_text")
            
            # Clean abstract
            if document.abstract:
                original_abstract = document.abstract
                document.abstract = remove_html_tags(normalize_text(document.abstract))
                if document.abstract != original_abstract:
                    fields_cleaned.append("abstract")
                    cleaning_operations.append("remove_html_tags")
                    cleaning_operations.append("normalize_text")
            
            # Clean content
            if document.content:
                original_content = document.content
                document.content = remove_html_tags(normalize_text(document.content))
                if document.content != original_content:
                    fields_cleaned.append("content")
                    cleaning_operations.append("remove_html_tags")
                    cleaning_operations.append("normalize_text")
            
            # Create cleaning result
            result = DataCleaningResult(
                document_id=document.id or 0,
                fields_cleaned=fields_cleaned,
                cleaning_operations=cleaning_operations,
                metadata={"cleaning_service_version": "1.0.0"}
            )
            
            logger.info(f"Document {document.external_id} cleaning completed")
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning document {document.external_id}: {e}")
            raise DataCleaningError(
                f"Error cleaning document {document.external_id}: {e}",
                context={"document_id": document.external_id, "error": str(e)}
            )


# Global validation service instance
validation_service = ValidationService()