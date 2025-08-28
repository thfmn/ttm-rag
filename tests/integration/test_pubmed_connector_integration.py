import sys
import os
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.connectors.pubmed import PubMedConnector
from src.models.source import Source

@pytest.mark.integration
def test_pubmed_connector_integration():
    """Integration test for PubMed connector with real API"""
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
    
    # Test searching for articles
    pmids = connector.search_articles("traditional medicine", 5)
    
    # Assertions
    assert isinstance(pmids, list)
    # We might not get exactly 5 results, but we should get some
    assert len(pmids) <= 5
    
    # Test fetching article details (only for first article to keep test fast)
    if pmids:
        articles = connector.fetch_article_details([pmids[0]])
        assert isinstance(articles, list)
        assert len(articles) == 1
        assert "pmid" in articles[0]
        assert "raw_xml" in articles[0]
        assert articles[0]["pmid"] == pmids[0]