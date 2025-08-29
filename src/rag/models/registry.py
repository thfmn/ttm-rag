"""
Model adapter registry for pluggable text-generation backends.
"""

from __future__ import annotations

from typing import Any, Dict, List
import importlib

from .base import BaseAdapter


# Public model catalog returned to clients (backend/FE)
_AVAILABLE_MODELS: List[Dict[str, Any]] = [
    {
        "id": "hf-typhoon-7b",
        "name": "Typhoon 7B (Transformers)",
        "provider": "huggingface",
        "capabilities": {
            "local": True,
            "cpu_default": True,
            "gpu_optional": True,
            "language": ["th", "en"],
        },
        "default": True,
    },
    {
        "id": "openai-gpt-4o-mini",
        "name": "OpenAI GPT-4o-mini",
        "provider": "openai",
        "capabilities": {"tools": False, "streaming": True},
        "default": False,
    },
    {
        "id": "qwen3-code",
        "name": "Qwen3-Code",
        "provider": "qwen",
        "capabilities": {"code": True, "streaming": True},
        "default": False,
    },
]


# Mapping from adapter id to fully-qualified class path for lazy import
_ADAPTER_CLASS_PATHS: Dict[str, str] = {
    "hf-typhoon-7b": "src.rag.models.hf_adapter.TyphoonHFAdapter",
    "openai-gpt-4o-mini": "src.rag.models.openai_adapter.OpenAIAdapter",
    "qwen3-code": "src.rag.models.qwen_adapter.QwenCodeAdapter",
}


def get_model_list() -> List[Dict[str, Any]]:
    """
    Return the list of available models with metadata for selection UIs.
    """
    return list(_AVAILABLE_MODELS)


def get_adapter(adapter_id: str, config: Dict[str, Any] | None = None) -> BaseAdapter:
    """
    Construct and return an adapter instance for the given adapter_id.
    Uses lazy import to avoid optional dependency errors at import time.
    Raises ValueError if the adapter_id is unknown.
    """
    class_path = _ADAPTER_CLASS_PATHS.get(adapter_id)
    if not class_path:
        raise ValueError(f"Unknown adapter id: {adapter_id}")
    module_path, _, class_name = class_path.rpartition(".")
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(adapter_id=adapter_id, config=(config or {}))
