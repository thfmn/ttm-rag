from src.connectors.pubmed import PubMedConnector
from src.models.source import Source
from src.models.document import Document
import logging
from typing import List

logger = logging.getLogger(__name__)

class PubMedPipeline:
    """
    Pipeline for ingesting data from PubMed
    """
    
    def __init__(self, source: Source):
        self.source = source
        self.connector = PubMedConnector(source)
        
    def run(self, query: str, max_results: int = 100) -> List[Document]:
        """
        Run the PubMed data ingestion pipeline
        
        Args:
            query: Search query for PubMed
            max_results: Maximum number of results to fetch
            
        Returns:
            List of Document objects
        """
        logger.info(f"Starting PubMed pipeline with query: {query}")
        
        # Step 1: Search for articles
        pmids = self.connector.search_articles(query, max_results)
        
        if not pmids:
            logger.warning("No articles found for the given query")
            return []
            
        # Step 2: Fetch article details
        articles = self.connector.fetch_article_details(pmids[:10])  # Limit for testing
        
        # Step 3: Convert to Document objects
        documents = self._convert_to_documents(articles)
        
        logger.info(f"PubMed pipeline completed. Processed {len(documents)} documents.")
        return documents
        
    def _convert_to_documents(self, articles: List[dict]) -> List[Document]:
        """
        Convert raw article data to Document objects
        
        Args:
            articles: List of raw article data
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for article in articles:
            doc = Document(
                source_id=self.source.id,
                external_id=article.get("pmid"),
                content=article.get("raw_xml"),  # In a full implementation, we'd parse this
                document_type="research_paper"
            )
            documents.append(doc)
            
        return documents

if __name__ == '__main__':
    pipeline = PubMedPipeline