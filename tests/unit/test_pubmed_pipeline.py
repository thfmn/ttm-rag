import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pipelines.pubmed_pipeline import PubMedPipeline
from src.models.source import Source
from src.models.document import Document
from src.models.pubmed import PubmedArticle, PubmedAuthor, PubmedJournal

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
def pubmed_pipeline(mock_source):
    """Create a PubMedPipeline instance for testing"""
    return PubMedPipeline(mock_source)

@patch('src.pipelines.pubmed_pipeline.PubMedConnector.search_articles')
@patch('src.pipelines.pubmed_pipeline.PubMedConnector.fetch_article_details')
def test_pubmed_pipeline_run(mock_fetch_details, mock_search_articles, pubmed_pipeline):
    """Test running the PubMed pipeline"""
    # Mock the connector methods
    mock_search_articles.return_value = ["123456", "789012"]
    
    # Create sample PubmedArticle objects
    article1 = PubmedArticle(
        pmid="123456",
        title="Test Article 1",
        abstract="This is a test abstract 1",
        authors=[PubmedAuthor(name="John Smith", affiliation="Test University")],
        raw_xml="<xml>Article 1</xml>"
    )
    
    article2 = PubmedArticle(
        pmid="789012",
        title="Test Article 2",
        abstract="This is a test abstract 2",
        authors=[PubmedAuthor(name="Jane Doe", affiliation="Another University")],
        raw_xml="<xml>Article 2</xml>"
    )
    
    mock_fetch_details.return_value = [article1, article2]
    
    # Run the pipeline
    documents = pubmed_pipeline.run("traditional medicine", 10)
    
    # Assertions
    assert len(documents) == 2
    assert isinstance(documents[0], Document)
    assert documents[0].external_id == "123456"
    assert documents[0].title == "Test Article 1"
    assert documents[0].abstract == "This is a test abstract 1"
    assert documents[0].content == "<xml>Article 1</xml>"
    assert documents[1].external_id == "789012"
    assert documents[1].title == "Test Article 2"
    assert documents[1].abstract == "This is a test abstract 2"
    assert documents[1].content == "<xml>Article 2</xml>"
    
    # Verify mocks were called
    mock_search_articles.assert_called_once_with("traditional medicine", 10)
    mock_fetch_details.assert_called_once_with(["123456", "789012"])

@patch('src.pipelines.pubmed_pipeline.PubMedConnector.search_articles')
@patch('src.pipelines.pubmed_pipeline.PubMedConnector.fetch_article_details')
def test_pubmed_pipeline_run_no_results(mock_fetch_details, mock_search_articles, pubmed_pipeline):
    """Test running the PubMed pipeline with no results"""
    # Mock the connector methods
    mock_search_articles.return_value = []
    
    # Run the pipeline
    documents = pubmed_pipeline.run("nonexistentquery", 10)
    
    # Assertions
    assert len(documents) == 0
    
    # Verify mocks were called
    mock_search_articles.assert_called_once_with("nonexistentquery", 10)
    mock_fetch_details.assert_not_called()

@patch('src.pipelines.pubmed_pipeline.PubMedConnector.search_articles')
@patch('src.pipelines.pubmed_pipeline.PubMedConnector.fetch_article_details')
def test_pubmed_pipeline_run_limited_results(mock_fetch_details, mock_search_articles, pubmed_pipeline):
    """Test running the PubMed pipeline with limited results"""
    # Mock the connector methods
    mock_search_articles.return_value = [str(i) for i in range(100)]
    
    # Create sample PubmedArticle objects (only 10 as per implementation)
    sample_articles = [
        PubmedArticle(
            pmid=str(i),
            title=f"Test Article {i}",
            raw_xml=f"<xml>Article {i}</xml>"
        ) 
        for i in range(10)
    ]
    
    mock_fetch_details.return_value = sample_articles
    
    # Run the pipeline
    documents = pubmed_pipeline.run("traditional medicine", 100)
    
    # Assertions
    assert len(documents) == 10
    assert isinstance(documents[0], Document)
    
    # Verify mocks were called
    mock_search_articles.assert_called_once_with("traditional medicine", 100)
    mock_fetch_details.assert_called_once()