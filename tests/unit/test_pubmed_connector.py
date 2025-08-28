import sys
import os
import pytest
from unittest.mock import Mock, patch
import requests

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.connectors.pubmed import PubMedConnector
from src.models.source import Source

@pytest.fixture
def mock_source():
    """Create a mock Source object for testing"""
    return Source(
        id=1,
        name="PubMed",
        type="academic",
        url="https://pubmed.ncbi.nlm.nih.gov/",
        api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        access_method="api",
        reliability_score=5,
        metadata={"api_key": "test_key"}
    )

@pytest.fixture
def pubmed_connector(mock_source):
    """Create a PubMedConnector instance for testing"""
    return PubMedConnector(mock_source)

@patch('src.connectors.pubmed.requests.get')
def test_search_articles(mock_get, pubmed_connector):
    """Test searching for articles"""
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {
        "esearchresult": {
            "idlist": ["123456", "789012"]
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test the method
    pmids = pubmed_connector.search_articles("traditional medicine", 10)
    
    # Assertions
    assert len(pmids) == 2
    assert "123456" in pmids
    assert "789012" in pmids
    mock_get.assert_called_once()

@patch('src.connectors.pubmed.requests.get')
def test_search_articles_empty_result(mock_get, pubmed_connector):
    """Test searching for articles with no results"""
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {
        "esearchresult": {
            "idlist": []
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test the method
    pmids = pubmed_connector.search_articles("nonexistentquery", 10)
    
    # Assertions
    assert len(pmids) == 0
    mock_get.assert_called_once()

@patch('src.connectors.pubmed.requests.get')
def test_search_articles_request_exception(mock_get, pubmed_connector):
    """Test searching for articles when request fails"""
    # Mock the response
    mock_get.side_effect = requests.RequestException("Network error")
    
    # Test the method
    pmids = pubmed_connector.search_articles("traditional medicine", 10)
    
    # Assertions
    assert len(pmids) == 0
    mock_get.assert_called_once()

@patch('src.connectors.pubmed.requests.get')
def test_fetch_article_details(mock_get, pubmed_connector):
    """Test fetching article details"""
    # Mock the response
    mock_response = Mock()
    mock_response.text = "<xml>Article content</xml>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test the method
    articles = pubmed_connector.fetch_article_details(["123456", "789012"])
    
    # Assertions
    assert len(articles) == 2
    assert articles[0]["pmid"] == "123456"
    assert articles[0]["raw_xml"] == "<xml>Article content</xml>"
    assert articles[1]["pmid"] == "789012"
    assert articles[1]["raw_xml"] == "<xml>Article content</xml>"
    mock_get.assert_called_once()

@patch('src.connectors.pubmed.requests.get')
def test_fetch_article_details_empty_input(mock_get, pubmed_connector):
    """Test fetching article details with empty input"""
    # Test the method
    articles = pubmed_connector.fetch_article_details([])
    
    # Assertions
    assert len(articles) == 0
    mock_get.assert_not_called()

@patch('src.connectors.pubmed.requests.get')
def test_fetch_article_details_request_exception(mock_get, pubmed_connector):
    """Test fetching article details when request fails"""
    # Mock the response
    mock_get.side_effect = requests.RequestException("Network error")
    
    # Test the method
    articles = pubmed_connector.fetch_article_details(["123456"])
    
    # Assertions
    assert len(articles) == 0
    mock_get.assert_called_once()