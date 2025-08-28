import requests
from typing import Dict, List, Optional, Union
from src.models.source import Source
from src.models.pubmed import PubmedArticle
from src.utils.pubmed_parser import parse_pubmed_xml
from src.utils.pubmed_query_builder import PubMedQueryBuilder
from src.utils.exceptions import (
    PubMedAPIError, 
    PubMedParseError, 
    PubMedNetworkError,
    PubMedRateLimitError,
    create_pubmed_error_from_response
)
from src.utils.retry import retry, RetryConfig, should_retry_pubmed_error
import logging

logger = logging.getLogger(__name__)

# Configure retry settings for PubMed API calls
PUBMED_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    jitter=True
)


class PubMedConnector:
    """
    Connector for fetching data from PubMed API
    """
    
    def __init__(self, source: Source):
        self.source = source
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.api_key = source.metadata.get("api_key") if source.metadata else None
        
    @retry(
        exceptions=(PubMedAPIError, PubMedNetworkError, PubMedRateLimitError),
        config=PUBMED_RETRY_CONFIG,
        should_retry=should_retry_pubmed_error
    )
    def search_articles(self, query: Union[str, PubMedQueryBuilder], max_results: int = 100) -> List[str]:
        """
        Search for articles in PubMed based on a query
        
        Args:
            query: Search query string or PubMedQueryBuilder object
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs (PMIDs)
            
        Raises:
            PubMedAPIError: For API-related errors
            PubMedNetworkError: For network-related errors
            PubMedRateLimitError: For rate limiting errors
        """
        # If query is a PubMedQueryBuilder, build the query string
        if isinstance(query, PubMedQueryBuilder):
            query_str = query.build()
        else:
            query_str = query
            
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query_str,
            "retmax": max_results,
            "retmode": "json",
            "usehistory": "y"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            logger.debug(f"Searching PubMed with query: {query_str}")
            response = requests.get(search_url, params=params, timeout=30)
            
            # Check for HTTP errors
            if response.status_code != 200:
                raise create_pubmed_error_from_response(
                    response, 
                    context={"query": query_str, "max_results": max_results}
                )
            
            data = response.json()
            
            # Check for API errors in the response
            if "esearchresult" not in data:
                if "error" in data:
                    raise PubMedAPIError(
                        f"PubMed API error: {data['error']}",
                        context={"query": query_str, "response": data}
                    )
                else:
                    raise PubMedAPIError(
                        "Unexpected response format from PubMed API",
                        context={"query": query_str, "response": data}
                    )
            
            pmids = data.get("esearchresult", {}).get("idlist", [])
            logger.info(f"Found {len(pmids)} articles for query: {query_str}")
            return pmids
            
        except requests.RequestException as e:
            logger.error(f"Network error searching PubMed: {e}")
            raise PubMedNetworkError(
                f"Network error searching PubMed: {e}",
                original_exception=e,
                context={"query": query_str}
            )
        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")
            raise PubMedParseError(
                f"Error parsing JSON response from PubMed: {e}",
                context={"query": query_str}
            )
        except Exception as e:
            logger.error(f"Unexpected error searching PubMed: {e}")
            raise PubMedAPIError(
                f"Unexpected error searching PubMed: {e}",
                context={"query": query_str}
            )
            
    @retry(
        exceptions=(PubMedAPIError, PubMedNetworkError, PubMedRateLimitError),
        config=PUBMED_RETRY_CONFIG,
        should_retry=should_retry_pubmed_error
    )
    def fetch_article_details(self, pmids: List[str]) -> List[PubmedArticle]:
        """
        Fetch detailed information for a list of PubMed IDs and parse into structured data
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of PubmedArticle objects with structured data
            
        Raises:
            PubMedAPIError: For API-related errors
            PubMedNetworkError: For network-related errors
            PubMedRateLimitError: For rate limiting errors
            PubMedParseError: For XML parsing errors
        """
        if not pmids:
            return []
            
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            logger.debug(f"Fetching details for {len(pmids)} articles")
            response = requests.get(fetch_url, params=params, timeout=60)
            
            # Check for HTTP errors
            if response.status_code != 200:
                raise create_pubmed_error_from_response(
                    response, 
                    context={"pmids": pmids}
                )
            
            # Parse the XML into structured PubmedArticle objects
            try:
                articles = parse_pubmed_xml(response.text)
                logger.info(f"Fetched and parsed details for {len(articles)} articles")
                return articles
            except PubMedParseError:
                # Re-raise PubMedParseError as is
                raise
            except Exception as e:
                logger.error(f"Error parsing XML response: {e}")
                raise PubMedParseError(
                    f"Error parsing XML response from PubMed: {e}",
                    context={"pmids": pmids, "response_length": len(response.text)}
                )
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching article details: {e}")
            raise PubMedNetworkError(
                f"Network error fetching article details: {e}",
                original_exception=e,
                context={"pmids": pmids}
            )
        except PubMedParseError:
            # Re-raise PubMedParseError as is
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching article details: {e}")
            raise PubMedAPIError(
                f"Unexpected error fetching article details: {e}",
                context={"pmids": pmids}
            )