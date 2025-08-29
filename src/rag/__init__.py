"""
RAG (Retrieval-Augmented Generation) system for Thai Traditional Medicine documents.

This module provides the core RAG functionality including document retrieval,
embedding generation, and response generation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import logging

# Import new implementation components
from src.rag.pipeline import RAGPipeline, RAGConfig, create_rag_pipeline
from src.rag.chunker import DocumentChunk, DocumentChunker, ChunkConfig
from src.rag.embeddings import EmbeddingGenerator, EmbeddingConfig
from src.rag.vector_store import VectorStore

# Set up logging
logger = logging.getLogger(__name__)

# Legacy classes for backward compatibility
class RagDocument(BaseModel):
    """Legacy document representation for backward compatibility."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class RagQuery(BaseModel):
    """Legacy query representation for backward compatibility."""
    text: str
    metadata: Optional[Dict[str, Any]] = None

class RagResponse(BaseModel):
    """Legacy response representation for backward compatibility."""
    answer: str
    sources: List[RagDocument]
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class RagSystem:
    """Main RAG system class - now using the new pipeline implementation."""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize the RAG system.
        
        Args:
            config: Optional RAG configuration
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing RAG system with new pipeline")
        
        # Initialize the new RAG pipeline
        self.pipeline = RAGPipeline(config)
    
    def process_documents(self, documents: List[RagDocument]) -> List[RagDocument]:
        """
        Process documents for RAG readiness (legacy interface).
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of processed documents with embeddings
        """
        # Convert to new format
        doc_dicts = [
            {
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata
            }
            for doc in documents
        ]
        
        # Process through pipeline
        stats = self.pipeline.process_documents(doc_dicts)
        self.logger.info(f"Processed documents: {stats}")
        
        # Return original documents (compatibility)
        return documents
    
    def retrieve_documents(self, query: RagQuery, top_k: int = 5) -> List[RagDocument]:
        """
        Retrieve relevant documents for a query (legacy interface).
        
        Args:
            query: Query to search for
            top_k: Number of top documents to retrieve
            
        Returns:
            List of relevant documents
        """
        # Use new pipeline retrieve
        results = self.pipeline.retrieve(query.text, top_k=top_k)
        
        # Convert to legacy format
        documents = []
        for chunk, score in results:
            doc = RagDocument(
                id=chunk.chunk_id,
                content=chunk.content,
                metadata={
                    **chunk.metadata,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "similarity_score": score
                }
            )
            documents.append(doc)
        
        return documents
    
    def generate_response(self, query: RagQuery, documents: List[RagDocument]) -> RagResponse:
        """
        Generate a response based on a query and retrieved documents (legacy interface).
        
        Args:
            query: Query to generate response for
            documents: Retrieved documents to use for generation
            
        Returns:
            Generated response
        """
        # Create context from documents
        if documents:
            context = "\n\n".join([doc.content for doc in documents])
            answer = f"Based on the retrieved context:\n\n{context[:500]}..."
            confidence = 0.8
        else:
            answer = "No relevant documents found for your query."
            confidence = 0.0
        
        return RagResponse(
            answer=answer,
            sources=documents,
            confidence=confidence,
            metadata={"query": query.text}
        )
    
    def query(self, query_text: str, top_k: int = 5) -> RagResponse:
        """
        Process a query through the full RAG pipeline (legacy interface).
        
        Args:
            query_text: Text of the query
            top_k: Number of top documents to retrieve
            
        Returns:
            Generated response
        """
        # Use new pipeline query
        result = self.pipeline.query(query_text, top_k=top_k)
        
        # Convert to legacy format
        documents = []
        if "context" in result:
            for ctx in result["context"]:
                doc = RagDocument(
                    id=f"{ctx['document_id']}_{ctx['chunk_index']}",
                    content=ctx["content"],
                    metadata={
                        "document_id": ctx["document_id"],
                        "chunk_index": ctx["chunk_index"],
                        "score": ctx["score"]
                    }
                )
                documents.append(doc)
        
        # Create response
        if result["num_results"] > 0:
            answer = f"Found {result['num_results']} relevant chunks. Context:\n\n{result.get('combined_context', '')[:500]}..."
            confidence = 0.8
        else:
            answer = "No relevant information found for your query."
            confidence = 0.0
        
        return RagResponse(
            answer=answer,
            sources=documents,
            confidence=confidence,
            metadata={"retrieval_time": result["retrieval_time"]}
        )
    
    #
