"""
Intent and language agent (lightweight stub).

Analyzes a query (and optional headers) to infer:
- persona: one of ["clinician","pharmacist","wellness","tourist"]
- language: one of ["th","en","mixed"]

This stub uses simple heuristics and is intended to be replaced by a
Pydantic-AI agent later without changing call sites.
"""

from __future__ import annotations

from typing import Dict, Tuple


THAI_CHARS = tuple(
    [chr(c) for c in range(0x0E00, 0x0E7F + 1)]
)  # Basic range of Thai unicode block


def _has_thai(text: str) -> bool:
    return any(ch in text for ch in THAI_CHARS)


def _has_english(text: str) -> bool:
    return any(("a" <= ch.lower() <= "z") for ch in text)


def _guess_language(query: str) -> str:
    has_th = _has_thai(query)
    has_en = _has_english(query)
    if has_th and has_en:
        return "mixed"
    if has_th:
        return "th"
    return "en"


def _guess_persona(query: str) -> str:
    ql = query.lower()
    if any(k in ql for k in ["contraindication", "pregnancy", "renal", "hepatic", "interaction", "dosage", "dose"]):
        return "clinician"
    if any(k in ql for k in ["pharmacokinetic", "pharmacodynamic", "dispense", "prescription"]):
        return "pharmacist"
    if any(k in ql for k in ["tour", "travel", "visitor", "foreigner"]):
        return "tourist"
    return "wellness"


def analyze(query: str, headers: Dict[str, str] | None = None) -> Tuple[str, str]:
    """
    Analyze query + optional headers and return (persona, language).
    Heuristics can be refined to use headers (e.g., roles) if provided.
    """
    language = _guess_language(query)
    persona = _guess_persona(query)
    # headers-based override (optional, conservative)
    if headers:
        role = (headers.get("x-user-role") or headers.get("x-role") or "").lower()
        if role in {"clinician", "doctor", "md"}:
            persona = "clinician"
        elif role in {"pharmacist", "rx"}:
            persona = "pharmacist"
    return persona, language
