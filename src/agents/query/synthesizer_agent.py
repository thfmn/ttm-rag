"""
Synthesizer agent (lightweight stub).

Produces a PlannedAnswer from a query and a list of AnswerChunk.
"""

from __future__ import annotations

from typing import List, Set

from src.agents.common.types import AnswerChunk, PlannedAnswer


def synthesize(query: str, chunks: List[AnswerChunk]) -> PlannedAnswer:
    """
    Create a simple answer by stitching together the top chunks and
    extracting citations from their document_ids.

    Heuristic behavior:
    - Use up to 2 top chunks to form the answer body.
    - Collect citations from unique document_ids.
    - grounded=True if at least one citation exists.
    - safety_score baseline set to 0.7 if chunks present, else 0.3.
    - Add a general disclaimer about medical advice.
    """
    if not chunks:
        return PlannedAnswer(
            answer="No relevant context found to answer the query.",
            citations=[],
            grounded=False,
            disclaimers=["This information is for educational purposes and not medical advice."],
            safety_score=0.3,
        )

    # Combine top 2 chunk contents
    top_contents = [c.content.strip() for c in chunks[:2] if c.content]
    answer = "\n\n".join(top_contents) if top_contents else "Context unavailable."

    # Citations based on unique document_id
    seen: Set[str] = set()
    citations: List[str] = []
    for c in chunks:
        if c.document_id and c.document_id not in seen:
            citations.append(str(c.document_id))
            seen.add(c.document_id)

    grounded = len(citations) > 0
    safety_score = 0.7 if grounded else 0.5

    disclaimers = ["This information is for educational purposes and not medical advice."]

    return PlannedAnswer(
        answer=answer,
        citations=citations,
        grounded=grounded,
        disclaimers=disclaimers,
        safety_score=float(safety_score),
    )
