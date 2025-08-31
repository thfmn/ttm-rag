"""
Unit tests for VectorStore metadata filtering (SQLite fallback path).
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple
import numpy as np
import pytest

from src.rag.vector_store import VectorStore
from src.rag.chunker import DocumentChunk


def make_chunk(
    document_id: str,
    content: str,
    idx: int,
    metadata: Dict[str, Any] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=f"{document_id}_{idx}_unit",
        document_id=document_id,
        content=content,
        chunk_index=idx,
        start_char=0,
        end_char=len(content),
        metadata=metadata or {},
    )


def test_similarity_search_with_filter_metadata_sqlite_fallback(tmp_path):
    # Use a temporary on-disk sqlite DB to persist across sessions
    db_path = tmp_path / "test_filters.db"
    vs = VectorStore(database_url=f"sqlite:///{db_path}", embedding_dim=3)

    # Prepare chunks with different metadata
    chunks: List[Tuple[DocumentChunk, np.ndarray]] = [
        (
            make_chunk(
                "doc1",
                "Thai medicine chunk 1",
                0,
                {"source_type": "pubmed", "lang": "en", "reviewed": True},
            ),
            np.array([1.0, 0.0, 0.0]),
        ),
        (
            make_chunk(
                "doc2",
                "Thai medicine chunk 2",
                0,
                {"source_type": "pubmed", "lang": "th", "reviewed": False},
            ),
            np.array([0.9, 0.1, 0.0]),
        ),
        (
            make_chunk(
                "doc3",
                "Thai medicine chunk 3",
                0,
                {"source_type": "web", "lang": "en", "reviewed": True},
            ),
            np.array([0.8, 0.2, 0.0]),
        ),
    ]

    stored = vs.store_chunk_embeddings_batch(chunks)
    assert stored == len(chunks)

    # Query vector near first chunk
    q = np.array([1.0, 0.0, 0.0])

    # Filter by multiple metadata constraints
    res = vs.similarity_search(q, top_k=10, filter_metadata={"source_type": "pubmed", "reviewed": True})
    # Expect only doc1 to match both conditions
    assert len(res) == 1
    c, score = res[0]
    assert c.document_id == "doc1"
    assert c.metadata.get("source_type") == "pubmed"
    assert c.metadata.get("reviewed") is True
    assert 0.0 <= score <= 1.0

    # Filter by language only
    res2 = vs.similarity_search(q, top_k=10, filter_metadata={"lang": "en"})
    assert len(res2) >= 2
    for chunk, _ in res2:
        assert chunk.metadata.get("lang") == "en"

    # No matches case
    res3 = vs.similarity_search(q, top_k=10, filter_metadata={"source_type": "unknown"})
    assert res3 == []
