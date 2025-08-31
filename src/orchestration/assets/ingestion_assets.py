"""
Dagster assets for agentic continuous ingestion & curation (Phase 2).

Import guarded to avoid hard dependency when Dagster is not installed.
Assets implement a simple linear flow:
  raw_docs -> redacted_docs -> labeled_docs -> scored_docs -> safe_docs -> accepted_corpus

To run locally (manual per .clinerules):
  1) Install Dagster:
     uv pip install "dagster>=1.7" "dagster-webserver>=1.7"
  2) Start dev webserver:
     uv run dagster dev -m src.orchestration.dagster_defs
  3) Materialize assets from UI or CLI.

Environment variables:
  - INGEST_INPUT_JSON: path to input JSON (array of docs like pubmed fixtures)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import json
from pathlib import Path

# Import agent stubs (dependency-light)
from src.agents.ingestion import pdpa_agent, taxonomy_agent, quality_agent, safety_agent
from src.agents.ingestion.committee_agent import decide


def _load_docs_from_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input JSON not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of documents")
    # Normalize minimal shape
    out: List[Dict[str, Any]] = []
    for i, d in enumerate(data):
        out.append(
            {
                "id": d.get("pmid", d.get("id", f"doc_{i}")),
                "content": d.get("abstract", "") or d.get("content", "") or d.get("title", ""),
                "metadata": {
                    "source": d.get("source", "pubmed"),
                    "title": d.get("title"),
                    "journal": d.get("journal"),
                    "publication_year": (d.get("publication_date") or {}).get("year") if isinstance(d.get("publication_date"), dict) else d.get("year"),
                    "authors": [a.get("name") for a in (d.get("authors") or []) if isinstance(a, dict) and a.get("name")],
                },
            }
        )
    # Filter empty content
    return [x for x in out if x["content"]]


def _ensure_dagster():
    try:
        import dagster as _dag  # noqa: F401
    except Exception as e:
        raise ImportError(
            "Dagster is required to use orchestration assets.\n"
            "Install with:\n"
            "  uv pip install \"dagster>=1.7\" \"dagster-webserver>=1.7\""
        ) from e


def get_assets():
    """
    Return list of dagster asset definitions. Import dagster lazily to avoid hard dependency.
    """
    _ensure_dagster()
    from dagster import asset

    @asset(
        name="raw_docs",
        description="Load raw documents from JSON file specified by INGEST_INPUT_JSON or default fixture.",
    )
    def raw_docs() -> List[Dict[str, Any]]:
        input_path = Path(os.getenv("INGEST_INPUT_JSON", "data/raw/pubmed_ttm_100_articles.json"))
        return _load_docs_from_json(input_path)

    @asset(
        name="redacted_docs",
        description="Apply PDPA redaction to content and append findings to metadata.audit",
    )
    def redacted_docs(raw_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for d in raw_docs:
            r = pdpa_agent.redact(d["content"], d.get("metadata"))
            md = dict(d.get("metadata") or {})
            md["audit"] = {"pdpa": r.findings.model_dump()}
            out.append({"id": d["id"], "content": r.cleaned_text, "metadata": md})
        return out

    @asset(
        name="labeled_docs",
        description="Classify redacted documents into taxonomy labels and store in metadata.taxonomy",
    )
    def labeled_docs(redacted_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for d in redacted_docs:
            labels = taxonomy_agent.classify(d["content"], d.get("metadata"), top_n=2)
            md = dict(d.get("metadata") or {})
            md["taxonomy"] = [lbl.model_dump() for lbl in labels]
            out.append({"id": d["id"], "content": d["content"], "metadata": md})
        return out

    @asset(
        name="scored_docs",
        description="Compute heuristic quality scores and store in metadata.quality",
    )
    def scored_docs(labeled_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for d in labeled_docs:
            q = quality_agent.score(d["content"], d.get("metadata"))
            md = dict(d.get("metadata") or {})
            md["quality"] = q.model_dump()
            out.append({"id": d["id"], "content": d["content"], "metadata": md})
        return out

    @asset(
        name="safe_docs",
        description="Run simple safety checks and store warnings in metadata.safety_warnings",
    )
    def safe_docs(scored_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for d in scored_docs:
            warns = safety_agent.check_contraindications(d["content"], d.get("metadata"))
            md = dict(d.get("metadata") or {})
            md["safety_warnings"] = warns
            out.append({"id": d["id"], "content": d["content"], "metadata": md})
        return out

    @asset(
        name="accepted_corpus",
        description="Committee decision to accept/reject; returns list of accepted docs (id/content/metadata).",
    )
    def accepted_corpus(safe_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        accepted: List[Dict[str, Any]] = []
        for d in safe_docs:
            decision = decide(
                {
                    "quality": (d.get("metadata") or {}).get("quality"),
                    "safety_warnings": (d.get("metadata") or {}).get("safety_warnings"),
                    "taxonomy": (d.get("metadata") or {}).get("taxonomy"),
                    "min_overall": 0.5,
                }
            )
            md = dict(d.get("metadata") or {})
            md["committee"] = decision.model_dump()
            if decision.accepted:
                accepted.append({"id": d["id"], "content": d["content"], "metadata": md})
        return accepted

    return [raw_docs, redacted_docs, labeled_docs, scored_docs, safe_docs, accepted_corpus]
