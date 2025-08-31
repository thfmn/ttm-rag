"""
FastAPI router for RAG endpoints.

This module provides REST API endpoints for the RAG system.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from src.rag.pipeline import create_rag_pipeline, RAGPipeline
from src.api.sanitization import sanitize_text, sanitize_dict

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

# Global RAG pipeline instance (singleton)
_rag_pipeline: Optional[RAGPipeline] = None

def get_rag_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        logger.info("Initializing RAG pipeline...")
        _rag_pipeline = create_rag_pipeline()
    return _rag_pipeline


# Request/Response models
class DocumentInput(BaseModel):
    """Input model for adding a document."""
    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Document metadata")


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str = Field(..., min_length=1, max_length=1000, description="Query text")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to retrieve")
    return_context: Optional[bool] = Field(True, description="Whether to return context")
    model: Optional[str] = Field(None, description="Optional model adapter id to use for answer generation")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filters applied at retrieval")
    agentic: Optional[bool] = Field(default=None, description="Enable agentic planner/synthesizer path")
    use_policy: Optional[bool] = Field(default=None, description="Enable policy-based model selection")
    policy_constraints: Optional[Dict[str, Any]] = Field(default=None, description="Constraints for policy (e.g., allow_external, max_cost_per_call)")


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    query: str
    num_results: int
    retrieval_time: float
    answer: Optional[str] = None
    context: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[str]] = None
    combined_context: Optional[str] = None


class ProcessingStats(BaseModel):
    """Statistics for document processing."""
    documents_processed: int
    chunks_created: int
    chunks_stored: int
    processing_time: float
    avg_time_per_doc: float


class SystemStats(BaseModel):
    """System statistics."""
    vector_store: Dict[str, Any]
    embedding_model: Dict[str, Any]
    chunker_config: Dict[str, Any]
    retrieval_config: Dict[str, Any]


@router.get("/models")
async def get_models():
    """
    Get available model adapters.
    """
    try:
        from src.rag.models import registry as model_registry
        return {"models": model_registry.get_model_list()}
    except Exception as e:
        logger.error(f"Error fetching model list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints
@router.post("/query", response_model=QueryResponse)
async def query_rag(
    http_request: Request,
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    """
    Query the RAG system with a text query.
    
    Args:
        request: Query request
        pipeline: RAG pipeline instance
        
    Returns:
        Query response with retrieved context
    """
    try:
        # Sanitize input
        clean_query = sanitize_text(request.query)
        
        # Execute query
        if request.model is not None:
            model = sanitize_text(request.model)
        else:
            model = None

        if request.filter_metadata is not None:
            clean_filters = sanitize_dict(request.filter_metadata)
        else:
            clean_filters = None

        # Collect headers (minimally) for agentic intent analysis if enabled
        headers_dict = dict(http_request.headers)
        if request.policy_constraints is not None:
            constraints = sanitize_dict(request.policy_constraints)
        else:
            constraints = None
        result = pipeline.query(
            clean_query,
            top_k=request.top_k,
            return_context=request.return_context if request.return_context is not None else True,
            model=model,
            filter_metadata=clean_filters,
            agentic=request.agentic if getattr(request, "agentic", None) is not None else None,
            headers=headers_dict if headers_dict else None,
            use_policy=request.use_policy if getattr(request, "use_policy", None) is not None else None,
            policy_constraints=constraints,
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents", response_model=Dict[str, bool])
async def add_document(
    document: DocumentInput,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Add a single document to the RAG system.
    
    Args:
        document: Document to add
        pipeline: RAG pipeline instance
        
    Returns:
        Success status
    """
    try:
        # Sanitize input
        clean_id = sanitize_text(document.id)
        clean_content = sanitize_text(document.content)
        clean_metadata = sanitize_dict(document.metadata) if document.metadata else {}
        
        # Add document
        success = pipeline.add_document(
            clean_id,
            clean_content,
            clean_metadata
        )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/batch", response_model=ProcessingStats)
async def process_documents_batch(
    documents: List[DocumentInput],
    batch_size: int = Query(10, ge=1, le=100),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Process multiple documents in batch.
    
    Args:
        documents: List of documents to process
        batch_size: Batch size for processing
        pipeline: RAG pipeline instance
        
    Returns:
        Processing statistics
    """
    try:
        # Convert and sanitize documents
        doc_dicts = []
        for doc in documents:
            doc_dicts.append({
                "id": sanitize_text(doc.id),
                "content": sanitize_text(doc.content),
                "metadata": sanitize_dict(doc.metadata) if doc.metadata else {}
            })
        
        # Process documents
        stats = pipeline.process_documents(doc_dicts, batch_size=batch_size)
        
        return ProcessingStats(**stats)
        
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Delete all chunks for a document.
    
    Args:
        document_id: Document ID to delete
        pipeline: RAG pipeline instance
        
    Returns:
        Number of chunks deleted
    """
    try:
        # Sanitize input
        clean_id = sanitize_text(document_id)
        
        # Delete document
        deleted_count = pipeline.delete_document(clean_id)
        
        return {"document_id": clean_id, "chunks_deleted": deleted_count}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=SystemStats)
async def get_statistics(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Get system statistics.
    
    Args:
        pipeline: RAG pipeline instance
        
    Returns:
        System statistics
    """
    try:
        stats = pipeline.get_statistics()
        return SystemStats(**stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Clear the embedding cache.
    
    Args:
        pipeline: RAG pipeline instance
        
    Returns:
        Success message
    """
    try:
        pipeline.clear_cache()
        return {"message": "Cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check RAG system health.
    
    Returns:
        Health status
    """
    try:
        pipeline = get_rag_pipeline()
        stats = pipeline.get_statistics()
        
        return {
            "status": "healthy",
            "total_chunks": stats["vector_store"]["total_chunks"],
            "unique_documents": stats["vector_store"]["unique_documents"],
            "embedding_model": stats["embedding_model"]["model_name"]
        }
        
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
