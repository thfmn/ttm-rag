import pytest
import time
from datetime import date
from src.connectors.pmc import PmcConnector
from src.models.source import Source
from src.utils.pubmed_query_builder import PubMedQueryBuilder, DateRange

# Configuration for integration tests
MAX_RESULTS = 3
MIN_INTERVAL = 1.0  # seconds

def rate_limited_request():
    """Enforce a delay between requests to respect API rate limits."""
    time.sleep(MIN_INTERVAL)

@pytest.fixture(scope="module")
def pmc_connector():
    """Fixture to provide a PmcConnector instance for testing."""
    source = Source(id=2, name="PMC", type="open_access_journal")
    return PmcConnector(source)

@pytest.mark.integration
class TestPmcConnectorIntegration:
    def test_search_articles_basic(self, pmc_connector):
        """Test basic article search functionality."""
        rate_limited_request()
        query = "traditional medicine"
        pmcids = pmc_connector.search_articles(query, max_results=MAX_RESULTS)
        assert isinstance(pmcids, list)
        assert len(pmcids) <= MAX_RESULTS
        if pmcids:
            assert all(isinstance(pmcid, str) for pmcid in pmcids)

    def test_search_articles_with_builder(self, pmc_connector):
        """Test searching with a query builder."""
        rate_limited_request()
        query = (
            PubMedQueryBuilder()
            .search("herbal medicine")
            .date_range(DateRange(start_date=date(2022, 1, 1), end_date=date(2023, 12, 31)))
        )
        pmcids = pmc_connector.search_articles(query, max_results=MAX_RESULTS)
        assert isinstance(pmcids, list)
        assert len(pmcids) <= MAX_RESULTS

    def test_search_articles_no_results(self, pmc_connector):
        """Test a query that should yield no results."""
        rate_limited_request()
        query = "non_existent_term_xyz123"
        pmcids = pmc_connector.search_articles(query, max_results=MAX_RESULTS)
        assert isinstance(pmcids, list)
        assert len(pmcids) == 0

    def test_fetch_article_details(self, pmc_connector):
        """Test fetching full article details."""
        rate_limited_request()
        # A known article with full text
        pmcids = ["PMC7034423"]
        articles = pmc_connector.fetch_article_details(pmcids)
        assert len(articles) == 1
        article = articles[0]
        assert article.pmcid == "PMC7034423"
        assert "Title for PMC7034423" in article.title
        assert len(article.full_text) > 0
