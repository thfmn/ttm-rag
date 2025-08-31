"""
Unit tests for src.api.rag_router:
- GET /api/v1/rag/models returns model list
- POST /api/v1/rag/query passes through model and filter_metadata
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

import src.api.rag_router as rr_module


def make_app(pipeline_override: Any | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(rr_module.router)
    if pipeline_override is not None:
        app.dependency_overrides[rr_module.get_rag_pipeline] = lambda: pipeline_override
    return app


def test_get_models_returns_registry_list():
    app = make_app()
    client = TestClient(app)

    fake_models = [
        {"id": "hf-typhoon-7b", "name": "Typhoon 7B (Transformers)", "provider": "huggingface", "default": True},
        {"id": "openai-gpt-4o-mini", "name": "OpenAI GPT-4o-mini", "provider": "openai"},
        {"id": "qwen3-code", "name": "Qwen3-Code", "provider": "qwen"},
    ]

    with patch("src.rag.models.registry.get_model_list", return_value=fake_models):
        res = client.get("/api/v1/rag/models")
        assert res.status_code == 200
        data = res.json()
        assert "models" in data
        assert isinstance(data["models"], list)
        assert len(data["models"]) >= 3
        ids = {m["id"] for m in data["models"]}
        assert "hf-typhoon-7b" in ids
        assert "qwen3-code" in ids
        assert any(m.get("provider") == "openai" for m in data["models"])


def test_post_query_passthrough_model_and_filters():
    # Stub pipeline result
    stub_result: Dict[str, Any] = {
        "query": "Thai herbs",
        "num_results": 0,
        "retrieval_time": 0.01,
        "answer": "stub",
        "context": [],
        "sources": [],
        "combined_context": "",
    }

    pipeline_mock = MagicMock()
    pipeline_mock.query.return_value = stub_result

    app = make_app(pipeline_override=pipeline_mock)
    client = TestClient(app)

    payload = {
        "query": "Thai herbs",
        "model": "hf-typhoon-7b",
        "filter_metadata": {"source_type": "pubmed", "lang": "th"},
    }

    res = client.post("/api/v1/rag/query", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["query"] == "Thai herbs"
    assert "combined_context" in body

    # Verify passthrough of model and filters
    assert pipeline_mock.query.called
    _, kwargs = pipeline_mock.query.call_args
    assert kwargs.get("model") == "hf-typhoon-7b"
    assert kwargs.get("filter_metadata") == {"source_type": "pubmed", "lang": "th"}
