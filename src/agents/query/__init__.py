"""
Query-time agents for intent detection, routing, planning, synthesis, and safety adjudication (Phase 3).

These are lightweight, dependency-free stubs intended to be replaced by
Pydantic-AI agents later without changing call sites.
"""
from . import intent_agent
from . import router_agent
from . import planner_agent
from . import synthesizer_agent
from . import safety_adjudicator

__all__ = [
    "intent_agent",
    "router_agent",
    "planner_agent",
    "synthesizer_agent",
    "safety_adjudicator",
]
