"""
Unit tests for query-time planner and router stubs.
"""

from __future__ import annotations

from src.agents.query import router_agent, planner_agent
from src.agents.common.types import QueryPlan


def test_router_routes_basic_keywords():
    assert router_agent.route("clinician", "Warfarin interaction with herb") == "interactions"
    assert router_agent.route("clinician", "Recommended dosage 500 mg") == "dosage"
    assert router_agent.route("clinician", "Contraindications in pregnancy") == "contraindications"
    assert router_agent.route("wellness", "Preparation by decoction") == "preparation"
    assert router_agent.route("wellness", "General info") == "general"


def test_planner_outputs_valid_queryplan_types():
    route = "dosage"
    q = "Thai herb dosage guidance"
    plan: QueryPlan = planner_agent.plan(q, persona="clinician", route=route, default_top_k=5)
    assert isinstance(plan, QueryPlan)
    assert plan.persona in {"clinician", "pharmacist", "wellness", "tourist"}
    assert plan.language in {"th", "en", "mixed"}
    assert plan.domain_route in {"interactions", "dosage", "contraindications", "preparation", "general"}
    assert isinstance(plan.top_k, int) and plan.top_k >= 5
    # retrieval mix sums to 1
    assert abs(sum(plan.retrieval_mix.values()) - 1.0) < 1e-6
