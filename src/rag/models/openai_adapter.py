"""
OpenAI adapter using the official SDK (if available) with safe fallbacks.

- Does NOT import openai at module import time to avoid hard dependency.
- Reads OPENAI_API_KEY from environment at runtime.
- If SDK or API key is missing, returns a deterministic fallback using provided context.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .base import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    def __init__(self, adapter_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(adapter_id, config)
        # Allow overriding model name; default to a lightweight model
        self.model_name: str = self.config.get("model_name", "gpt-4o-mini")
        # Basic timeouts; only used if SDK is present
        self.request_timeout: float = float(self.config.get("request_timeout", 30.0))

    def _load_client(self):
        """
        Lazy-load the OpenAI client to avoid import errors if package not installed.
        Returns (client, api_key) or (None, None) on failure.
        """
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return None, None
        try:
            import openai  # type: ignore
            # New OpenAI SDK v1 style
            try:
                client = openai.OpenAI(api_key=api_key, timeout=self.request_timeout)
            except Exception:
                # Fallback for older SDKs
                openai.api_key = api_key
                client = openai
            return client, api_key
        except Exception:
            return None, None

    def generate(self, prompt: str, context: List[Dict[str, Any]], **kwargs) -> str:
        client, api_key = self._load_client()
        if client is None or api_key is None:
            # Fallback behavior with no network dependency
            combined = " ".join([c.get("content", "") for c in context]).strip()
            if not combined:
                combined = "No context available."
            return f"[openai-fallback:{self.model_name}] {combined[:800]}"

        # Try new SDK response
        try:
            # New SDK (Responses API)
            if hasattr(client, "responses"):
                resp = client.responses.create(
                    model=kwargs.get("model_name", self.model_name),
                    input=prompt,
                    max_output_tokens=kwargs.get("max_tokens", 256),
                    temperature=kwargs.get("temperature", 0.3),
                )
                # Extract text
                if hasattr(resp, "output") and hasattr(resp.output, "text"):
                    return (resp.output.text or "").strip()
                # Some SDK variants pack content differently
                text = getattr(resp, "text", None) or ""
                return text.strip()
            # Older Chat Completions
            if hasattr(client, "ChatCompletion"):
                resp = client.ChatCompletion.create(
                    model=kwargs.get("model_name", self.model_name),
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=kwargs.get("max_tokens", 256),
                    temperature=kwargs.get("temperature", 0.3),
                )
                choices = resp.get("choices") or []
                if choices:
                    msg = choices[0].get("message", {})
                    return (msg.get("content") or "").strip()
            # Older Completions
            if hasattr(client, "Completion"):
                resp = client.Completion.create(
                    model=kwargs.get("model_name", self.model_name),
                    prompt=prompt,
                    max_tokens=kwargs.get("max_tokens", 256),
                    temperature=kwargs.get("temperature", 0.3),
                )
                choices = resp.get("choices") or []
                if choices:
                    txt = choices[0].get("text") or ""
                    return txt.strip()
        except Exception:
            pass

        # Final fallback if SDK call failed
        combined = " ".join([c.get("content", "") for c in context]).strip()
        return f"[openai-runtime-fallback:{self.model_name}] {combined[:800]}"

    def model_info(self) -> Dict[str, Any]:
        return {
            "id": self.adapter_id,
            "name": f"OpenAI {self.model_name}",
            "provider": "openai",
            "capabilities": {"tools": False, "streaming": True},
            "default": False,
        }
