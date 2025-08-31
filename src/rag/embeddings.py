"""
Embedding generation module for RAG system.

This module provides functionality to generate vector embeddings
from text chunks using sentence transformers.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
# Lazy imports are performed in __init__ to avoid heavy deps at module import time.
# from sentence_transformers import SentenceTransformer  # moved to __init__
# import torch  # moved to __init__
import logging
import time
from dataclasses import dataclass
from src.rag.chunker import DocumentChunk

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight model for start
    batch_size: int = 32
    max_length: int = 512
    normalize_embeddings: bool = True
    device: Optional[str] = None  # None for auto-detect
    show_progress_bar: bool = False
    cache_embeddings: bool = True


class EmbeddingGenerator:
    """Handles embedding generation for document chunks."""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize the embedding generator.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        
        # Determine device (lazy import torch)
        try:
            import torch as _torch  # type: ignore
        except Exception:
            _torch = None

        if self.config.device is None:
            self.device = "cuda" if (_torch is not None and hasattr(_torch, "cuda") and _torch.cuda.is_available()) else "cpu"
        else:
            self.device = self.config.device

        # Initialize the model (lazy import sentence-transformers)
        logger.info(f"Loading embedding model: {self.config.model_name}")
        try:
            from sentence_transformers import SentenceTransformer as _SentenceTransformer  # type: ignore
        except Exception as e:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install with: uv pip install 'sentence-transformers>=5.1.0' 'torch>=2.1.0'"
            ) from e

        self.model = _SentenceTransformer(self.config.model_name, device=self.device)

        # Set max sequence length
        self.model.max_seq_length = self.config.max_length
        
        # Cache for embeddings (document_id -> embeddings)
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
        logger.info(f"Initialized EmbeddingGenerator with model {self.config.model_name} on {self.device}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        start_time = time.time()
        
        # Generate embedding
        embedding = self.model.encode(
            text,
            normalize_embeddings=self.config.normalize_embeddings,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
        logger.debug(f"Generated embedding in {elapsed_time:.2f}ms")
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embedding vectors
        """
        if not texts:
            return np.array([])
        
        start_time = time.time()
        
        # Generate embeddings in batch
        embeddings = self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=self.config.normalize_embeddings,
            show_progress_bar=self.config.show_progress_bar,
            convert_to_numpy=True
        )
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
        avg_time = elapsed_time / len(texts) if texts else 0
        logger.info(f"Generated {len(texts)} embeddings in {elapsed_time:.2f}ms (avg: {avg_time:.2f}ms/text)")
        
        return embeddings
    
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[Tuple[DocumentChunk, np.ndarray]]:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            List of tuples (chunk, embedding)
        """
        if not chunks:
            return []
        
        results = []
        texts_to_embed = []
        chunks_to_embed = []
        
        # Check cache and prepare texts to embed
        for chunk in chunks:
            if self.config.cache_embeddings and chunk.chunk_id in self.embedding_cache:
                # Use cached embedding
                logger.debug(f"Using cached embedding for chunk {chunk.chunk_id}")
                results.append((chunk, self.embedding_cache[chunk.chunk_id]))
            else:
                # Need to generate embedding
                texts_to_embed.append(chunk.content)
                chunks_to_embed.append(chunk)
        
        # Generate embeddings for uncached chunks
        if texts_to_embed:
            logger.info(f"Generating embeddings for {len(texts_to_embed)} chunks")
            embeddings = self.generate_embeddings_batch(texts_to_embed)
            
            # Combine with chunks and cache
            for chunk, embedding in zip(chunks_to_embed, embeddings):
                if self.config.cache_embeddings:
                    self.embedding_cache[chunk.chunk_id] = embedding
                results.append((chunk, embedding))
        
        logger.info(f"Processed {len(chunks)} chunks ({len(texts_to_embed)} new embeddings generated)")
        return results
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Ensure embeddings are normalized
        if not self.config.normalize_embeddings:
            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        return float(similarity)
    
    def find_similar_chunks(
        self, 
        query_embedding: np.ndarray, 
        chunk_embeddings: List[Tuple[DocumentChunk, np.ndarray]], 
        top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Find most similar chunks to a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            chunk_embeddings: List of (chunk, embedding) tuples
            top_k: Number of top results to return
            
        Returns:
            List of (chunk, similarity_score) tuples, sorted by similarity
        """
        if not chunk_embeddings:
            return []
        
        # Calculate similarities
        similarities = []
        for chunk, embedding in chunk_embeddings:
            similarity = self.calculate_similarity(query_embedding, embedding)
            similarities.append((chunk, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results
        return similarities[:top_k]
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.embedding_cache.clear()
        logger.info("Cleared embedding cache")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        dim = self.model.get_sentence_embedding_dimension()
        # Guard for Optional[int] typing in stubs
        return int(dim) if dim is not None else 0
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.config.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_sequence_length": self.model.max_seq_length,
            "device": self.device,
            "normalize_embeddings": self.config.normalize_embeddings,
            "cache_size": len(self.embedding_cache)
        }
