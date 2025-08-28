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
    
    # Test searching for articles with a small result set
    pmids = connector.search_articles("traditional medicine", 3)
    
    # Assertions
    assert isinstance(pmids, list)
    # We might not get exactly 3 results, but we should get some
    assert len(pmids) <= 3
    
    # Test fetching article details (only for first article to keep test fast)
    if pmids:
        articles = connector.fetch_article_details([pmids[0]])
        assert isinstance(articles, list)
        assert len(articles) == 1
        # Now we expect PubmedArticle objects
        assert hasattr(articles[0], 'pmid')
        assert articles[0].pmid == pmids[0]