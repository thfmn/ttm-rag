"""
Unit tests for RAGPipeline preprocessors plumbing.
Ensures preprocessors run before chunking and their outputs are merged into metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from unittest.mock import patch
import numpy as np
import pytest


def test_preprocessors_applied_before_chunking(monkeypatch):
    """
    RAGPipeline.process_documents should:
    - apply preprocessors to each document
    - pass modified content to the chunker
    - merge returned metadata and audit into chunk metadata
    - proceed to embedding and storage without errors (stubbed)
    """
    from src.rag.pipeline import RAGPipeline, RAGConfig
    from src.rag.chunker import ChunkConfig

    # Dummy preprocessor: redact the word "secret" and attach pdpa metadata + audit
    def redact_preprocessor(doc: Dict[str, Any]) -> Dict[str, Any]:
        content = doc.get("content", "")
        cleaned = content.replace("secret", "[REDACTED]")
        return {
            "content": cleaned,
            "metadata": {"pdpa": True, "stage": "redacted"},
            "audit": {"redactions": [{"label": "PII", "count": content.count("secret")}]},
        }

    # Patch EmbeddingGenerator and VectorStore to avoid heavyweight deps
    class DummyEmb:
        def get_embedding_dimension(self) -> int:
            return 8

        def embed_chunks(self, chunks) -> List[Tuple[Any, np.ndarray]]:
            # Return simple unit vectors correlated with chunk_index for determinism
            out = []
            for ch in chunks:
                vec = np.zeros(8)
                vec[min(ch.chunk_index, 7)] = 1.0
                out.append((ch, vec))
            return out

        def generate_embedding(self, _q):
            return np.ones(8)

        def get_model_info(self) -> Dict[str, Any]:
            return {"model_name": "dummy", "dimension": 8}

        def clear_cache(self):
            pass

    class DummyVS:
        def __init__(self, *args, **kwargs):
            self.stored: List[Tuple[Any, np.ndarray]] = []

        def store_chunk_embeddings_batch(self, cw):
            # Capture what gets stored for assertions
            self.stored.extend(cw)
            return len(cw)

        def get_statistics(self):
            return {"total_chunks": len(self.stored), "unique_documents": 1, "embedding_dimension": 8, "database_url": "local"}

    monkeypatch.setattr("src.rag.pipeline.EmbeddingGenerator", lambda *_a, **_k: DummyEmb())
    monkeypatch.setattr("src.rag.pipeline.VectorStore", lambda *_a, **_k: DummyVS())

    cfg = RAGConfig(
        preprocessors=[redact_preprocessor],
        top_k=3,
        chunk_config=ChunkConfig(min_chunk_size=1, chunk_overlap=0, chunk_size=128),
    )
    pipeline = RAGPipeline(cfg)

    docs = [
        {
            "id": "doc-1",
            "content": "This is a secret Thai herb description. More secret notes.",
            "metadata": {"lang": "en"},
        }
    ]

    stats = pipeline.process_documents(docs, batch_size=10)
    assert stats["documents_processed"] == 1
    assert stats["chunks_stored"] >= 1

    # Validate that chunks passed through embedding store contain redacted content and merged metadata
    # Retrieve the stored batch from the DummyVS instance
    vs_instance = pipeline.vector_store  # type: ignore[attr-defined]
    stored = getattr(vs_instance, "stored", [])
    assert len(stored) >= 1

    for chunk, _vec in stored:
        # Content should no longer include "secret"
        assert "secret" not in chunk.content
        assert "[REDACTED]" in chunk.content
        # Metadata should include original + pdpa + audit
        assert chunk.metadata.get("lang") == "en"
        assert chunk.metadata.get("pdpa") is True
        assert chunk.metadata.get("stage") == "redacted"
        assert "audit" in chunk.metadata
        assert isinstance(chunk.metadata["audit"], dict)
