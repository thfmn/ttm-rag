"""
Pydantic schemas for MCP tools and resources I/O.

These models mirror the public contracts documented in docs/reference/mcp_contracts.md
and should evolve additively. They also align with gRPC/GraphQL read surfaces.

Install note (documented only):
  uv pip install pydantic orjson
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ======================
# Resource Schemas
# ======================

class NamePair(BaseModel):
    th: str = ""
    en: str = ""


class Constituent(BaseModel):
    id: str
    name: str


class Indication(BaseModel):
    icdCode: str
    description: str


class HerbResource(BaseModel):
    id: str
    names: NamePair = Field(default_factory=NamePair)
    parts: List[str] = Field(default_factory=list)
    constituents: List[Constituent] = Field(default_factory=list)
    indications: List[Indication] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)


class PaperResource(BaseModel):
    pmid: str
    title: str
    abstract: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    journal: Optional[str] = None
    year: Optional[int] = None
    links: List[str] = Field(default_factory=list)


# ======================
# Tool Schemas
# ======================

# tool.query_kg
class StartNode(BaseModel):
    type: Literal["herb", "constituent", "indication"]
    id: str


class KGNode(BaseModel):
    id: str
    type: str
    label: str


class QueryKGInput(BaseModel):
    start: StartNode
    pattern: Optional[str] = None
    filters: Optional[dict] = None
    max_depth: int = 3


class QueryKGOutput(BaseModel):
    paths: List[List[KGNode]] = Field(default_factory=list)
    audit: dict


# tool.hybrid_search
class SearchInput(BaseModel):
    query: str
    lang: Literal["th", "en", "auto"] = "th"
    filters: Optional[dict] = None
    top_k: int = 10


class Hit(BaseModel):
    id: str
    type: str
    title: str
    snippet: str
    score: float
    source: str


class SearchOutput(BaseModel):
    hits: List[Hit] = Field(default_factory=list)
    audit: dict


# tool.rag_answer
class RetrievalParams(BaseModel):
    top_k: int = 5


class RagAnswerInput(BaseModel):
    question: str
    lang: Literal["th", "en", "auto"] = "th"
    retrieval: Optional[RetrievalParams] = None


class Citation(BaseModel):
    id: str
    uri: str
    title: str
    span: Optional[str] = None


class Scores(BaseModel):
    retrieval: Optional[float] = None
    answer_conf: Optional[float] = None


class RagAnswerOutput(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    scores: Scores = Field(default_factory=Scores)
    audit: dict


# tool.find_contraindications
class ContraindicationsInput(BaseModel):
    herb_ids: Optional[List[str]] = None
    formulation_ids: Optional[List[str]] = None


class ContraResult(BaseModel):
    entity_id: str
    type: Literal["herb", "formulation"]
    contraindication: str
    evidence: str
    strength: Literal["low", "moderate", "high"]


class ContraindicationsOutput(BaseModel):
    results: List[ContraResult] = Field(default_factory=list)
    audit: dict


# tool.ingest.run
class IngestItem(BaseModel):
    uri: str
    lang: Literal["th", "en", "auto"] = "auto"
    doc_type: str


class IngestInput(BaseModel):
    dry_run: bool = True
    batch: List[IngestItem]
    ocr: Optional[dict] = None
    ner: Optional[dict] = None


class IngestOutput(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "error"]
    log_uri: Optional[str] = None
    audit: dict


# tool.eval.run
class EvalInput(BaseModel):
    set: Literal["smoke", "curated", "custom"]
    metrics: List[Literal["R@k", "MRR", "factuality"]]
    params: Optional[dict] = None


class Metric(BaseModel):
    name: str
    value: float


class EvalOutput(BaseModel):
    metrics: List[Metric] = Field(default_factory=list)
    report_uri: Optional[str] = None
    audit: dict
