# Implementation

In this section, we'll walk through our implementation process, from setting up the project structure to implementing the PubMed connector.

## Project Structure

We started by setting up a well-organized project structure following best practices:

```
thai-traditional-medicine-rag-bot/
├── README.md
├── QWEN.md                    # Project Requirements Document
├── docs/                      # Documentation
│   ├── conf.py                # Sphinx configuration
│   ├── index.rst              # Documentation index
│   ├── introduction.md        # Introduction to the project
│   ├── project_overview.md    # Project overview
│   ├── implementation.md      # Implementation details (this file)
│   ├── testing.md             # Testing documentation
│   ├── current_state.md       # Current state of the project
│   └── future_steps.md        # Future steps
├── src/                       # Source code
│   ├── connectors/            # Source connector implementations
│   ├── models/                # Data models
│   ├── pipelines/             # Data pipeline code
│   ├── validators/            # Data validation modules
│   └── utils/                 # Utility functions
├── tests/                     # Tests
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data
├── config/                    # Configuration files
├── scripts/                   # Scripts
├── docker/                    # Docker configurations
├── .github/                   # GitHub Actions workflows
└── requirements/              # Python dependencies
```

## PubMed Connector Implementation

Our first implementation focused on creating a connector for the PubMed API, which is one of our Tier 1 sources.

### Why PubMed?

PubMed is a free search engine accessing primarily the MEDLINE database of references and abstracts on life sciences and biomedical topics. It's an excellent source of academic papers related to traditional medicine, including Thai Traditional Medicine.

### Connector Design

We designed our PubMed connector with the following considerations:

1. **Modularity**: The connector is a separate module that can be easily reused
2. **Error Handling**: Robust error handling for network issues and API errors
3. **Configuration**: Easy configuration through our Source model
4. **Logging**: Comprehensive logging for debugging and monitoring

### Key Components

1. **Source Model**: A data class representing a data source with all necessary configuration
2. **PubMedConnector Class**: The main class that handles communication with the PubMed API
3. **Methods**:
   - `search_articles()`: Searches for articles based on a query
   - `fetch_article_details()`: Fetches detailed information for specific articles

### Implementation Details

Here's a simplified version of our PubMed connector:

```python
class PubMedConnector:
    def __init__(self, source: Source):
        self.source = source
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.api_key = source.metadata.get("api_key") if source.metadata else None
        
    def search_articles(self, query: str, max_results: int = 100) -> List[str]:
        # Implementation details...
        
    def fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        # Implementation details...
```

## PubMed Pipeline Implementation

We also implemented a pipeline that uses our connector to fetch and process data:

### Pipeline Design

Our pipeline follows a simple but effective design:

1. **Search**: Use the connector to search for articles
2. **Fetch**: Retrieve detailed information for the found articles
3. **Convert**: Convert the raw data into our internal Document format

### Key Components

1. **Document Model**: A data class representing a document with all relevant fields
2. **PubMedPipeline Class**: The main class that orchestrates the data ingestion process
3. **Methods**:
   - `run()`: Executes the entire pipeline
   - `_convert_to_documents()`: Converts raw article data to Document objects

### Implementation Details

Here's a simplified version of our PubMed pipeline:

```python
class PubMedPipeline:
    def __init__(self, source: Source):
        self.source = source
        self.connector = PubMedConnector(source)
        
    def run(self, query: str, max_results: int = 100) -> List[Document]:
        # Implementation details...
        
    def _convert_to_documents(self, articles: List[dict]) -> List[Document]:
        # Implementation details...
```

## Main Script

We created a main script to demonstrate how to use our pipeline:

```python
def main():
    # Create a source object for PubMed
    source = Source(
        id=1,
        name="PubMed",
        type="academic",
        # ... other fields
    )
    
    # Create the pipeline
    pipeline = PubMedPipeline(source)
    
    # Run the pipeline with a sample query
    documents = pipeline.run("traditional medicine", 5)
    
    # Print results
    print(f"Found {len(documents)} documents")
    # ... print document details
```

This script demonstrates the end-to-end flow of our implementation, from creating a source configuration to running the pipeline and displaying results.