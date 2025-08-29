import asyncio
import json
import os
from pathlib import Path

from src.connectors.pubmed import PubMedConnector
from src.models.source import Source
from src.utils.pubmed_query_builder import PubMedQueryBuilder

# Configuration
QUERY = '("thai traditional medicine"[Title/Abstract] OR "thai herbal medicine"[Title/Abstract]) AND ("2020"[PDAT] : "3000"[PDAT])'
MAX_RESULTS = 100
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "pubmed_ttm_100_articles.json"

def main():
    """
    Fetches 100 articles from PubMed based on a predefined query and saves them to a JSON file.
    """
    print("Starting data acquisition from PubMed...")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create a source object for PubMed
    # In a real app, this would come from a config or database
    source = Source(
        id=1,
        name="PubMed",
        type="academic_journal",
        url="https://pubmed.ncbi.nlm.nih.gov/",
        metadata={"api_key": os.getenv("PUBMED_API_KEY")},
    )

    connector = PubMedConnector(source)
    
    try:
        print(f"Searching for articles with query: {QUERY}")
        pmids = connector.search_articles(QUERY, max_results=MAX_RESULTS)
        print(f"Found {len(pmids)} articles.")

        if not pmids:
            print("No articles found. Exiting.")
            return

        print(f"Fetching details for {len(pmids)} articles...")
        # The fetch_article_details method returns a list of PubmedArticle objects.
        # We need to convert them to a JSON-serializable format.
        articles_data = connector.fetch_article_details(pmids)
        articles = [article.model_dump() for article in articles_data]
        print("Successfully fetched article details.")

        # Save the data
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully saved {len(articles)} articles to {OUTPUT_FILE}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Data acquisition process finished.")

if __name__ == "__main__":
    main()
