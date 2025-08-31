# RAG API Usage and Testing Tutorial

This tutorial provides a comprehensive guide on how to use and test the RAG API for the Thai Traditional Medicine RAG Bot.

## 1. API Overview

The RAG API provides several endpoints for interacting with the system. The base URL for the API is `http://localhost:8005/api/v1/rag`.

### Key Endpoints:
- `POST /query`: Query the RAG system to retrieve relevant information.
- `POST /documents`: Add a single document to the vector store.
- `POST /documents/batch`: Add multiple documents in a single request.
- `GET /statistics`: Get statistics about the RAG system.
- `GET /health`: Check the health of the RAG system.
- `DELETE /documents/{document_id}`: Delete a document and its associated chunks.

## 2. Adding Documents

You can add documents to the RAG system one by one or in batches.

### Adding a Single Document

To add a single document, send a `POST` request to the `/documents` endpoint with the following payload:

```json
{
  "id": "your-unique-document-id",
  "content": "The full text of the document goes here...",
  "metadata": {
    "source": "pubmed",
    "publication_year": "2024",
    "authors": ["Author One", "Author Two"]
  }
}
```

**Example using `curl`:**

```bash
curl -X POST "http://localhost:8005/api/v1/rag/documents" \
-H "Content-Type: application/json" \
-d '{
  "id": "doc-001",
  "content": "Thai traditional medicine is a holistic approach to health...",
  "metadata": {
    "source": "manual",
    "year": 2024
  }
}'
```

### Adding Documents in a Batch

For multiple documents, use the `/documents/batch` endpoint. The payload is a list of document objects.

```json
[
  {
    "id": "doc-001",
    "content": "Content of the first document...",
    "metadata": { "source": "pubmed" }
  },
  {
    "id": "doc-002",
    "content": "Content of the second document...",
    "metadata": { "source": "journal" }
  }
]
```

**Example using `curl`:**

```bash
curl -X POST "http://localhost:8005/api/v1/rag/documents/batch?batch_size=50" \
-H "Content-Type: application/json" \
-d '[
  {
    "id": "doc-001",
    "content": "...",
    "metadata": {}
  },
  {
    "id": "doc-002",
    "content": "...",
    "metadata": {}
  }
]'
```

## 3. Querying the System

To retrieve information, send a `POST` request to the `/query` endpoint.

### Basic Query

```json
{
  "query": "What are the benefits of Plai?",
  "top_k": 5,
  "return_context": true
}
```

- `query`: The question you want to ask.
- `top_k`: The number of relevant chunks to retrieve.
- `return_context`: Whether to include the retrieved text chunks in the response.

**Example using `curl`:**

```bash
curl -X POST "http://localhost:8005/api/v1/rag/query" \
-H "Content-Type: application/json" \
-d '{
  "query": "anti-inflammatory properties of Plai",
  "top_k": 3
}'
```

### Sample Response

```json
{
  "query": "anti-inflammatory properties of Plai",
  "num_results": 3,
  "retrieval_time": 0.045,
  "context": [
    {
      "chunk_id": "some-chunk-id-1",
      "document_id": "doc-xyz",
      "content": "Zingiber cassumunar, commonly known as Plai, has been shown to possess significant anti-inflammatory properties...",
      "score": 0.85
    },
    ...
  ],
  "sources": ["doc-xyz"],
  "combined_context": "Zingiber cassumunar, commonly known as Plai, has been shown to possess significant anti-inflammatory properties..."
}
```

## 4. Checking System Status

### System Statistics

To get detailed statistics about the RAG pipeline configuration and the vector store, use the `/statistics` endpoint.

```bash
curl http://localhost:8005/api/v1/rag/statistics
```

### Health Check

To quickly check if the system is running and see the number of chunks and documents, use the `/health` endpoint.

```bash
curl http://localhost:8005/api/v1/rag/health
```

## 5. How to Test the RAG API

We have created scripts to automate the process of testing the RAG pipeline.

### Prerequisites
Ensure the RAG API is running:
```bash
make api
```

### Step 1: Acquire Data

Run the acquisition script to download a test set of documents from PubMed.

```bash
uv run python scripts/acquisition/fetch_pubmed_data.py
```
This will create a file at `data/raw/pubmed_ttm_100_articles.json`.

### Step 2: Ingest Data

Run the ingestion script to load the downloaded documents into the RAG system.

```bash
uv run python scripts/ingestion/ingest_documents.py
```
This script will call the `/documents` endpoint for each document and print the progress and a summary.

### Step 3: Evaluate Retrieval

Run the evaluation script to test the retrieval quality with a set of predefined questions.

```bash
uv run python scripts/evaluation/evaluate_retrieval.py
```
This script will query the `/query` endpoint and save the results to `results/retrieval_evaluation_results.json`.

### Step 4: Analyze Results

After running the evaluation, you can inspect the `results/retrieval_evaluation_results.json` file to see the retrieved chunks for each question. This is crucial for debugging and improving the RAG system's performance.
