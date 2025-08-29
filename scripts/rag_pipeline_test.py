"""
RAG Pipeline Test

This script demonstrates the basic RAG pipeline functionality.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import RagSystem, RagDocument, RagQuery

def test_rag_pipeline():
    """Test the basic RAG pipeline functionality."""
    print("Testing RAG pipeline...")
    
    # Initialize the RAG system
    rag_system = RagSystem()
    
    # Create some test documents
    documents = [
        RagDocument(
            id="doc-1",
            content="Traditional Thai medicine has been practiced for centuries and includes various healing practices such as herbal medicine, massage, and spiritual rituals.",
            metadata={"source": "thai_medicine_overview", "category": "overview"}
        ),
        RagDocument(
            id="doc-2",
            content="Herbal remedies in Thai traditional medicine often use plants like turmeric, ginger, and lemongrass for their anti-inflammatory properties.",
            metadata={"source": "thai_herbs", "category": "herbal_medicine"}
        ),
        RagDocument(
            id="doc-3",
            content="Thai massage combines acupressure, Indian Ayurvedic principles, and assisted yoga postures to improve circulation and flexibility.",
            metadata={"source": "thai_massage", "category": "massage_therapy"}
        )
    ]
    
    # Process the documents
    print(f"Processing {len(documents)} documents...")
    processed_docs = rag_system.process_documents(documents)
    print(f"Processed {len(processed_docs)} documents")
    
    # Test a query
    query_text = "What are the benefits of Thai traditional medicine?"
    print(f"\nQuery: {query_text}")
    
    # Process the query through the RAG pipeline
    response = rag_system.query(query_text)
    print(f"Response: {response.answer}")
    print(f"Confidence: {response.confidence}")
    print(f"Sources: {len(response.sources)} documents")
    
    # Test another query
    query_text = "How does Thai massage work?"
    print(f"\nQuery: {query_text}")
    
    response = rag_system.query(query_text)
    print(f"Response: {response.answer}")
    print(f"Confidence: {response.confidence}")
    print(f"Sources: {len(response.sources)} documents")
    
    print("\nRAG pipeline test completed successfully!")

if __name__ == "__main__":
    test_rag_pipeline()