"""
Integration tests for the PubMed query builder functionality.

These tests verify that our query builder works correctly with the real PubMed API.
"""

import sys
import os
import pytest
from datetime import date

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.connectors.pubmed import PubMedConnector
from src.models.source import Source
from src.utils.pubmed_query_builder import (
    PubMedQueryBuilder,
    DateRange,
    ArticleType
)


@pytest.mark.integration
def test_pubmed_query_builder_integration():
    """Integration test for PubMed query builder with real API"""
    # Create a source object
    source = Source(
        id=1,
        name="PubMed",
        type="academic",
        url="https://pubmed.ncbi.nlm.nih.gov/",
        api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        access_method="api",
        reliability_score=5,
        metadata={"api_key": None}  # No API key for testing
    )
    
    # Create connector
    connector = PubMedConnector(source)
    
    # Test 1: Basic query builder
    builder = PubMedQueryBuilder()
    builder.search("traditional medicine").and_words(["thai"])
    
    pmids = connector.search_articles(builder, 3)
    
    # Assertions
    assert isinstance(pmids, list)
    assert len(pmids) <= 3
    
    # Test 2: Complex query with filters
    builder2 = PubMedQueryBuilder()
    start_date = date(2020, 1, 1)
    end_date = date(2023, 12, 31)
    date_range = DateRange(start_date, end_date)
    
    query = (builder2
             .search("thai medicine")
             .and_words(["herbal"])
             .date_range(date_range)
             .article_type(ArticleType.REVIEW)
             .build())
    
    pmids2 = connector.search_articles(query, 3)
    
    # Assertions
    assert isinstance(pmids2, list)
    assert len(pmids2) <= 3
    
    # Test 3: Phrase search
    builder3 = PubMedQueryBuilder()
    builder3.phrase_search("thai traditional medicine")
    
    pmids3 = connector.search_articles(builder3, 3)
    
    # Assertions
    assert isinstance(pmids3, list)
    assert len(pmids3) <= 3


@pytest.mark.integration
def test_thai_traditional_medicine_specialized_query():
    """Test the specialized Thai Traditional Medicine query function"""
    from src.utils.pubmed_query_builder import build_thai_traditional_medicine_query, ArticleType
    
    # Create a source object
    source = Source(
        id=1,
        name="PubMed",
        type="academic",
        url="https://pubmed.ncbi.nlm.nih.gov/",
        api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        access_method="api",
        reliability_score=5,
        metadata={"api_key": None}  # No API key for testing
    )
    
    # Create connector
    connector = PubMedConnector(source)
    
    # Test the specialized query function
    query = build_thai_traditional_medicine_query(
        additional_terms=["herbal", "plant"],
        exclude_terms=["chinese", "acupuncture"],
        article_types=[ArticleType.REVIEW]
    )
    
    pmids = connector.search_articles(query, 3)
    
    # Assertions
    assert isinstance(pmids, list)
    assert len(pmids) <= 3