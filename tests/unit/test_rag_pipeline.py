"""
Unit tests for the RAG pipeline implementation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.rag.pipeline import RAGPipeline, RAGConfig, create_rag_pipeline
from src.rag.chunker import DocumentChunk, ChunkConfig
from src.rag.embeddings import EmbeddingConfig


class TestRAGPipeline:
    """Test suite for RAG pipeline."""
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing."""
        return [
            {
                "id": "doc1",
                "content": "Traditional Thai medicine uses herbs like turmeric and ginger for healing.",
                "metadata": {"source": "test", "category": "herbal"}
            },
            {
                "id": "doc2",
                "content": "Thai massage combines acupressure and yoga-like stretching techniques.",
                "metadata": {"source": "test", "category": "massage"}
            }
        ]
    
    @pytest.fixture
    def mock_embedding_generator(self):
        """Mock embedding generator."""
        mock = Mock()
        mock.get_embedding_dimension.return_value = 384
        mock.generate_embedding.return_value = np.random.rand(384)
        mock.embed_chunks.return_value = []
        return mock
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        mock = Mock()
        mock.store_chunk_embeddings_batch.return_value = 2
        mock.similarity_search.return_value = []
        mock.get_statistics.return_value = {
            "total_chunks": 0,
            "unique_documents": 0
        }
        return mock
    
    def test_pipeline_initialization(self):
        """Test RAG pipeline initialization."""
        config = RAGConfig(
            chunk_config=ChunkConfig(chunk_size=256),
            embedding_config=EmbeddingConfig(model_name="test-model")
        )
        
        with patch('src.rag.pipeline.EmbeddingGenerator') as mock_emb:
            mock_emb.return_value.get_embedding_dimension.return_value = 384
            with patch('src.rag.pipeline.VectorStore'):
                pipeline = RAGPipeline(config)
                assert pipeline.config == config
    
    def test_process_documents(self, sample_documents, mock_embedding_generator, mock_vector_store):
        """Test document processing."""
        with patch('src.rag.pipeline.EmbeddingGenerator', return_value=mock_embedding_generator):
            with patch('src.rag.pipeline.VectorStore', return_value=mock_vector_store):
                pipeline = RAGPipeline()
                
                # Mock chunker to return chunks
                mock_chunks = [
                    DocumentChunk(
                        chunk_id="chunk1",
                        document_id="doc1",
                        content="Test chunk 1",
                        chunk_index=0,
                        start_char=0,
                        end_char=10,
                        metadata={}
                    ),
                    DocumentChunk(
                        chunk_id="chunk2",
                        document_id="doc1",
                        content="Test chunk 2",
                        chunk_index=1,
                        start_char=10,
                        end_char=20,
                        metadata={}
                    )
                ]
                pipeline.chunker.process_documents = Mock(return_value=mock_chunks)
                
                # Mock embedding generator
                mock_embedding_generator.embed_chunks.return_value = [
                    (mock_chunks[0], np.random.rand(384)),
                    (mock_chunks[1], np.random.rand(384))
                ]
                
                # Process documents
                stats = pipeline.process_documents(sample_documents)
                
                assert stats["documents_processed"] == 2
                assert stats["chunks_created"] == 2
                assert stats["chunks_stored"] == 2
    
    def test_retrieve(self, mock_embedding_generator, mock_vector_store):
        """Test document retrieval."""
        with patch('src.rag.pipeline.EmbeddingGenerator', return_value=mock_embedding_generator):
            with patch('src.rag.pipeline.VectorStore', return_value=mock_vector_store):
                pipeline = RAGPipeline()
                
                # Mock search results
                mock_chunk = DocumentChunk(
                    chunk_id="chunk1",
                    document_id="doc1",
                    content="Thai herbal medicine",
                    chunk_index=0,
                    start_char=0,
                    end_char=20,
                    metadata={}
                )
                mock_vector_store.similarity_search.return_value = [
                    (mock_chunk, 0.85)
                ]
                
                # Retrieve documents
                results = pipeline.retrieve("What are Thai herbs?")
                
                assert len(results) == 1
                assert results[0][0].content == "Thai herbal medicine"
                assert results[0][1] == 0.85
    
    def test_query(self, mock_embedding_generator, mock_vector_store):
        """Test full query pipeline."""
        with patch('src.rag.pipeline.EmbeddingGenerator', return_value=mock_embedding_generator):
            with patch('src.rag.pipeline.VectorStore', return_value=mock_vector_store):
                pipeline = RAGPipeline()
                
                # Mock search results
                mock_chunk = DocumentChunk(
                    chunk_id="chunk1",
                    document_id="doc1",
                    content="Thai traditional medicine uses herbs",
                    chunk_index=0,
                    start_char=0,
                    end_char=30,
                    metadata={"source": "test"}
                )
                mock_vector_store.similarity_search.return_value = [
                    (mock_chunk, 0.9)
                ]
                
                # Execute query
                result = pipeline.query("Thai herbs")
                
                assert result["query"] == "Thai herbs"
                assert result["num_results"] == 1
                assert "context" in result
                assert "sources" in result
                assert "combined_context" in result
    
    def test_add_document(self, mock_embedding_generator, mock_vector_store):
        """Test adding a single document."""
        with patch('src.rag.pipeline.EmbeddingGenerator', return_value=mock_embedding_generator):
            with patch('src.rag.pipeline.VectorStore', return_value=mock_vector_store):
                pipeline = RAGPipeline()
                
                # Mock process_documents
                pipeline.process_documents = Mock(return_value={"chunks_stored": 3})
                
                # Add document
                success = pipeline.add_document(
                    "doc3",
                    "Thai massage techniques",
                    {"category": "massage"}
                )
                
                assert success is True
                pipeline.process_documents.assert_called_once()
    
    def test_get_statistics(self, mock_embedding_generator, mock_vector_store):
        """Test getting system statistics."""
        with patch('src.rag.pipeline.EmbeddingGenerator', return_value=mock_embedding_generator):
            with patch('src.rag.pipeline.VectorStore', return_value=mock_vector_store):
                pipeline = RAGPipeline()
                
                # Mock statistics
                mock_embedding_generator.get_model_info.return_value = {
                    "model_name": "test-model",
                    "embedding_dimension": 384
                }
                
                stats = pipeline.get_statistics()
                
                assert "vector_store" in stats
                assert "embedding_model" in stats
                assert "chunker_config" in stats
                assert "retrieval_config" in stats


class TestCreateRAGPipeline:
    """Test pipeline creation helper."""
    
    def test_create_default_pipeline(self):
        """Test creating pipeline with default settings."""
        with patch('src.rag.pipeline.EmbeddingGenerator') as mock_emb:
            mock_emb.return_value.get_embedding_dimension.return_value = 384
            with patch('src.rag.pipeline.VectorStore'):
                pipeline = create_rag_pipeline()
                assert pipeline is not None
                assert pipeline.config.top_k == 5
    
    def test_create_custom_pipeline(self):
        """Test creating pipeline with custom settings."""
        with patch('src.rag.pipeline.EmbeddingGenerator') as mock_emb:
            mock_emb.return_value.get_embedding_dimension.return_value = 768
            with patch('src.rag.pipeline.VectorStore'):
                pipeline = create_rag_pipeline(
                    chunk_size=1024,
                    chunk_overlap=100,
                    model_name="custom-model",
                    top_k=10
                )
                assert pipeline is not None
                assert pipeline.config.top_k == 10
                assert pipeline.chunker.config.chunk_size == 1024
