"""
Unit tests for advanced PubMed search query functionality.

These tests verify that our search query builder can construct
complex queries for Thai Traditional Medicine research.
"""

import sys
import os
import pytest
from datetime import datetime, date

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.pubmed_query_builder import (
    PubMedQueryBuilder,
    DateRange,
    ArticleType
)


class TestPubMedQueryBuilder:
    """Tests for the PubMedQueryBuilder class."""
    
    def test_basic_query_construction(self):
        """Test basic query construction."""
        builder = PubMedQueryBuilder()
        query = builder.search("traditional medicine").build()
        
        assert query == "traditional medicine"
    
    def test_thai_traditional_medicine_query(self):
        """Test constructing a query for Thai traditional medicine."""
        builder = PubMedQueryBuilder()
        query = builder.search("traditional medicine").and_words(["thai", "herbal"]).build()
        
        # Should contain all terms
        assert "traditional medicine" in query
        assert "thai" in query
        assert "herbal" in query
        # Should use AND operators
        assert " AND " in query
    
    def test_exclusion_query(self):
        """Test constructing a query with exclusions."""
        builder = PubMedQueryBuilder()
        query = builder.search("traditional medicine").not_words(["acupuncture", "chinese"]).build()
        
        assert "traditional medicine" in query
        assert "acupuncture" in query
        assert "chinese" in query
        # Should use AND NOT operators
        assert " AND NOT " in query
    
    def test_phrase_search(self):
        """Test constructing a phrase search query."""
        builder = PubMedQueryBuilder()
        query = builder.phrase_search("thai traditional medicine").build()
        
        assert query == '"thai traditional medicine"'
    
    def test_field_search(self):
        """Test constructing a field-specific search."""
        builder = PubMedQueryBuilder()
        query = builder.field_search("traditional medicine", "title").build()
        
        assert query == "traditional medicine[title]"
    
    def test_date_range_filter(self):
        """Test adding a date range filter."""
        builder = PubMedQueryBuilder()
        start_date = date(2020, 1, 1)
        end_date = date(2023, 12, 31)
        date_range = DateRange(start_date, end_date)
        query = builder.search("traditional medicine").date_range(date_range).build()
        
        # Should contain the date range filter
        assert "2020/01/01" in query
        assert "2023/12/31" in query
        assert "traditional medicine" in query
    
    def test_article_type_filter(self):
        """Test adding an article type filter."""
        builder = PubMedQueryBuilder()
        query = builder.search("traditional medicine").article_type(ArticleType.REVIEW).build()
        
        # Should contain the article type filter
        assert "traditional medicine" in query
        assert "review[pt]" in query
    
    def test_multiple_filters(self):
        """Test combining multiple filters."""
        builder = PubMedQueryBuilder()
        start_date = date(2020, 1, 1)
        end_date = date(2023, 12, 31)
        date_range = DateRange(start_date, end_date)
        query = (builder
                 .search("thai medicine")
                 .and_words(["herbal"])
                 .date_range(date_range)
                 .article_type(ArticleType.CLINICAL_TRIAL)
                 .build())
        
        # Should contain all components
        assert "thai medicine" in query
        assert "herbal" in query
        assert "2020/01/01" in query
        assert "2023/12/31" in query
        assert "clinical trial[pt]" in query
        assert " AND " in query
    
    def test_complex_query_with_exclusions(self):
        """Test a complex query with exclusions."""
        builder = PubMedQueryBuilder()
        query = (builder
                 .search("traditional medicine")
                 .and_words(["thai", "plant"])
                 .not_words(["chinese", "acupuncture"])
                 .build())
        
        # Should contain all terms with proper operators
        assert "traditional medicine" in query
        assert "thai" in query
        assert "plant" in query
        assert "chinese" in query
        assert "acupuncture" in query
        assert " AND " in query
        assert " AND NOT " in query
    
    def test_mesh_term_search(self):
        """Test searching with MeSH terms."""
        builder = PubMedQueryBuilder()
        query = builder.mesh_term("Medicine, Traditional").build()
        
        assert query == "Medicine, Traditional[Mesh]"
    
    def test_language_filter(self):
        """Test adding a language filter."""
        builder = PubMedQueryBuilder()
        query = builder.search("traditional medicine").language("english").build()
        
        assert "traditional medicine" in query
        assert "english[lang]" in query
    
    def test_journal_filter(self):
        """Test adding a journal filter."""
        builder = PubMedQueryBuilder()
        query = builder.search("traditional medicine").journal("J Ethnopharmacol").build()
        
        assert "traditional medicine" in query
        assert "J Ethnopharmacol[journal]" in query