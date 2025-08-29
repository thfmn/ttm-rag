import requests
from typing import List, Union
from src.models.source import Source
from src.models.pmc import PmcArticle
from src.utils.pmc_parser import parse_pmc_xml
from src.utils.pubmed_query_builder import PubMedQueryBuilder
from src.utils.exceptions import (
    PubMedAPIError,
    PubMedNetworkError,
    PubMedRateLimitError,
    create_pubmed_error_from_response,
)
from src.utils.retry import retry, RetryConfig, should_retry_pubmed_error
from src.utils.rate_limiting import acquire_rate_limit
import logging

logger = logging.getLogger(__name__)

# Configure retry settings for PMC API calls
PMC_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    jitter=True
)

class PmcConnector:
    """
    Connector for fetching data from PubMed Central (PMC) API
    """

    def __init__(self, source: Source):
        self.source = source
        self.base_url = "https://www.ncbi.nlm.nih.gov/pmc/articles"
        self.api_key = source.metadata.get("api_key") if source.metadata else None

    def search_articles(
        self, query: Union[str, PubMedQueryBuilder], max_results: int = 100
    ) -> List[str]:
        """
        Search for articles in PMC based on a query.
        """
        # This method will be implemented in a future step.
        logger.warning("PmcConnector.search_articles is not yet implemented.")
        return []

    def fetch_article_details(self, pmcids: List[str]) -> List[PmcArticle]:
        """
        Fetch detailed information for a list of PMC IDs.
        """
        if not pmcids:
            return []

        articles = []
        for pmcid in pmcids:
            try:
                if not acquire_rate_limit("pmc_fetch", 1.0):
                    logger.warning(f"Rate limit exceeded for PMC fetch for {pmcid}")
                    continue

                article_url = f"{self.base_url}/{pmcid}/"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(article_url, headers=headers, timeout=60)
                response.raise_for_status()

                # This is a simplified approach; real implementation would parse the HTML.
                # For now, we will extract a placeholder title.
                title = f"Title for {pmcid}"
                full_text = response.text

                articles.append(
                    PmcArticle(
                        pmcid=pmcid,
                        title=title,
                        full_text=full_text,
                    )
                )
                logger.info(f"Successfully fetched article {pmcid}")
            except requests.RequestException as e:
                logger.error(f"Failed to fetch article {pmcid}: {e}")

        return articles
