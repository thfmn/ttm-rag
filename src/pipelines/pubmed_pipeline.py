from src.connectors.pubmed import PubMedConnector
from src.models.source import Source
from src.models.document import Document
from src.models.pubmed import PubmedArticle
import logging
from typing import List
from datetime import datetime

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
            
        # Step 2: Fetch article details (limited for testing)
        articles = self.connector.fetch_article_details(pmids[:10])  # Limit for testing
        
        # Step 3: Convert to Document objects
        documents = self._convert_to_documents(articles)
        
        logger.info(f"PubMed pipeline completed. Processed {len(documents)} documents.")
        return documents
        
    def _convert_to_documents(self, articles: List[PubmedArticle]) -> List[Document]:
        """
        Convert PubmedArticle objects to Document objects
        
        Args:
            articles: List of PubmedArticle objects
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for article in articles:
            # Create a Document from the PubmedArticle
            doc = Document(
                source_id=self.source.id,
                external_id=article.pmid,
                title=article.title,
                abstract=article.abstract,
                authors=[author.name for author in article.authors] if article.authors else None,
                publication_date=None,  # Would need to parse datetime from article.publication_date
                language=article.language,
                document_type=article.article_type or "research_paper",
                content=article.raw_xml,  # Store raw XML for now, could be full text later
                metadata={
                    "doi": article.doi,
                    "journal": article.journal.title if article.journal else None,
                    "mesh_terms": article.mesh_terms,
                    "chemicals": article.chemicals,
                    "country": article.country
                } if any([
                    article.doi, article.journal, article.mesh_terms, 
                    article.chemicals, article.country
                ]) else None
            )
            documents.append(doc)
            
        return documents

if __name__ == '__main__':
    pipeline = PubMedPipeline