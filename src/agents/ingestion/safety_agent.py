"""
Safety check agent (lightweight stub).

Scans content for simple contraindication signals and returns a list of
warnings (strings). This is a minimal heuristic intended to be replaced
or augmented by a Pydantic-AI agent later.
"""

from __future__ import annotations

from typing import Any, Dict, List


THAI_EN_RISKS: List[str] = [
    "pregnancy",
    "pregnant",
    "breastfeeding",
    "เด็ก",
    "หญิงตั้งครรภ์",
    "ให้นมบุตร",
    "โรคตับ",
    "โรคไต",
    "ตับ",
    "ไต",
    "anticoagulant",
    "warfarin",
    "bleeding",
    "เลือดออก",
    "hypotension",
    "ความดันต่ำ",
]


def check_contraindications(content: str, metadata: Dict[str, Any] | None = None) -> List[str]:
    """
    Return a list of human-readable warnings detected from the text.
    """
    warnings: List[str] = []
    lower = content.lower()

    if any(k in lower for k in ["pregnancy", "pregnant", "หญิงตั้งครรภ์"]):
        warnings.append("Potential risk in pregnancy. Consult a clinician.")
    if any(k in lower for k in ["breastfeeding", "ให้นมบุตร"]):
        warnings.append("Potential risk in breastfeeding. Consult a clinician.")
    if any(k in lower for k in ["tub", "ตับ", "โรคตับ", "liver"]):
        warnings.append("Use caution in hepatic impairment.")
    if any(k in lower for k in ["ไต", "โรคไต", "renal", "kidney"]):
        warnings.append("Use caution in renal impairment.")
    if any(k in lower for k in ["warfarin", "anticoagulant", "เลือดออก", "bleeding"]):
        warnings.append("Interaction risk with anticoagulants.")
    if any(k in lower for k in ["hypotension", "ความดันต่ำ"]):
        warnings.append("May lower blood pressure; monitor hypotension.")

    # De-duplicate and return
    dedup: List[str] = []
    for w in warnings:
        if w not in dedup:
            dedup.append(w)
    return dedup
