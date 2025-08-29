"""
Vector storage module for RAG system using PostgreSQL with pgvector.

This module provides functionality to store and retrieve document embeddings
using PostgreSQL's pgvector extension.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sqlalchemy import create_engine, text, Column, String, Integer, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
import logging
import json
from dataclasses import asdict

from src.rag.chunker import DocumentChunk

def get_database_url() -> str:
    """Get database URL from environment or use default SQLite."""
    import os
    return os.getenv("DATABASE_URL", "sqlite:///thai_medicine.db")

logger = logging.getLogger(__name__)

Base = declarative_base()

class ChunkEmbedding(Base):
    """SQLAlchemy model for storing chunk embeddings."""
    __tablename__ = 'chunk_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_id = Column(String, unique=True, nullable=False, index=True)
    document_id = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)
    embedding = Column(String, nullable=False)  # Will store as text, convert to vector
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VectorStore:
    """Handles vector storage and retrieval using PostgreSQL with pgvector."""
    
    def __init__(self, database_url: Optional[str] = None, embedding_dim: int = 384):
        """
        Initialize the vector store.
        
        Args:
            database_url: Database connection URL
            embedding_dim: Dimension of embedding vectors
        """
        self.database_url = database_url or get_database_url()
        self.embedding_dim = embedding_dim
        
        # Create engine and session
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Initialized VectorStore with embedding dimension {embedding_dim}")
    
    def _initialize_database(self):
        """Initialize database with pgvector extension and tables."""
        # First, create the tables using SQLAlchemy
        Base.metadata.create_all(bind=self.engine)
        logger.info("Created database tables")
        
        # Try to set up pgvector if using PostgreSQL
        if "postgresql" in self.database_url.lower():
            try:
                with self.engine.connect() as conn:
                    # Create pgvector extension if not exists
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    
                    # Add vector column if not exists (using raw SQL for pgvector)
                    conn.execute(text(f"""
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_name='chunk_embeddings' 
                                AND column_name='embedding_vector'
                            ) THEN
                                ALTER TABLE chunk_embeddings 
                                ADD COLUMN embedding_vector vector({self.embedding_dim});
                            END IF;
                        END $$;
                    """))
                    
                    # Create index for similarity search
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS chunk_embeddings_embedding_vector_idx 
                        ON chunk_embeddings 
                        USING ivfflat (embedding_vector vector_cosine_ops)
                        WITH (lists = 100)
                    """))
                    conn.commit()
                    
                logger.info("Database initialized with pgvector extension")
            except Exception as e:
                logger.warning(f"Could not initialize pgvector: {e}")
                logger.info("Falling back to text-based embedding storage")
        else:
            logger.info("Using SQLite with text-based embedding storage")
    
    def store_chunk_embedding(
        self, 
        chunk: DocumentChunk, 
        embedding: np.ndarray,
        session: Optional[Session] = None
    ) -> bool:
        """
        Store a chunk with its embedding in the database.
        
        Args:
            chunk: Document chunk to store
            embedding: Embedding vector
            session: Optional database session
            
        Returns:
            Success status
        """
        close_session = False
        if session is None:
            session = self.SessionLocal()
            close_session = True
        
        try:
            # Check if chunk already exists
            existing = session.query(ChunkEmbedding).filter_by(chunk_id=chunk.chunk_id).first()
            
            if existing:
                # Update existing chunk
                existing.content = chunk.content
                existing.chunk_metadata = chunk.metadata
                existing.embedding = json.dumps(embedding.tolist())
                existing.updated_at = datetime.now()
                
                # Update vector column if available
                try:
                    session.execute(
                        text("UPDATE chunk_embeddings SET embedding_vector = :vec WHERE chunk_id = :id"),
                        {"vec": f"[{','.join(map(str, embedding.tolist()))}]", "id": chunk.chunk_id}
                    )
                except:
                    pass  # pgvector not available
            else:
                # Create new chunk
                chunk_embedding = ChunkEmbedding(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    chunk_metadata=chunk.metadata,
                    embedding=json.dumps(embedding.tolist())
                )
                session.add(chunk_embedding)
                session.flush()
                
                # Set vector column if available
                try:
                    session.execute(
                        text("UPDATE chunk_embeddings SET embedding_vector = :vec WHERE chunk_id = :id"),
                        {"vec": f"[{','.join(map(str, embedding.tolist()))}]", "id": chunk.chunk_id}
                    )
                except:
                    pass  # pgvector not available
            
            session.commit()
            logger.debug(f"Stored chunk {chunk.chunk_id} with embedding")
            return True
            
        except Exception as e:
            logger.error(f"Error storing chunk embedding: {e}")
            session.rollback()
            return False
        finally:
            if close_session:
                session.close()
    
    def store_chunk_embeddings_batch(
        self,
        chunks_with_embeddings: List[Tuple[DocumentChunk, np.ndarray]]
    ) -> int:
        """
        Store multiple chunks with embeddings in batch.
        
        Args:
            chunks_with_embeddings: List of (chunk, embedding) tuples
            
        Returns:
            Number of successfully stored chunks
        """
        session = self.SessionLocal()
        success_count = 0
        
        try:
            for chunk, embedding in chunks_with_embeddings:
                if self.store_chunk_embedding(chunk, embedding, session):
                    success_count += 1
            
            logger.info(f"Stored {success_count}/{len(chunks_with_embeddings)} chunks")
            return success_count
            
        finally:
            session.close()
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Search for similar chunks using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        session = self.SessionLocal()
        
        try:
            # Try pgvector similarity search first
            try:
                query_vec = f"[{','.join(map(str, query_embedding.tolist()))}]"
                
                # Build query with optional metadata filtering
                query = text("""
                    SELECT 
                        chunk_id, document_id, content, chunk_index,
                        start_char, end_char, chunk_metadata,
                        1 - (embedding_vector <=> :query_vec::vector) as similarity
                    FROM chunk_embeddings
                    WHERE embedding_vector IS NOT NULL
                    ORDER BY embedding_vector <=> :query_vec::vector
                    LIMIT :limit
                """)
                
                results = session.execute(query, {"query_vec": query_vec, "limit": top_k})
                
                chunks_with_scores = []
                for row in results:
                    chunk = DocumentChunk(
                        chunk_id=row.chunk_id,
                        document_id=row.document_id,
                        content=row.content,
                        chunk_index=row.chunk_index,
                        start_char=row.start_char,
                        end_char=row.end_char,
                        metadata=row.chunk_metadata or {}
                    )
                    chunks_with_scores.append((chunk, row.similarity))
                
                logger.info(f"Found {len(chunks_with_scores)} similar chunks using pgvector")
                return chunks_with_scores
                
            except Exception as e:
                logger.debug(f"pgvector search not available, falling back to numpy: {e}")
                
                # Fallback to numpy-based similarity search
                all_chunks = session.query(ChunkEmbedding).all()
                
                if not all_chunks:
                    return []
                
                # Calculate similarities
                similarities = []
                for chunk_record in all_chunks:
                    # Parse embedding from JSON
                    chunk_embedding = np.array(json.loads(chunk_record.embedding))
                    
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                    
                    # Create chunk object
                    chunk = DocumentChunk(
                        chunk_id=chunk_record.chunk_id,
                        document_id=chunk_record.document_id,
                        content=chunk_record.content,
                        chunk_index=chunk_record.chunk_index,
                        start_char=chunk_record.start_char,
                        end_char=chunk_record.end_char,
                        metadata=chunk_record.chunk_metadata or {}
                    )
                    
                    similarities.append((chunk, similarity))
                
                # Sort by similarity and return top-k
                similarities.sort(key=lambda x: x[1], reverse=True)
                return similarities[:top_k]
                
        finally:
            session.close()
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # Calculate dot product
        return float(np.dot(vec1_norm, vec2_norm))
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """
        Retrieve a chunk by its ID.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            Document chunk or None
        """
        session = self.SessionLocal()
        
        try:
            chunk_record = session.query(ChunkEmbedding).filter_by(chunk_id=chunk_id).first()
            
            if chunk_record:
                return DocumentChunk(
                    chunk_id=chunk_record.chunk_id,
                    document_id=chunk_record.document_id,
                    content=chunk_record.content,
                    chunk_index=chunk_record.chunk_index,
                    start_char=chunk_record.start_char,
                    end_char=chunk_record.end_char,
                    metadata=chunk_record.chunk_metadata or {}
                )
            return None
            
        finally:
            session.close()
    
    def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        """
        Retrieve all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
        """
        session = self.SessionLocal()
        
        try:
            chunk_records = session.query(ChunkEmbedding).filter_by(
                document_id=document_id
            ).order_by(ChunkEmbedding.chunk_index).all()
            
            chunks = []
            for record in chunk_records:
                chunk = DocumentChunk(
                    chunk_id=record.chunk_id,
                    document_id=record.document_id,
                    content=record.content,
                    chunk_index=record.chunk_index,
                    start_char=record.start_char,
                    end_char=record.end_char,
                    metadata=record.chunk_metadata or {}
                )
                chunks.append(chunk)
            
            return chunks
            
        finally:
            session.close()
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk from the store.
        
        Args:
            chunk_id: Chunk ID to delete
            
        Returns:
            Success status
        """
        session = self.SessionLocal()
        
        try:
            chunk = session.query(ChunkEmbedding).filter_by(chunk_id=chunk_id).first()
            if chunk:
                session.delete(chunk)
                session.commit()
                logger.info(f"Deleted chunk {chunk_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting chunk: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        session = self.SessionLocal()
        
        try:
            total_chunks = session.query(ChunkEmbedding).count()
            unique_documents = session.query(ChunkEmbedding.document_id).distinct().count()
            
            return {
                "total_chunks": total_chunks,
                "unique_documents": unique_documents,
                "embedding_dimension": self.embedding_dim,
                "database_url": self.database_url.split('@')[-1] if '@' in self.database_url else 'local'
            }
            
        finally:
            session.close()
