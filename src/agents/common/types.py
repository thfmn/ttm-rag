"""
Common typed models for agents and pipeline extensions.

These Pydantic models are used across ingestion and query-time agents.
They are intentionally dependency-light to keep unit tests fast.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Literal
from pydantic import BaseModel, Field


class PDPAFindings(BaseModel):
    pii_found: bool = Field(default=False)
    redactions: List[Tuple[int, int, str]] = Field(
        default_factory=list, description="(start, end, label)"
    )
    notes: Optional[str] = None


class RedactionResult(BaseModel):
    cleaned_text: str
    findings: PDPAFindings = Field(default_factory=PDPAFindings)
    audit_id: str = Field(default_factory=lambda: "audit-unknown")


class TaxonomyLabel(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class QualityScore(BaseModel):
    completeness: float = Field(ge=0.0, le=1.0)
    coherence: float = Field(ge=0.0, le=1.0)
    citation_presence: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)


class AcceptanceDecision(BaseModel):
    accepted: bool
    reasons: List[str] = Field(default_factory=list)
    votes: Dict[str, float] = Field(default_factory=dict)


class IngestionDoc(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SafeChunk(BaseModel):
    document_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnswerChunk(BaseModel):
    content: str
    score: float
    document_id: str
    chunk_index: int


class QueryPlan(BaseModel):
    persona: Literal["clinician", "pharmacist", "wellness", "tourist"]
    language: Literal["th", "en", "mixed"]
    domain_route: Literal["interactions", "dosage", "contraindications", "preparation", "general"]
    retrieval_mix: Dict[str, float] = Field(default_factory=dict)
    top_k: int = 5


class PlannedAnswer(BaseModel):
    answer: str
    citations: List[str] = Field(default_factory=list)
    grounded: bool = False
    disclaimers: List[str] = Field(default_factory=list)
    safety_score: float = 0.0
