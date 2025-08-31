"""
Qwen3-code adapter via an OpenAI-compatible HTTP API or vendor SDK.

- Tries to use an OpenAI-compatible endpoint if QWEN_BASE_URL and QWEN_API_KEY are set.
- Falls back to deterministic summary if HTTP client or env vars are unavailable.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .base import BaseAdapter


class QwenCodeAdapter(BaseAdapter):
    def __init__(self, adapter_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(adapter_id, config)
        # Allow overriding endpoint/model
        self.base_url: str = self.config.get("base_url", os.getenv("QWEN_BASE_URL", "").strip())
        self.api_key: str = self.config.get("api_key", os.getenv("QWEN_API_KEY", "").strip())
        self.model_name: str = self.config.get("model_name", "qwen3-code")
        self.timeout: float = float(self.config.get("timeout", 30.0))

    def _http_client(self):
        if not self.base_url or not self.api_key:
            return None
        try:
            import httpx  # type: ignore
            return httpx.Client(base_url=self.base_url, timeout=self.timeout, headers={"Authorization": f"Bearer {self.api_key}"})
        except Exception:
            return None

    def generate(self, prompt: str, context: List[Dict[str, Any]], **kwargs) -> str:
        client = self._http_client()
        if client is None:
            combined = " ".join([c.get("content", "") for c in context]).strip()
            if not combined:
                combined = "No context available."
            return f"[qwen-fallback:{self.model_name}] {combined[:800]}"
        try:
            # Assume OpenAI-compatible chat/completions
            payload = {
                "model": kwargs.get("model_name", self.model_name),
                "messages": [
                    {"role": "system", "content": "You are a helpful code assistant."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": kwargs.get("max_tokens", 256),
                "temperature": kwargs.get("temperature", 0.2),
            }
            resp = client.post("/v1/chat/completions", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                choices = (data or {}).get("choices") or []
                if choices:
                    msg = choices[0].get("message", {})
                    return (msg.get("content") or "").strip()
            # Try responses-like endpoint if available
            resp = client.post("/v1/responses", json={"model": self.model_name, "input": prompt})
            if resp.status_code == 200:
                data = resp.json()
                # vendor-specific; do best-effort extraction
                text = (data.get("text") if isinstance(data, dict) else "") or ""
                return (text or "").strip()
        except Exception:
            pass
        combined = " ".join([c.get("content", "") for c in context]).strip()
        return f"[qwen-runtime-fallback:{self.model_name}] {combined[:800]}"

    def model_info(self) -> Dict[str, Any]:
        return {
            "id": self.adapter_id,
            "name": "Qwen3-Code",
            "provider": "qwen",
            "capabilities": {"code": True, "streaming": True},
            "default": False,
        }
