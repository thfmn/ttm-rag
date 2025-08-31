import json
import time
from pathlib import Path
import requests
import os

# Configuration
INPUT_FILE = Path("data/raw/pubmed_ttm_100_articles.json")
API_ENDPOINT = "http://localhost:8005/api/v1/rag/documents"
HEADERS = {"Content-Type": "application/json"}

def main():
    """
    Reads documents from a JSON file and ingests them into the RAG system
    via the API, measuring performance metrics.
    """
    print("Starting document ingestion process...")

    if not INPUT_FILE.exists():
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        documents = json.load(f)

    total_docs = len(documents)
    print(f"Found {total_docs} documents to ingest.")
    # Optional Dagster emission mode: when enabled, emit JSON Lines to stdout instead of POSTing
    dagster_mode = os.getenv("DAGSTER_MODE", "0")
    dagster_mode = str(dagster_mode).strip().lower() not in ("", "0", "false", "no")

    start_time = time.time()
    errors = []
    success_count = 0

    for i, doc in enumerate(documents):
        # Construct the payload for the API
        payload = {
            "id": doc.get("pmid", f"doc_{i}"),
            "content": doc.get("abstract", "") or doc.get("title", ""), # Use abstract or title
            "metadata": {
                "source": "pubmed",
                "title": doc.get("title"),
                "journal": doc.get("journal"),
                "publication_year": str(pub_date.get("year")) if (pub_date := doc.get("publication_date")) else None,
                "authors": [author.get("name") for author in doc.get("authors", []) if author],
            },
        }

        # Filter out metadata with None values
        payload["metadata"] = {k: v for k, v in payload["metadata"].items() if v is not None}
        
        # Ensure content is not empty
        if not payload["content"]:
            print(f"Skipping document {payload['id']} due to empty content.")
            continue

        # If in DAGSTER_MODE, emit JSON line to stdout for downstream assets and skip API call
        if dagster_mode:
            print(json.dumps(payload), flush=True)
            success_count += 1
            print(f"Emitted document {i + 1}/{total_docs} to stdout (DAGSTER_MODE=1): {payload['id']}")
            time.sleep(0.1)
            continue

        try:
            response = requests.post(API_ENDPOINT, headers=HEADERS, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for bad status codes
            success_count += 1
            print(f"Successfully ingested document {i + 1}/{total_docs}: {payload['id']}")
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to ingest document {payload['id']}: {e}"
            print(error_message)
            errors.append(error_message)
        
        # Simple rate limiting
        time.sleep(0.1)

    end_time = time.time()
    total_time = end_time - start_time
    docs_per_minute = (success_count / total_time) * 60 if total_time > 0 else 0

    print("\n--- Ingestion Summary ---")
    print(f"Total documents processed: {total_docs}")
    print(f"Successfully ingested: {success_count}")
    print(f"Errors: {len(errors)}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {docs_per_minute:.2f} docs/minute")
    
    if errors:
        print("\n--- Errors ---")
        for error in errors:
            print(error)

if __name__ == "__main__":
    main()
