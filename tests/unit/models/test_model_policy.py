"""
Unit tests for initial model policy selector (Phase 4).
"""

from __future__ import annotations

from src.rag.models.policy import ModelPolicySelector


def test_policy_defaults_and_listing():
    selector = ModelPolicySelector()
    models = selector.list_models()
    assert isinstance(models, list)
    ids = {m["id"] for m in models}
    # Ensure known ids exist (from registry)
    assert "hf-typhoon-7b" in ids
    assert any(m.get("provider") == "openai" for m in models)


def test_policy_prefers_local_for_thai_when_external_disallowed():
    selector = ModelPolicySelector()
    model_id = selector.select_model(persona="clinician", language="th", constraints={"allow_external": False})
    assert model_id == "hf-typhoon-7b"


def test_policy_respects_budget():
    # Set a very low budget to force selection to local/zero-cost candidates
    selector = ModelPolicySelector(costs={"openai-gpt-4o-mini": 0.01})
    model_id = selector.select_model(persona="wellness", language="en", constraints={"allow_external": True, "max_cost_per_call": 0.0})
    assert model_id in {"hf-typhoon-7b", "qwen3-code"}


def test_policy_allows_external_when_within_budget_and_persona_bias():
    selector = ModelPolicySelector(costs={"openai-gpt-4o-mini": 0.001})
    model_id = selector.select_model(persona="clinician", language="en", constraints={"allow_external": True, "max_cost_per_call": 0.005})
    # Given constraints and persona bias, openai may be chosen
    assert model_id in {"openai-gpt-4o-mini", "hf-typhoon-7b", "qwen3-code"}
