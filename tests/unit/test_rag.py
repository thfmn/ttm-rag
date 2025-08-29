"""
Test module for the RAG system.
"""

import pytest
from src.rag import RagSystem, RagDocument, RagQuery, RagResponse

def test_rag_system_initialization():
    """Test that the RAG system can be initialized."""
    rag_system = RagSystem()
    assert rag_system is not None

def test_rag_document_creation():
    """Test that RAG documents can be created."""
    doc = RagDocument(
        id="test-1",
        content="This is a test document.",
        metadata={"source": "test", "category": "medical"}
    )
    assert doc.id == "test-1"
    assert doc.content == "This is a test document."
    assert doc.metadata["source"] == "test"

def test_rag_query_creation():
    """Test that RAG queries can be created."""
    query = RagQuery(text="What are the benefits of Thai massage?")
    assert query.text == "What are the benefits of Thai massage?"

def test_rag_response_creation():
    """Test that RAG responses can be created."""
    response = RagResponse(
        answer="Thai massage has many benefits.",
        sources=[],
        confidence=0.85
    )
    assert response.answer == "Thai massage has many benefits."
    assert response.confidence == 0.85

def test_rag_system_process_documents():
    """Test that the RAG system can process documents."""
    rag_system = RagSystem()
    
    documents = [
        RagDocument(
            id="doc-1",
            content="Document 1 content",
            metadata={"source": "test"}
        ),
        RagDocument(
            id="doc-2",
            content="Document 2 content",
            metadata={"source": "test"}
        )
    ]
    
    processed_docs = rag_system.process_documents(documents)
    assert len(processed_docs) == 2
    assert processed_docs[0].id == "doc-1"

def test_rag_system_retrieve_documents():
    """Test that the RAG system can retrieve documents."""
    rag_system = RagSystem()
    
    query = RagQuery(text="Test query")
    documents = rag_system.retrieve_documents(query, top_k=3)
    assert isinstance(documents, list)
    # For now, this will return an empty list since implementation is incomplete

def test_rag_system_generate_response():
    """Test that the RAG system can generate responses."""
    rag_system = RagSystem()
    
    query = RagQuery(text="Test query")
    documents = []
    
    response = rag_system.generate_response(query, documents)
    assert isinstance(response, RagResponse)
    assert response.answer is not None
    assert response.confidence is not None

def test_rag_system_query():
    """Test that the RAG system can process queries."""
    rag_system = RagSystem()
    
    response = rag_system.query("What are the benefits of Thai massage?")
    assert isinstance(response, RagResponse)
    assert response.answer is not None

if __name__ == "__main__":
    pytest.main([__file__])