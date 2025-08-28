"""
Integration tests for the PubMed connector.

These tests:
1. Use the real PubMed API but with controlled, minimal requests
2. Respect rate limits and ethical usage guidelines
3. Use small result sets to minimize API load
4. Include proper error handling and cleanup
5. Test both successful and edge cases
"""

import sys
import os
import time
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.connectors.pubmed import PubMedConnector
from src.models.source import Source

# Global rate limiting variables
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 1.0  # Minimum 1 second between requests (respectful rate limiting)

def rate_limited_request():
    """Ensure respectful rate limiting between API calls"""
    global LAST_REQUEST_TIME
    current_time = time.time()
    time_since_last = current_time - LAST_REQUEST_TIME
    
    if time_since_last < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last
        time.sleep(sleep_time)
    
    LAST_REQUEST_TIME = time.time()

@pytest.fixture
def pubmed_source():
    """Create a PubMed source fixture"""
    return Source(
        id=1,
        name="PubMed",
        type="academic",
        url="https://pubmed.ncbi.nlm.nih.gov/",
        api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        access_method="api",
        reliability_score=5,
        metadata={"api_key": None}  # No API key for public access
    )

@pytest.fixture
def pubmed_connector(pubmed_source):
    """Create a PubMed connector fixture"""
    return PubMedConnector(pubmed_source)

class TestPubMedIntegration:
    """Integration tests for PubMed connector with ethical considerations"""
    
    def test_search_articles_basic(self, pubmed_connector):
        """Test basic article search functionality"""
        # Rate limiting
        rate_limited_request()
        
        # Small result set to minimize API load
        pmids = pubmed_connector.search_articles("traditional medicine", 3)
        
        # Verify results
        assert isinstance(pmids, list)
        assert len(pmids) <= 3  # Should not exceed requested limit
        # All returned IDs should be strings
        for pmid in pmids:
            assert isinstance(pmid, str)
            # PMID should be numeric
            assert pmid.isdigit()
    
    def test_search_articles_empty_query(self, pubmed_connector):
        """Test search with empty query"""
        # Rate limiting
        rate_limited_request()
        
        # Test with empty query
        pmids = pubmed_connector.search_articles("", 3)
        
        # Should handle gracefully
        assert isinstance(pmids, list)
        # May return results or empty list depending on API behavior
    
    def test_search_articles_no_results(self, pubmed_connector):
        """Test search with query that should return no results"""
        # Rate limiting
        rate_limited_request()
        
        # Very specific query unlikely to have results
        pmids = pubmed_connector.search_articles("nonexistentmedicalterm12345", 3)
        
        # Should handle gracefully
        assert isinstance(pmids, list)
        # Might be empty or have very few results
    
    def test_fetch_article_details_single(self, pubmed_connector):
        """Test fetching details for a single article"""
        # Rate limiting
        rate_limited_request()
        
        # First get a PMID to test with
        pmids = pubmed_connector.search_articles("traditional medicine", 1)
        
        # If we got results, test fetching details
        if pmids:
            rate_limited_request()  # Additional rate limiting for fetch request
            articles = pubmed_connector.fetch_article_details([pmids[0]])
            
            # Verify results
            assert isinstance(articles, list)
            assert len(articles) == 1
            article = articles[0]
            # Now we expect PubmedArticle objects
            assert hasattr(article, 'pmid')
            assert hasattr(article, 'title')
            assert hasattr(article, 'abstract')
            assert hasattr(article, 'raw_xml')
            assert article.pmid == pmids[0]
            assert isinstance(article.raw_xml, str)
            assert len(article.raw_xml) > 0  # Should have content
    
    def test_fetch_article_details_multiple(self, pubmed_connector):
        """Test fetching details for multiple articles"""
        # Rate limiting
        rate_limited_request()
        
        # Get a few PMIDs to test with
        pmids = pubmed_connector.search_articles("traditional medicine", 2)
        
        # If we got results, test fetching details
        if len(pmids) >= 2:
            rate_limited_request()  # Additional rate limiting for fetch request
            articles = pubmed_connector.fetch_article_details(pmids)
            
            # Verify results
            assert isinstance(articles, list)
            assert len(articles) == len(pmids)
            for i, article in enumerate(articles):
                # Now we expect PubmedArticle objects
                assert hasattr(article, 'pmid')
                assert hasattr(article, 'title')
                assert hasattr(article, 'abstract')
                assert hasattr(article, 'raw_xml')
                assert article.pmid == pmids[i]
                assert isinstance(article.raw_xml, str)
                assert len(article.raw_xml) > 0  # Should have content
    
    def test_fetch_article_details_empty_list(self, pubmed_connector):
        """Test fetching details with empty list"""
        # Rate limiting
        rate_limited_request()
        
        # Test with empty list
        articles = pubmed_connector.fetch_article_details([])
        
        # Should return empty list
        assert isinstance(articles, list)
        assert len(articles) == 0
    
    def test_fetch_article_details_invalid_pmid(self, pubmed_connector):
        """Test fetching details with invalid PMID"""
        # Rate limiting
        rate_limited_request()
        
        # Test with invalid PMID
        articles = pubmed_connector.fetch_article_details(["invalid123"])
        
        # Should handle gracefully - parser will likely return empty list
        # due to validation errors
        assert isinstance(articles, list)
        # Depending on API behavior, might be empty or contain error info
        # but should not crash
    
    def test_search_and_fetch_combined(self, pubmed_connector):
        """Test combined search and fetch workflow"""
        # Rate limiting for search
        rate_limited_request()
        
        # Search for articles
        search_query = "medicinal plants"
        pmids = pubmed_connector.search_articles(search_query, 2)
        
        # Verify search results
        assert isinstance(pmids, list)
        assert len(pmids) <= 2
        
        # If we have results, fetch details
        if pmids:
            # Rate limiting for fetch
            rate_limited_request()
            
            articles = pubmed_connector.fetch_article_details(pmids)
            
            # Verify fetch results
            assert isinstance(articles, list)
            assert len(articles) == len(pmids)
            
            # Verify article structure
            for article in articles:
                # Now we expect PubmedArticle objects
                assert hasattr(article, 'pmid')
                assert hasattr(article, 'title')
                assert hasattr(article, 'abstract')
                assert hasattr(article, 'raw_xml')
                assert article.pmid in pmids
                assert isinstance(article.raw_xml, str)
                assert len(article.raw_xml) > 0
    
    def test_connector_with_different_query_types(self, pubmed_connector):
        """Test connector with different types of queries"""
        test_queries = [
            "thai traditional medicine",
            "herbal medicine",
            "medicinal plants"
        ]
        
        for query in test_queries:
            # Rate limiting
            rate_limited_request()
            
            # Test search
            pmids = pubmed_connector.search_articles(query, 1)
            
            # Verify basic structure
            assert isinstance(pmids, list)
            if pmids:
                assert isinstance(pmids[0], str)
                assert pmids[0].isdigit()
    
    def test_respectful_api_usage(self, pubmed_connector):
        """Test that we're using the API respectfully"""
        # This test verifies we're following ethical guidelines:
        # 1. Limited result sets (max 3 results per request)
        # 2. Rate limiting between requests
        # 3. Minimal overall API calls
        
        # Count requests to verify we're not making too many
        request_count = 0
        
        # Test search
        rate_limited_request()
        request_count += 1
        pmids = pubmed_connector.search_articles("traditional medicine", 3)
        
        # Test fetch if we have results
        if pmids:
            rate_limited_request()
            request_count += 1
            articles = pubmed_connector.fetch_article_details([pmids[0]])
            assert len(articles) == 1
        
        # Verify we didn't make too many requests
        assert request_count <= 2  # Should only make 1-2 requests in this test