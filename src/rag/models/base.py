"""
Base adapter interface for generation backends used by the RAG pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAdapter(ABC):
    """
    Abstract base class for all model adapters.

    Adapters encapsulate the details of interacting with different generation backends
    (e.g., local Transformers, OpenAI SDK, OpenAI-compatible HTTP APIs).
    """

    def __init__(self, adapter_id: str, config: Optional[Dict[str, Any]] = None):
        self.adapter_id = adapter_id
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    def generate(self, prompt: str, context: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate text given a prompt and optional structured context.
        Implementations should return the raw generated text.
        """
        raise NotImplementedError

    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """
        Return a serializable dictionary describing the model (id, name, provider, capabilities).
        """
        raise NotImplementedError
