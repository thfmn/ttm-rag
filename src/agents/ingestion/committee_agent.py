"""
Committee decision agent (lightweight stub).

Aggregates simple signals (quality score, safety warnings, taxonomy labels)
and produces an AcceptanceDecision with reasons and votes. This heuristic
stub can be replaced by a Pydantic-AI committee later without changing
call sites.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.agents.common.types import AcceptanceDecision, QualityScore, TaxonomyLabel


def _vote_quality(q: QualityScore | Dict[str, Any] | None) -> float:
    if q is None:
        return 0.0
    if isinstance(q, dict):
        overall = float(q.get("overall", 0.0))
    else:
        overall = float(q.overall)
    # Map overall [0,1] -> vote [-1, +1]
    return 2.0 * overall - 1.0


def _vote_safety(safety_warnings: List[str] | None) -> float:
    """
    Penalize documents with many safety warnings.
    """
    if not safety_warnings:
        return 0.5  # mild positive vote if no warnings
    n = len(safety_warnings)
    return max(-1.0, 0.5 - 0.3 * n)


def _vote_taxonomy(labels: List[TaxonomyLabel] | List[Dict[str, Any]] | None) -> float:
    """
    Encourage domain-labeled docs (weak prior). If provided as dicts, accept those too.
    """
    if not labels:
        return 0.0

    def _get_conf(item: Any) -> float:
        try:
            # TaxonomyLabel path
            return float(getattr(item, "confidence"))
        except Exception:
            try:
                # dict path
                return float(item.get("confidence", 0.0)) if isinstance(item, dict) else 0.0
            except Exception:
                return 0.0

    top_conf = max((_get_conf(it) for it in labels), default=0.0)
    return min(0.5, max(0.0, top_conf))  # cap at +0.5


def decide(inputs: Dict[str, Any]) -> AcceptanceDecision:
    """
    Make an acceptance decision based on inputs:
      - quality: QualityScore or dict-like
      - safety_warnings: List[str]
      - taxonomy: List[TaxonomyLabel] or list of dicts
      - min_overall: float threshold (default 0.5)

    Returns:
      AcceptanceDecision with accepted flag, reasons, votes
    """
    quality = inputs.get("quality")
    safety_warnings = inputs.get("safety_warnings") or []
    taxonomy = inputs.get("taxonomy") or []
    min_overall = float(inputs.get("min_overall", 0.5))

    v_quality = _vote_quality(quality)
    v_safety = _vote_safety(safety_warnings)
    v_tax = _vote_taxonomy(taxonomy)

    votes = {
        "quality": v_quality,
        "safety": v_safety,
        "taxonomy": v_tax,
    }
    total = v_quality + v_safety + v_tax

    reasons: List[str] = []
    # Thresholding logic
    overall_val = 0.0
    try:
        overall_val = float(quality.get("overall", 0.0)) if isinstance(quality, dict) else float(quality.overall)  # type: ignore[attr-defined]
    except Exception:
        overall_val = 0.0

    if overall_val < min_overall:
        reasons.append(f"Overall quality {overall_val:.2f} below threshold {min_overall:.2f}")
    if safety_warnings:
        reasons.append(f"{len(safety_warnings)} safety warning(s) present")

    accepted = (overall_val >= min_overall) and (v_safety > -0.2)

    if accepted and not reasons:
        reasons.append("Meets quality threshold and no blocking safety risks")

    return AcceptanceDecision(accepted=accepted, reasons=reasons, votes=votes)
