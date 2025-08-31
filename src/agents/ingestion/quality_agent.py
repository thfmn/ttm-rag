"""
Quality scoring agent (lightweight stub).

Computes simple heuristic quality scores for a document:
- completeness: based on length
- coherence: penalizes too many short fragments and excessive punctuation
- citation_presence: detects simple citation markers
- overall: average of components with mild weighting
"""

from __future__ import annotations

from typing import Any, Dict, List
import re

from src.agents.common.types import QualityScore


CITATION_PATTERNS = [
    re.compile(r"\[\d+(?:,\s*\d+)*\]"),  # [1], [1, 2]
    re.compile(r"\(doi:\s*10\.\d{4,9}/[-._;()/:A-Z0-9]+\)", re.IGNORECASE),
    re.compile(r"PMID:\s*\d+", re.IGNORECASE),
    re.compile(r"ref\.", re.IGNORECASE),
]


def _completeness(text: str) -> float:
    n = len(text.strip())
    # 0.0 under 200 chars, 1.0 above 1200 chars (clip to [0,1])
    return max(0.0, min(1.0, (n - 200) / 1000.0))


def _coherence(text: str) -> float:
    # Penalize excessive punctuation bursts and too many tiny fragments
    fragments = [f for f in re.split(r"[.!?]", text) if f.strip()]
    short_count = sum(1 for f in fragments if len(f.strip()) < 30)
    punct_bursts = len(re.findall(r"[,\-;:]{2,}", text))
    base = 1.0
    penalty = min(0.6, 0.02 * short_count + 0.05 * punct_bursts)
    return max(0.0, base - penalty)


def _citation_presence(text: str) -> float:
    hits = 0
    for pat in CITATION_PATTERNS:
        if pat.search(text):
            hits += 1
    return min(1.0, hits / 2.0)


def score(content: str, metadata: Dict[str, Any] | None = None) -> QualityScore:
    c1 = _completeness(content)
    c2 = _coherence(content)
    c3 = _citation_presence(content)
    # Mild weighting: coherence slightly more important
    overall = max(0.0, min(1.0, (c1 + 1.2 * c2 + c3) / 3.2))
    reasons: List[str] = []
    if c1 < 0.3:
        reasons.append("Short content; completeness low")
    if c2 < 0.6:
        reasons.append("Coherence impacted by fragments/punctuation")
    if c3 < 0.3:
        reasons.append("No clear citations detected")
    return QualityScore(
        completeness=float(c1),
        coherence=float(c2),
        citation_presence=float(c3),
        overall=float(overall),
        reasons=reasons,
    )
