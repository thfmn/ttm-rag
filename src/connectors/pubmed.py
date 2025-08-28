import requests
from typing import Dict, List, Optional
from src.models.source import Source
from src.models.pubmed import PubmedArticle
from src.utils.pubmed_parser import parse_pubmed_xml
import logging

logger = logging.getLogger(__name__)

class PubMedConnector:
    """
    Connector for fetching data from PubMed API
    """
    
    def __init__(self, source: Source):
        self.source = source
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.api_key = source.metadata.get("api_key") if source.metadata else None
        
    def search_articles(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for articles in PubMed based on a query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs (PMIDs)
        """
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "usehistory": "y"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pmids = data.get("esearchresult", {}).get("idlist", [])
            logger.info(f"Found {len(pmids)} articles for query: {query}")
            return pmids
            
        except requests.RequestException as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
            
    def fetch_article_details(self, pmids: List[str]) -> List[PubmedArticle]:
        """
        Fetch detailed information for a list of PubMed IDs and parse into structured data
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of PubmedArticle objects with structured data
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
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse the XML into structured PubmedArticle objects
            articles = parse_pubmed_xml(response.text)
            logger.info(f"Fetched and parsed details for {len(articles)} articles")
            return articles
            
        except requests.RequestException as e:
            logger.error(f"Error fetching article details: {e}")
            return []