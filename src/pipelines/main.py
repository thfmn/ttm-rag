import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pipelines.pubmed_pipeline import PubMedPipeline
from src.models.source import Source

def main():
    """Main function to demonstrate the PubMed pipeline"""
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
    
    # Run the pipeline with a sample query
    print("Running PubMed pipeline...")
    documents = pipeline.run("traditional medicine", 5)
    
    # Print results
    print(f"Found {len(documents)} documents")
    for i, doc in enumerate(documents):
        print(f"Document {i+1}:")
        print(f"  PMID: {doc.external_id}")
        print(f"  Content length: {len(doc.content) if doc.content else 0} characters")
        print()

if __name__ == "__main__":
    main()