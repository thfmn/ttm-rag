"""
Planner agent (lightweight stub).

Generates a QueryPlan based on query, persona, and domain route.
"""

from __future__ import annotations

from typing import Dict, Literal, cast

from src.agents.common.types import QueryPlan

Persona = Literal["clinician", "pharmacist", "wellness", "tourist"]
Language = Literal["th", "en", "mixed"]
DomainRoute = Literal["interactions", "dosage", "contraindications", "preparation", "general"]


def plan(query: str, persona: str, route: str, default_top_k: int = 5) -> QueryPlan:
    """
    Produce a simple QueryPlan using heuristics on persona/route.

    Retrieval mix is a dict like {"bm25": 0.3, "dense": 0.7}.
    """
    mix: Dict[str, float] = {"dense": 0.7, "bm25": 0.3}

    # Adjust mix per route
    r = route
    if r == "interactions":
        mix = {"dense": 0.6, "bm25": 0.4}
    elif r == "dosage":
        mix = {"dense": 0.5, "bm25": 0.5}
    elif r == "contraindications":
        mix = {"dense": 0.65, "bm25": 0.35}
    elif r == "preparation":
        mix = {"dense": 0.55, "bm25": 0.45}
    else:
        mix = {"dense": 0.7, "bm25": 0.3}

    # Adjust top_k per persona (clinicians often want more context)
    tk = default_top_k
    if persona == "clinician":
        tk = max(default_top_k, 6)
    elif persona == "pharmacist":
        tk = max(default_top_k, 5)
    else:
        tk = default_top_k

    # Normalize mix to sum to 1.0
    total = sum(mix.values()) or 1.0
    mix = {k: float(v) / float(total) for k, v in mix.items()}

    # Language is guessed upstream by intent agent; set mixed as placeholder.
    language = "mixed"

    persona_val: Persona = cast(Persona, persona if persona in {"clinician", "pharmacist", "wellness", "tourist"} else "wellness")
    language_val: Language = cast(Language, language if language in {"th", "en", "mixed"} else "mixed")
    route_val: DomainRoute = cast(DomainRoute, r if r in {"interactions", "dosage", "contraindications", "preparation", "general"} else "general")

    return QueryPlan(
        persona=persona_val,
        language=language_val,
        domain_route=route_val,
        retrieval_mix=mix,
        top_k=int(tk),
    )
