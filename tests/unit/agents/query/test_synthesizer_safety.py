"""
Unit tests for synthesizer and safety adjudicator stubs.
"""

from __future__ import annotations

from src.agents.common.types import AnswerChunk, PlannedAnswer
from src.agents.query import synthesizer_agent, safety_adjudicator


def test_synthesizer_produces_grounded_answer_with_citations():
    chunks = [
        AnswerChunk(content="Content A", score=0.95, document_id="doc-1", chunk_index=0),
        AnswerChunk(content="Content B", score=0.90, document_id="doc-2", chunk_index=1),
    ]
    planned = synthesizer_agent.synthesize("What herbs?", chunks)
    assert isinstance(planned, PlannedAnswer)
    assert planned.answer
    # Should include at least part of a chunk
    assert "Content" in planned.answer
    # Citations should include unique document_ids
    assert "doc-1" in planned.citations and "doc-2" in planned.citations
    assert planned.grounded is True
    assert 0.0 <= planned.safety_score <= 1.0
    assert any("medical" in d.lower() for d in planned.disclaimers)


def test_adjudicator_lowers_safety_for_ungrounded_answers_and_adds_disclaimer():
    ungrounded = PlannedAnswer(
        answer="Some answer",
        citations=[],
        grounded=False,
        disclaimers=[],
        safety_score=0.8,
    )
    adjudicated = safety_adjudicator.adjudicate(ungrounded)
    assert adjudicated.safety_score <= 0.5
    assert any("not grounded" in d.lower() for d in adjudicated.disclaimers)


def test_adjudicator_adds_risk_disclaimer_when_pregnancy_or_anticoagulant_mentioned():
    risky = PlannedAnswer(
        answer="This mentions pregnancy and warfarin interaction.",
        citations=["doc-1"],
        grounded=True,
        disclaimers=[],
        safety_score=0.7,
    )
    adjudicated = safety_adjudicator.adjudicate(risky)
    assert any("clinical" in d.lower() for d in adjudicated.disclaimers)
