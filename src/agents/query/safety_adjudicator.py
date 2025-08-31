"""
Safety adjudicator agent (lightweight stub).

Takes a PlannedAnswer and may adjust disclaimers or safety_score.
"""

from __future__ import annotations

from typing import List

from src.agents.common.types import PlannedAnswer


def adjudicate(answer: PlannedAnswer) -> PlannedAnswer:
    """
    If the answer is not grounded (no citations), lower safety_score and add disclaimers.
    If the answer contains risky keywords, add an extra cautionary disclaimer.
    """
    a = answer.model_copy(deep=True)

    if not a.grounded:
        a.safety_score = float(min(a.safety_score, 0.5))
        extra = "This answer is not grounded to specific citations; verify with trusted sources."
        if extra not in a.disclaimers:
            a.disclaimers.append(extra)

    text = (a.answer or "").lower()
    risky = any(k in text for k in ["pregnancy", "pregnant", "warfarin", "anticoagulant", "bleeding"])
    if risky:
        extra2 = "Potential clinical risks mentioned; consult a qualified healthcare professional."
        if extra2 not in a.disclaimers:
            a.disclaimers.append(extra2)

    return a
