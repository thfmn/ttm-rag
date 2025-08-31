"""
Unit tests for the model adapter registry and per-request model override (TDD).
These tests are expected to fail initially until the adapter/registry layer is implemented.
"""

import pytest
from unittest.mock import patch, MagicMock


def test_registry_model_list_includes_required_models():
    """
    The registry should expose at least three models:
    - hf-typhoon-7b (Transformers)
    - openai-* (OpenAI SDK based)
    - qwen3-code (OpenAI-compatible/Qwen vendor)
    """
    import src.rag.models.registry as registry

    model_list = registry.get_model_list()
    assert isinstance(model_list, list)
    ids = {m.get("id") for m in model_list}
    assert "hf-typhoon-7b" in ids
    assert "qwen3-code" in ids
    # At least one OpenAI entry
    assert any(m.get("provider") == "openai" for m in model_list)
    assert len(model_list) >= 3


def test_pipeline_uses_adapter_when_model_overridden(monkeypatch):
    """
    RAGPipeline.query(..., model="hf-typhoon-7b") should delegate generation to adapter.
    """
    import numpy as np
    from src.rag.pipeline import RAGPipeline
    from src.rag.chunker import DocumentChunk

    # Patch EmbeddingGenerator and VectorStore inside pipeline to avoid heavy deps
    class DummyEmb:
        def get_embedding_dimension(self):
            return 384

        def generate_embedding(self, _q):
            return np.random.rand(384)

    class DummyVS:
        def __init__(self, *args, **kwargs):
            pass

        def similarity_search(self, *_args, **_kwargs):
            chunk = DocumentChunk(
                chunk_id="c1",
                document_id="docX",
                content="Thai herbal medicine context.",
                chunk_index=0,
                start_char=0,
                end_char=10,
                metadata={"source": "unit-test"},
            )
            return [(chunk, 0.95)]

    monkeypatch.setattr("src.rag.pipeline.EmbeddingGenerator", lambda *_a, **_k: DummyEmb())
    monkeypatch.setattr("src.rag.pipeline.VectorStore", lambda *_a, **_k: DummyVS())

    # Mock adapter and registry.get_adapter resolution path (to be introduced in pipeline)
    mock_adapter = MagicMock()
    mock_adapter.generate.return_value = "MOCK_ANSWER_FROM_ADAPTER"

    # This patch expects pipeline to import and use src.rag.models.registry.get_adapter
    with patch("src.rag.models.registry.get_adapter", return_value=mock_adapter) as get_adapter_mock:
        pipeline = RAGPipeline()
        result = pipeline.query("What herbs?", model="hf-typhoon-7b")

    # Expected after implementation:
    # - adapter used for answer generation
    # - answer equals adapter output
    # - get_adapter called with provided id
    assert result["query"] == "What herbs?"
    # Will fail until pipeline delegates to the adapter:
    assert result["answer"] == "MOCK_ANSWER_FROM_ADAPTER"
    get_adapter_mock.assert_called_once()
