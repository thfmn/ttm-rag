"""
Unit tests for ingestion agent stubs:
- pdpa_agent.redact
- taxonomy_agent.classify
- quality_agent.score
- safety_agent.check_contraindications
- committee_agent.decide
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.agents.common.types import (
    RedactionResult,
    TaxonomyLabel,
    QualityScore,
    AcceptanceDecision,
)
from src.agents.ingestion import pdpa_agent, taxonomy_agent, quality_agent, safety_agent
from src.agents.ingestion.committee_agent import decide


def test_pdpa_agent_redact_detects_emails_and_numbers():
    content = "Contact me at doctor@example.com or call +66 89-123-4567. ID: 12345678901"
    res = pdpa_agent.redact(content)
    assert isinstance(res, RedactionResult)
    assert res.cleaned_text != content
    # Should contain [REDACTED] at least once
    assert "[REDACTED]" in res.cleaned_text
    # Findings should indicate pii_found
    assert res.findings.pii_found is True
    assert isinstance(res.findings.redactions, list)


def test_taxonomy_agent_classify_returns_labels():
    content = "Recommended dosage is 500 mg per day. Avoid during pregnancy."
    labels = taxonomy_agent.classify(content, metadata={})
    assert isinstance(labels, list)
    assert len(labels) >= 1
    assert all(isinstance(lab, TaxonomyLabel) for lab in labels)
    # Top label should be one of the known domains
    assert labels[0].label in {"dosage", "contraindications", "interactions", "preparation", "general"}


def test_quality_agent_score_with_reasonable_ranges():
    content_short = "Short text."
    qs_short = quality_agent.score(content_short, {})
    assert isinstance(qs_short, QualityScore)
    for v in [qs_short.completeness, qs_short.coherence, qs_short.citation_presence, qs_short.overall]:
        assert 0.0 <= v <= 1.0

    content_long = (
        "This is a detailed abstract with multiple sentences. It presents references [1]. "
        "Another part includes DOI: (doi:10.1000/xyz123). It is coherent and descriptive."
    )
    qs_long = quality_agent.score(content_long, {})
    assert isinstance(qs_long, QualityScore)
    assert qs_long.overall >= qs_short.overall


def test_safety_agent_warnings_detected():
    content = "This herb should be avoided in pregnancy and when using warfarin due to bleeding risk."
    warns = safety_agent.check_contraindications(content, {})
    assert isinstance(warns, list)
    assert any("pregnan" in w.lower() or "ตั้งครรภ์" in w for w in warns)
    assert any("anticoagulant" in w.lower() or "warfarin" in w.lower() for w in warns) or any("interaction" in w.lower() for w in warns)


def test_committee_decide_accepts_high_quality_no_warnings():
    content = "A sufficiently long coherent text with citations [1]. (doi:10.1000/abc123)."
    quality = quality_agent.score(content, {})
    taxonomy = [TaxonomyLabel(label="general", confidence=0.2)]
    decision = decide({"quality": quality, "safety_warnings": [], "taxonomy": taxonomy, "min_overall": 0.4})
    assert isinstance(decision, AcceptanceDecision)
    assert decision.accepted is True
    assert "quality" in decision.votes
    assert "safety" in decision.votes
    assert "taxonomy" in decision.votes

def test_committee_decide_rejects_low_quality_or_many_warnings():
    quality = QualityScore(completeness=0.1, coherence=0.2, citation_presence=0.0, overall=0.15, reasons=["short"])
    warns = ["risk1", "risk2", "risk3"]
    decision = decide({"quality": quality, "safety_warnings": warns, "taxonomy": [], "min_overall": 0.5})
    assert isinstance(decision, AcceptanceDecision)
    assert decision.accepted is False
    assert any("warning" in r.lower() for r in decision.reasons)
