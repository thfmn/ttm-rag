"""
Taxonomy labeling agent (lightweight stub).

Classifies content into a small set of domain labels with confidences using
simple keyword heuristics. This is dependency-free and intended to be
upgraded to a Pydantic-AI agent later without changing call sites.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.agents.common.types import TaxonomyLabel


# Domain keyword maps (very light heuristics; expand for Thai/English)
DOMAIN_KEYWORDS = {
    "interactions": [
        "interaction",
        "interact",
        "ยา",
        "ปฏิกิริยา",
        "contraindicated with",
        "avoid with",
    ],
    "dosage": [
        "dose",
        "dosage",
        "mg",
        "ml",
        "ครั้ง",
        "วันละ",
        "รับประทาน",
        "ปริมาณ",
    ],
    "contraindications": [
        "contraindication",
        "avoid",
        "pregnancy",
        "pregnant",
        "เด็ก",
        "โรคตับ",
        "โรคไต",
        "ควรหลีกเลี่ยง",
    ],
    "preparation": [
        "prepare",
        "preparation",
        "decoction",
        "infusion",
        "ต้ม",
        "ชง",
        "บด",
        "ตำรับ",
    ],
    "general": [
        "herbal",
        "traditional",
        "สรรพคุณ",
        "ตำรายา",
        "สมุนไพร",
    ],
}


def _score_for_label(text: str, label: str) -> float:
    """
    Naive scoring: ratio of hits to a small denominator to keep it in [0,1].
    """
    keys = DOMAIN_KEYWORDS.get(label, [])
    if not keys:
        return 0.0
    hits = 0
    lower = text.lower()
    for k in keys:
        if k.lower() in lower:
            hits += 1
    # Smooth denominator to avoid 1.0 for trivial matches
    denom = max(5, len(keys))
    return min(1.0, hits / denom)


def classify(content: str, metadata: Dict[str, Any] | None = None, top_n: int = 2) -> List[TaxonomyLabel]:
    """
    Produce a ranked list of TaxonomyLabel with simple keyword heuristics.

    Args:
        content: input text
        metadata: optional metadata (unused in stub)
        top_n: number of labels to return

    Returns:
        List[TaxonomyLabel] sorted by confidence desc.
    """
    scores = []
    for label in DOMAIN_KEYWORDS.keys():
        s = _score_for_label(content, label)
        if s > 0.0 or label == "general":
            scores.append(TaxonomyLabel(label=label, confidence=float(s)))
    scores.sort(key=lambda x: x.confidence, reverse=True)
    return scores[: max(1, top_n)]
