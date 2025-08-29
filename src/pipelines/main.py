import sys
import os
from datetime import date

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pipelines.pubmed_pipeline import PubMedPipeline
from src.models.source import Source
from src.utils.pubmed_query_builder import (
    PubMedQueryBuilder,
    DateRange,
    ArticleType,
    build_thai_traditional_medicine_query
)
from src.database.config import init_database


def main():
    """Main function to demonstrate the PubMed pipeline"""
    # Initialize the database
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
    
    # Create a source object for PubMed
    source = Source(
        id=1,
        name="PubMed",
        type="academic",
        url="https://pubmed.ncbi.nlm.nih.gov/",
        api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        access_method="api",
        reliability_score=5,
        metadata={"api_key": None}  # No API key for demo
    )
    
    # Create the pipeline
    pipeline = PubMedPipeline(source)
    
    print("Running PubMed pipeline with different query approaches...")
    
    # Example 1: Basic query (existing functionality)
    print("\n1. Basic query: 'traditional medicine'")
    documents1 = pipeline.run("traditional medicine", 3)
    print(f"Found {len(documents1)} documents")
    
    # Example 2: Using the query builder for Thai Traditional Medicine
    print("\n2. Thai Traditional Medicine query using query builder")
    builder = PubMedQueryBuilder()
    query = (builder
             .search("traditional medicine")
             .and_words(["thai", "herbal", "plant"])
             .not_words(["chinese", "acupuncture"])
             .article_type(ArticleType.REVIEW)
             .build())
    
    # For now, we'll need to modify the pipeline to accept query builders
    # Let's directly use the connector for this example
    from src.connectors.pubmed import PubMedConnector
    connector = PubMedConnector(source)
    pmids = connector.search_articles(query, 3)
    if pmids:
        articles = connector.fetch_article_details(pmids)
        print(f"Found {len(articles)} articles with query: {query}")
        for i, article in enumerate(articles):
            print(f"  Article {i+1}: {article.title[:50]}{'...' if article.title and len(article.title) > 50 else ''}")
    
    # Example 3: Using the specialized Thai Traditional Medicine query function
    print("\n3. Specialized Thai Traditional Medicine query function")
    specialized_query = build_thai_traditional_medicine_query(
        additional_terms=["medicinal", "ethnopharmacology"],
        exclude_terms=["chinese", "korean"],
        article_types=[ArticleType.RESEARCH_ARTICLE, ArticleType.REVIEW]
    )
    
    pmids2 = connector.search_articles(specialized_query, 3)
    if pmids2:
        articles2 = connector.fetch_article_details(pmids2)
        print(f"Found {len(articles2)} articles with specialized query")
        for i, article in enumerate(articles2):
            print(f"  Article {i+1}: {article.title[:50]}{'...' if article.title and len(article.title) > 50 else ''}")
    
    # Example 4: Query with date range
    print("\n4. Query with date range filter")
    builder3 = PubMedQueryBuilder()
    start_date = date(2020, 1, 1)
    end_date = date(2023, 12, 31)
    date_range = DateRange(start_date, end_date)
    
    query3 = (builder3
              .search("thai medicine")
              .date_range(date_range)
              .build())
    
    pmids3 = connector.search_articles(query3, 3)
    if pmids3:
        articles3 = connector.fetch_article_details(pmids3)
        print(f"Found {len(articles3)} articles with date range query: {query3}")
        for i, article in enumerate(articles3):
            print(f"  Article {i+1}: {article.title[:50]}{'...' if article.title and len(article.title) > 50 else ''}")


if __name__ == "__main__":
    main()