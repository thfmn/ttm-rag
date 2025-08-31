"""
Router agent (lightweight stub).

Routes a query given a persona into a domain_route:
one of ["interactions","dosage","contraindications","preparation","general"].
"""

from __future__ import annotations

from typing import Literal

DomainRoute = Literal["interactions", "dosage", "contraindications", "preparation", "general"]


def route(persona: str, query: str) -> DomainRoute:
    q = (query or "").lower()
    # Simple keyword heuristics (extend later)
    if any(k in q for k in ["interaction", "interact", "warfarin", "anticoagulant"]):
        return "interactions"
    if any(k in q for k in ["dose", "dosage", "mg", "ml", "วันละ", "ครั้ง"]):
        return "dosage"
    if any(k in q for k in ["contraindication", "avoid", "pregnancy", "pregnant", "หญิงตั้งครรภ์"]):
        return "contraindications"
    if any(k in q for k in ["prepare", "preparation", "decoction", "infusion", "ต้ม", "ชง"]):
        return "preparation"
    return "general"
