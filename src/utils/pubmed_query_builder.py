"""
PubMed query builder for constructing complex search queries.

This module provides utilities for building sophisticated search queries
for the PubMed API, with specific support for Thai Traditional Medicine research.
"""

from typing import List, Optional
from datetime import date
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ArticleType(Enum):
    """Enumeration of PubMed article types."""
    CLINICAL_TRIAL = "clinical trial"
    REVIEW = "review"
    RESEARCH_ARTICLE = "research article"
    CASE_REPORT = "case report"
    COMPARATIVE_STUDY = "comparative study"
    EVALUATION_STUDY = "evaluation study"
    JOURNAL_ARTICLE = "journal article"


class DateRange:
    """Represents a date range for filtering search results."""
    
    def __init__(self, start_date: date, end_date: date):
        """
        Initialize a DateRange.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
        """
        self.start_date = start_date
        self.end_date = end_date


class PubMedQueryBuilder:
    """
    Builder class for constructing complex PubMed search queries.
    
    This class provides a fluent interface for building sophisticated
    search queries tailored for Thai Traditional Medicine research.
    """
    
    def __init__(self):
        """Initialize the query builder."""
        self.query_parts = []
        self.filters = []
    
    def search(self, terms: str) -> 'PubMedQueryBuilder':
        """
        Add search terms to the query.
        
        Args:
            terms: Search terms to add
            
        Returns:
            Self for method chaining
        """
        self.query_parts.append(terms)
        return self
    
    def phrase_search(self, phrase: str) -> 'PubMedQueryBuilder':
        """
        Add a phrase search to the query (enclosed in quotes).
        
        Args:
            phrase: Phrase to search for
            
        Returns:
            Self for method chaining
        """
        self.query_parts.append(f'"{phrase}"')
        return self
    
    def field_search(self, terms: str, field: str) -> 'PubMedQueryBuilder':
        """
        Add a field-specific search to the query.
        
        Args:
            terms: Search terms
            field: Field to search in (e.g., 'title', 'abstract')
            
        Returns:
            Self for method chaining
        """
        self.query_parts.append(f"{terms}[{field}]")
        return self
    
    def and_words(self, words: List[str]) -> 'PubMedQueryBuilder':
        """
        Add words that must be present in results.
        
        Args:
            words: List of words that must be present
            
        Returns:
            Self for method chaining
        """
        for word in words:
            self.query_parts.append(word)
        return self
    
    def not_words(self, words: List[str]) -> 'PubMedQueryBuilder':
        """
        Add words that must NOT be present in results.
        
        Args:
            words: List of words that must not be present
            
        Returns:
            Self for method chaining
        """
        for word in words:
            self.filters.append(f"NOT {word}")
        return self
    
    def mesh_term(self, term: str) -> 'PubMedQueryBuilder':
        """
        Add a MeSH term search to the query.
        
        Args:
            term: MeSH term to search for
            
        Returns:
            Self for method chaining
        """
        self.query_parts.append(f"{term}[Mesh]")
        return self
    
    def date_range(self, date_range: DateRange) -> 'PubMedQueryBuilder':
        """
        Add a date range filter to the query.
        
        Args:
            date_range: DateRange object with start and end dates
            
        Returns:
            Self for method chaining
        """
        start_str = date_range.start_date.strftime("%Y/%m/%d")
        end_str = date_range.end_date.strftime("%Y/%m/%d")
        self.filters.append(f"{start_str}:{end_str}[Date - Publication]")
        return self
    
    def article_type(self, article_type: ArticleType) -> 'PubMedQueryBuilder':
        """
        Add an article type filter to the query.
        
        Args:
            article_type: ArticleType enum value
            
        Returns:
            Self for method chaining
        """
        self.filters.append(f"{article_type.value}[pt]")
        return self
    
    def language(self, language: str) -> 'PubMedQueryBuilder':
        """
        Add a language filter to the query.
        
        Args:
            language: Language to filter by (e.g., 'english', 'thai')
            
        Returns:
            Self for method chaining
        """
        self.filters.append(f"{language}[lang]")
        return self
    
    def journal(self, journal_name: str) -> 'PubMedQueryBuilder':
        """
        Add a journal filter to the query.
        
        Args:
            journal_name: Name of journal to filter by
            
        Returns:
            Self for method chaining
        """
        self.filters.append(f"{journal_name}[journal]")
        return self
    
    def build(self) -> str:
        """
        Build the final query string.
        
        Returns:
            Constructed query string for PubMed API
        """
        # Combine query parts with AND operators
        if not self.query_parts:
            query = ""
        elif len(self.query_parts) == 1:
            query = self.query_parts[0]
        else:
            query = " AND ".join(self.query_parts)
        
        # Add filters
        if self.filters:
            filter_str = " AND ".join(self.filters)
            if query:
                query = f"({query}) AND {filter_str}"
            else:
                query = filter_str
        
        logger.debug(f"Built PubMed query: {query}")
        return query


def build_thai_traditional_medicine_query(
    additional_terms: Optional[List[str]] = None,
    exclude_terms: Optional[List[str]] = None,
    date_range: Optional[DateRange] = None,
    article_types: Optional[List[ArticleType]] = None
) -> str:
    """
    Build a specialized query for Thai Traditional Medicine research.
    
    Args:
        additional_terms: Additional terms to include in the search
        exclude_terms: Terms to exclude from the search
        date_range: Date range to filter results
        article_types: Types of articles to include
        
    Returns:
        Constructed query string for PubMed API
    """
    builder = PubMedQueryBuilder()
    
    # Start with core terms for Thai Traditional Medicine
    builder.search("traditional medicine").and_words(["thai", "herbal"])
    
    # Add any additional terms
    if additional_terms:
        builder.and_words(additional_terms)
    
    # Exclude any terms
    if exclude_terms:
        builder.not_words(exclude_terms)
    
    # Add date range if specified
    if date_range:
        builder.date_range(date_range)
    
    # Add article types if specified
    if article_types:
        for article_type in article_types:
            builder.article_type(article_type)
    
    return builder.build()