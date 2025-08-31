"""
Main RAG pipeline that integrates all components.

This module provides the complete RAG pipeline functionality,
combining document processing, embedding generation, storage, and retrieval.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
import logging
import time
from dataclasses import dataclass

from src.rag.chunker import DocumentChunker, DocumentChunk, ChunkConfig
from src.rag.embeddings import EmbeddingGenerator, EmbeddingConfig
from src.rag.vector_store import VectorStore
from src.rag.generation import TextGenerator, assemble_prompt
from src.rag.pipeline_ext import apply_preprocessors

logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Configuration for the RAG pipeline."""
    chunk_config: Optional[ChunkConfig] = None
    embedding_config: Optional[EmbeddingConfig] = None
    database_url: Optional[str] = None
    top_k: int = 5
    similarity_threshold: float = 0.3
    preprocessors: Optional[List[Callable]] = None


class RAGPipeline:
    """Main RAG pipeline for document processing and retrieval."""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize the RAG pipeline.
        
        Args:
            config: RAG configuration
        """
        self.config = config or RAGConfig()
        
        # Initialize components
        self.chunker = DocumentChunker(self.config.chunk_config)
        self.embedding_generator = EmbeddingGenerator(self.config.embedding_config)
        
        # Get embedding dimension from the model
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        self.vector_store = VectorStore(
            database_url=self.config.database_url,
            embedding_dim=embedding_dim
        )
        self.text_generator = TextGenerator()
        self.preprocessors = self.config.preprocessors or []
        
        logger.info("Initialized RAG pipeline")
    
    def process_documents(
        self, 
        documents: List[Dict[str, Any]], 
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Process documents through the complete RAG pipeline.
        
        Args:
            documents: List of documents with 'id', 'content', and optional 'metadata'
            batch_size: Number of chunks to process at once
            
        Returns:
            Processing statistics
        """
        start_time = time.time()
        
        # Step 1: Preprocess then chunk documents
        logger.info(f"Processing {len(documents)} documents")
        pre_docs = []
        for doc in documents:
            if getattr(self, "preprocessors", None):
                pre = apply_preprocessors(doc, self.preprocessors)
                merged_metadata = dict(doc.get("metadata", {}) or {})
                if pre.metadata:
                    merged_metadata.update(pre.metadata)
                if pre.audit:
                    merged_metadata["audit"] = pre.audit
                pre_docs.append({
                    "id": doc.get("id", ""),
                    "content": pre.content,
                    "metadata": merged_metadata,
                })
            else:
                pre_docs.append({
                    "id": doc.get("id", ""),
                    "content": doc.get("content", ""),
                    "metadata": dict(doc.get("metadata", {}) or {}),
                })
        all_chunks = self.chunker.process_documents(pre_docs)
        logger.info(f"Created {len(all_chunks)} chunks")
        
        # Step 2: Generate embeddings and store
        stored_count = 0
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            
            # Generate embeddings for batch
            chunks_with_embeddings = self.embedding_generator.embed_chunks(batch)
            
            # Store in vector database
            count = self.vector_store.store_chunk_embeddings_batch(chunks_with_embeddings)
            stored_count += count
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(all_chunks) + batch_size - 1)//batch_size}")
        
        elapsed_time = time.time() - start_time
        
        stats = {
            "documents_processed": len(documents),
            "chunks_created": len(all_chunks),
            "chunks_stored": stored_count,
            "processing_time": elapsed_time,
            "avg_time_per_doc": elapsed_time / len(documents) if documents else 0
        }
        
        logger.info(f"Processing complete: {stats}")
        return stats
    
    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        top_k = top_k or self.config.top_k
        
        # Generate query embedding
        logger.info(f"Processing query: {query[:100]}...")
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search for similar chunks
        results = self.vector_store.similarity_search(
            query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        # Filter by similarity threshold
        filtered_results = [
            (chunk, score) for chunk, score in results
            if score >= self.config.similarity_threshold
        ]
        
        logger.info(f"Found {len(filtered_results)} relevant chunks (threshold: {self.config.similarity_threshold})")
        return filtered_results
    
    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        return_context: bool = True,
        model: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        agentic: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None,
        use_policy: Optional[bool] = None,
        policy_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline.
        
        Args:
            query: Query text
            top_k: Number of results to retrieve
            return_context: Whether to return retrieved context
            model: Optional model adapter id to use for answer generation (adapter integration to be added)
            
        Returns:
            Dictionary with query results
        """
        start_time = time.time()
        
        # Agentic planning (optional)
        use_top_k = top_k
        plan = None
        if agentic:
            try:
                from src.agents.query import intent_agent, router_agent, planner_agent
                persona, language = intent_agent.analyze(query, headers or {})
                route = router_agent.route(persona, query)
                plan = planner_agent.plan(query, persona, route, default_top_k=top_k or self.config.top_k)
                use_top_k = plan.top_k
            except Exception as e:
                logger.error(f"Agentic planning failed: {e}")
                use_top_k = top_k or self.config.top_k

        # Retrieve relevant chunks
        results = self.retrieve(query, use_top_k, filter_metadata=filter_metadata)
        
        # Format response
        response = {
            "query": query,
            "num_results": len(results),
            "retrieval_time": time.time() - start_time,
            "answer": None,
        }
        
        context_chunks = []
        sources_set = set()
        combined_contents: List[str] = []
        if results:
            for chunk, score in results:
                context_chunks.append(
                    {
                        "content": chunk.content,
                        "score": score,
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                    }
                )
                # Collect sources from metadata if available, otherwise fallback to document_id
                src_val = None
                try:
                    src_val = (chunk.metadata or {}).get("source")
                except Exception:
                    src_val = None
                sources_set.add(src_val or chunk.document_id)
                combined_contents.append(chunk.content)
        
        if return_context:
            response["context"] = context_chunks

        # Enrich response schema for compatibility with existing tests
        response["sources"] = sorted(list(sources_set)) if sources_set else []
        response["combined_context"] = "\n\n".join(combined_contents) if combined_contents else ""

        # Generate answer (agentic path or adapter/default)
        if agentic:
            try:
                from src.agents.common.types import AnswerChunk as _AnswerChunk
                from src.agents.query import synthesizer_agent, safety_adjudicator
                ans_chunks = []
                for chunk, score in results:
                    ans_chunks.append(
                        _AnswerChunk(
                            content=chunk.content,
                            score=float(score),
                            document_id=chunk.document_id,
                            chunk_index=chunk.chunk_index,
                        )
                    )
                planned = synthesizer_agent.synthesize(query, ans_chunks)
                adjudicated = safety_adjudicator.adjudicate(planned)
                response["answer"] = adjudicated.answer
            except Exception as e:
                logger.error(f"Agentic synthesis failed: {e}")
                response["answer"] = self.text_generator.generate_answer(query, context_chunks)
        elif model:
            try:
                from src.rag.models import registry as model_registry
                prompt = assemble_prompt(query, context_chunks)
                adapter = model_registry.get_adapter(model, config={})
                response["answer"] = adapter.generate(prompt, context_chunks)
            except Exception as e:
                logger.error(f"Adapter generation failed for model '{model}': {e}")
                response["answer"] = self.text_generator.generate_answer(query, context_chunks)
        elif use_policy:
            try:
                # Select model via policy using persona/language from intent analysis (non-agentic policy).
                from src.agents.query import intent_agent as _intent_agent
                from src.rag.models.policy import ModelPolicySelector
                persona, language = _intent_agent.analyze(query, headers or {})
                selector = ModelPolicySelector()
                selected_model = selector.select_model(
                    persona=persona, language=language, constraints=policy_constraints or {}
                )
                from src.rag.models import registry as model_registry
                prompt = assemble_prompt(query, context_chunks)
                adapter = model_registry.get_adapter(selected_model, config={})
                response["answer"] = adapter.generate(prompt, context_chunks)
            except Exception as e:
                logger.error(f"Policy-based adapter selection failed: {e}")
                response["answer"] = self.text_generator.generate_answer(query, context_chunks)
        else:
            response["answer"] = self.text_generator.generate_answer(query, context_chunks)

        return response
    
    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a single document to the RAG system.
        
        Args:
            document_id: Document ID
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        try:
            # Process single document
            result = self.process_documents([{
                "id": document_id,
                "content": content,
                "metadata": metadata or {}
            }])
            
            return result["chunks_stored"] > 0
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Number of chunks deleted
        """
        chunks = self.vector_store.get_chunks_by_document(document_id)
        deleted_count = 0
        
        for chunk in chunks:
            if self.vector_store.delete_chunk(chunk.chunk_id):
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
        return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with system statistics
        """
        vector_stats = self.vector_store.get_statistics()
        embedding_info = self.embedding_generator.get_model_info()
        
        return {
            "vector_store": vector_stats,
            "embedding_model": embedding_info,
            "chunker_config": {
                "chunk_size": self.chunker.config.chunk_size,
                "chunk_overlap": self.chunker.config.chunk_overlap,
                "preserve_sentences": self.chunker.config.preserve_sentences
            },
            "retrieval_config": {
                "top_k": self.config.top_k,
                "similarity_threshold": self.config.similarity_threshold
            }
        }
    
    def clear_cache(self):
        """Clear embedding cache to free memory."""
        if hasattr(self.embedding_generator, "clear_cache"):
            self.embedding_generator.clear_cache()  # type: ignore[attr-defined]
        logger.info("Cleared embedding cache")


# Convenience function for creating a default RAG pipeline
def create_rag_pipeline(
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    database_url: Optional[str] = None,
    top_k: int = 5,
    preprocessors: Optional[List[Callable]] = None,
) -> RAGPipeline:
    """
    Create a RAG pipeline with custom configuration.
    
    Args:
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        model_name: Embedding model name
        database_url: Database URL
        top_k: Number of results to retrieve
        
    Returns:
        Configured RAG pipeline
    """
    config = RAGConfig(
        chunk_config=ChunkConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        ),
        embedding_config=EmbeddingConfig(
            model_name=model_name
        ),
        database_url=database_url,
        top_k=top_k,
        preprocessors=preprocessors
    )
    
    return RAGPipeline(config)
