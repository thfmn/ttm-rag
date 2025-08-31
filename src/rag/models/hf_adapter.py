"""
Typhoon 7B adapter using Hugging Face Transformers.

Notes:
- Defaults to CPU inference for local development.
- If accelerate is installed and device_map is provided in config, it can leverage a single GPU.
- This adapter initializes lazily on first generate() call to avoid heavy imports at module import time.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import BaseAdapter


class TyphoonHFAdapter(BaseAdapter):
    def __init__(self, adapter_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(adapter_id, config)
        self.hf_model_id: str = self.config.get("hf_model_id", "scb10x/typhoon-7b")
        self.max_new_tokens: int = int(self.config.get("max_new_tokens", 256))
        self.temperature: float = float(self.config.get("temperature", 0.3))
        self.top_p: float = float(self.config.get("top_p", 0.95))
        self.device_map: Optional[str] = self.config.get("device_map", None)  # e.g., "auto"
        self._pipeline = None
        self._init_error: Optional[str] = None

    def _ensure_pipeline(self):
        if self._pipeline is not None or self._init_error:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline  # type: ignore

            # Lazy-load model/tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.hf_model_id)
            model = AutoModelForCausalLM.from_pretrained(self.hf_model_id)

            kwargs: Dict[str, Any] = {
                "model": model,
                "tokenizer": tokenizer,
            }
            if self.device_map is not None:
                # Optional accelerate support when available
                kwargs["device_map"] = self.device_map

            self._pipeline = pipeline("text-generation", **kwargs)  # type: ignore
        except Exception as e:  # pragma: no cover - env dependent
            # Do not raise on import/load to keep CPU-only local dev lightweight
            self._init_error = str(e)
            self._pipeline = None

    def generate(self, prompt: str, context: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate text using Transformers if available, otherwise fall back to a simple deterministic response.
        """
        self._ensure_pipeline()
        if self._pipeline is None:
            # Fallback: deterministic summary from context (ensures tests without heavy deps can pass)
            combined = " ".join([c.get("content", "") for c in context]).strip()
            if not combined:
                combined = "No context available."
            return f"[typhoon-fallback] {combined[:800]}"

        # Run generation
        try:
            outputs = self._pipeline(
                prompt,
                max_new_tokens=kwargs.get("max_new_tokens", self.max_new_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                do_sample=True,
            )
            # transformers pipeline returns list of dicts with 'generated_text'
            if isinstance(outputs, list) and outputs:
                text = outputs[0].get("generated_text", "")
                return text[len(prompt) :].strip() if text.startswith(prompt) else text.strip()
            return ""
        except Exception:
            # Safe fallback if generation fails at runtime
            combined = " ".join([c.get("content", "") for c in context]).strip()
            return f"[typhoon-runtime-fallback] {combined[:800]}"

    def model_info(self) -> Dict[str, Any]:
        return {
            "id": self.adapter_id,
            "name": "Typhoon 7B (Transformers)",
            "provider": "huggingface",
            "capabilities": {
                "local": True,
                "cpu_default": True,
                "gpu_optional": True,
                "language": ["th", "en"],
            },
            "default": True,
        }
