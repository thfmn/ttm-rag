"""
Configuration and environment handling for the TTM MCP adapter.

Policy:
- Read-only adapter over gRPC/GraphQL services.
- No secrets logged. All keys via environment variables.
- Thai-first defaults, cross-lingual fallback configurable.

Install note (documented only):
  uv pip install pydantic pydantic-settings orjson
"""

from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel, Field


class MCPConfig(BaseModel):
    # Core API (REST base if needed) and gRPC endpoint for adapter calls
    ttm_api_url: str = Field(default_factory=lambda: os.getenv("TTM_API_URL", "http://localhost:8005"))
    ttm_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("TTM_API_KEY"))

    # gRPC host/port for core services (adapter calls should use gRPC, not internal imports)
    grpc_host: str = Field(default_factory=lambda: os.getenv("GRPC_HOST", "0.0.0.0"))
    grpc_port: int = Field(default_factory=lambda: int(os.getenv("GRPC_PORT") or os.getenv("API_GRPC_PORT") or "50051"))

    # Retrieval defaults
    embed_model_th: str = Field(default_factory=lambda: os.getenv("EMBED_MODEL_TH", "sentence-transformers/all-MiniLM-L6-v2"))
    embed_model_en: str = Field(default_factory=lambda: os.getenv("EMBED_MODEL_EN", "sentence-transformers/all-MiniLM-L6-v2"))
    search_topk: int = Field(default_factory=lambda: int(os.getenv("SEARCH_TOPK", "10")))
    rag_topk: int = Field(default_factory=lambda: int(os.getenv("RAG_TOPK", "5")))

    # Optional external MCP servers (not used here directly; documented for completeness)
    firecrawl_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("FIRECRAWL_API_KEY"))
    lightpanda_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("LIGHTPANDA_API_KEY"))
    context7_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("CONTEXT7_API_KEY"))

    # Policy thresholds (example; tune later)
    answer_conf_threshold: float = Field(default_factory=lambda: float(os.getenv("ANSWER_CONF_TAU", "0.6")))
    # Determinism seed is derived per-call from input hash; do not set a static seed here


def load_config() -> MCPConfig:
    """
    Construct the MCPConfig from environment variables.
    """
    return MCPConfig()
