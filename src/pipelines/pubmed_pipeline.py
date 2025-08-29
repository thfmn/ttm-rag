from src.connectors.pubmed import PubMedConnector
from src.models.source import Source
from src.models.document import Document
from src.models.pubmed import PubmedArticle
from src.utils.rate_limiting import configure_rate_limiting
from src.database.service import db_service
import logging
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure rate limiting for PubMed API
# PubMed recommends no more than 3 requests per second
# We'll set a conservative limit of 2 requests per second with a burst capacity of 5
configure_rate_limiting("pubmed_search", 2.0, 5.0)
configure_rate_limiting("pubmed_fetch", 2.0, 5.0)


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
        
        # Step 4: Save to database
        self._save_documents_to_database(documents)
        
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
        
    def _save_documents_to_database(self, documents: List[Document]) -> None:
        """
        Save documents to the database.
        
        Args:
            documents: List of Document objects to save
        """
        logger.info(f"Saving {len(documents)} documents to database")
        
        for document in documents:
            try:
                # Save document to database
                document_id = db_service.save_document(document, self.source.id)
                if document_id:
                    logger.info(f"Saved document {document.external_id} with ID {document_id}")
                else:
                    logger.error(f"Failed to save document {document.external_id}")
            except Exception as e:
                logger.error(f"Error saving document {document.external_id}: {e}")

if __name__ == '__main__':
    pipeline = PubMedPipeline