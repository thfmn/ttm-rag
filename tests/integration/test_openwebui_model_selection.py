"""
Integration tests for Open-WebUI TTM RAG router model listing and selection.

These tests mount the ttm_rag router in a FastAPI app with dependency overrides
to bypass authentication, and patch the RAG pipeline and model registry to verify
behavior without heavy dependencies.
"""
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the router module
import open_webui.backend.open_webui.routers.ttm_rag as ttm_rag_module


def make_app():
    app = FastAPI()

    # Dependency override: bypass auth
    def fake_get_verified_user():
        class Dummy:
            id = "user1"
            name = "Test User"

        return Dummy()

    # Apply override locally on the router dependency if needed
    # The router uses Depends(get_verified_user) inside handlers, so we patch the function
    app.dependency_overrides = {}

    # Include router at the same prefix it is mounted in backend main
    app.include_router(ttm_rag_module.router, prefix="/api/v1/ttm_rag", tags=["ttm_rag"])
    return app


def test_get_models_lists_three_or_more_models():
    app = make_app()
    client = TestClient(app)

    fake_models = [
        {"id": "hf-typhoon-7b", "name": "Typhoon 7B (Transformers)", "provider": "huggingface", "default": True},
        {"id": "openai-gpt-4o-mini", "name": "OpenAI GPT-4o-mini", "provider": "openai"},
        {"id": "qwen3-code", "name": "Qwen3-Code", "provider": "qwen"},
    ]

    with patch("open_webui.backend.open_webui.routers.ttm_rag.model_registry.get_model_list", return_value=fake_models):
        res = client.get("/api/v1/ttm_rag/models", headers={"Authorization": "Bearer TEST"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] is True
        assert "models" in data
        assert isinstance(data["models"], list)
        assert len(data["models"]) >= 3
        ids = {m["id"] for m in data["models"]}
        assert "hf-typhoon-7b" in ids
        assert "qwen3-code" in ids
        assert any(m.get("provider") == "openai" for m in data["models"])


def test_post_query_routes_to_pipeline_with_model_override():
    app = make_app()
    client = TestClient(app)

    # Patch rag_pipeline.query to verify it is called with model parameter and return a stubbed result
    stub_result = {
        "query": "Thai herbs",
        "num_results": 1,
        "retrieval_time": 0.01,
        "answer": "stub",
        "context": [],
        "sources": [],
        "combined_context": ""
    }

    with patch.object(ttm_rag_module, "rag_pipeline") as mock_pipeline:
        mock_pipeline.query.return_value = stub_result

        payload = {"query": "Thai herbs", "model": "hf-typhoon-7b"}
        res = client.post("/api/v1/ttm_rag/", json=payload, headers={"Authorization": "Bearer TEST"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] is True
        assert "results" in data
        assert data["results"]["query"] == "Thai herbs"
        mock_pipeline.query.assert_called_once()
        # Validate that our model override was passed through
        _, kwargs = mock_pipeline.query.call_args
        assert kwargs.get("model") == "hf-typhoon-7b"
