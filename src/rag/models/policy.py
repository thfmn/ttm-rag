"""
Model policy selection (Phase 4 initial, dependency-light).

Provides a simple, configurable policy for adapter selection based on:
- persona
- language
- constraints (e.g., allow_external, max_cost_per_call)

This is a heuristic starter and can be replaced by a more advanced policy later.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.rag.models import registry as model_registry


# Static cost assumptions per call (USD), rough placeholders
_DEFAULT_COSTS: Dict[str, float] = {
    "hf-typhoon-7b": 0.0,              # local
    "openai-gpt-4o-mini": 0.003,       # example price; adjust as appropriate
    "qwen3-code": 0.0,                 # treat as local/zero for this policy
}


class ModelPolicySelector:
    def __init__(
        self,
        costs: Optional[Dict[str, float]] = None,
        default_model_id: str = "hf-typhoon-7b",
    ) -> None:
        self._models = model_registry.get_model_list()
        self._by_id = {m["id"]: m for m in self._models}
        self._costs = dict(_DEFAULT_COSTS)
        if costs:
            self._costs.update(costs)
        self._default = default_model_id if default_model_id in self._by_id else "hf-typhoon-7b"

    def list_models(self) -> List[Dict[str, Any]]:
        return list(self._models)

    def get_cost(self, model_id: str) -> float:
        return float(self._costs.get(model_id, 0.0))

    def select_model(
        self,
        *,
        persona: Optional[str] = None,
        language: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Return a model_id chosen by a simple policy:
        - If constraints.allow_external is False -> prefer local models
        - If constraints.max_cost_per_call is set, choose model within budget
        - Bias towards Thai-compatible local "hf-typhoon-7b" for Thai/mixed queries
        - Otherwise, allow openai-gpt-4o-mini if budget allows for general usage
        - Fallback to default model id
        """
        constraints = constraints or {}
        allow_external = bool(constraints.get("allow_external", False))
        max_cost = constraints.get("max_cost_per_call", None)
        try:
            max_cost = float(max_cost) if max_cost is not None else None
        except Exception:
            max_cost = None

        # Candidate ordering by preference under constraints
        candidates = [m["id"] for m in self._models]

        # Filter by external allowance (assume openai is external)
        if not allow_external:
            candidates = [mid for mid in candidates if self._by_id[mid].get("provider") != "openai"]

        # Budget filter if applicable
        if max_cost is not None:
            candidates = [mid for mid in candidates if self.get_cost(mid) <= max_cost]

        # Language bias: prefer local Thai-capable model for th/mixed
        lang = (language or "").lower()
        if lang in {"th", "mixed"} and "hf-typhoon-7b" in candidates:
            return "hf-typhoon-7b"

        # Persona bias (clinician might benefit from better summarization; allow external if permitted and within budget)
        if persona == "clinician" and allow_external and "openai-gpt-4o-mini" in candidates:
            return "openai-gpt-4o-mini"

        # Generic preference order if available in filtered set
        for pref in ["hf-typhoon-7b", "qwen3-code", "openai-gpt-4o-mini"]:
            if pref in candidates:
                return pref

        # Fallback to default if no candidate remains
        return self._default
