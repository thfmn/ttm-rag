"""
Pipeline extensions: preprocessors plumbing for PDPA/quality/taxonomy hooks.

This module introduces a minimal, typed interface for document preprocessors and
a helper to apply a chain of preprocessors before chunking. It is intentionally
lightweight and does not depend on agent implementations so it can be used in
Phase 1 without adding new external dependencies.

Phase 2 adds convenience wrappers that adapt lightweight agent stubs into
preprocessors compatible with this module.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, Callable
from pydantic import BaseModel


class PreprocessorResult(BaseModel):
    """
    Result of applying a preprocessor to a document.
    - content: transformed/cleaned text
    - metadata: additional/updated metadata
    - audit: structured audit information about the transformation
    """
    content: str
    metadata: Dict[str, Any] = {}
    audit: Dict[str, Any] = {}


class DocPreprocessor(Protocol):
    """
    Protocol for preprocessors. Accepts a document dict with keys:
      - id: str
      - content: str
      - metadata: dict[str, Any]
    Returns a PreprocessorResult (or a dict coercible to it).
    """
    def __call__(self, doc: Dict[str, Any]) -> PreprocessorResult: ...


def _to_result(value: Any) -> PreprocessorResult:
    """
    Coerce arbitrary values into a PreprocessorResult for ergonomics.
    Supports:
      - PreprocessorResult
      - dict with keys content/metadata/audit
      - tuple (content, metadata) where audit is empty
      - str (content only)
    """
    if isinstance(value, PreprocessorResult):
        return value
    if isinstance(value, dict) and "content" in value:
        return PreprocessorResult(
            content=str(value.get("content", "")),
            metadata=dict(value.get("metadata", {}) or {}),
            audit=dict(value.get("audit", {}) or {}),
        )
    if isinstance(value, tuple) and len(value) == 2:
        content, metadata = value
        return PreprocessorResult(content=str(content), metadata=dict(metadata or {}), audit={})
    if isinstance(value, str):
        return PreprocessorResult(content=value, metadata={}, audit={})
    # Fallback to empty result
    return PreprocessorResult(content="", metadata={}, audit={"error": "invalid_preprocessor_output"})


def apply_preprocessors(
    doc: Dict[str, Any],
    preprocessors: Optional[List[Callable[[Dict[str, Any]], Any]]] = None
) -> PreprocessorResult:
    """
    Apply a list of preprocessors to a document.

    Args:
        doc: A dict with keys {"id": str, "content": str, "metadata": dict}
        preprocessors: List of callables returning PreprocessorResult-compatible outputs

    Returns:
        PreprocessorResult with final content/metadata and a merged audit tree.
    """
    content = str(doc.get("content", ""))
    metadata = dict(doc.get("metadata", {}) or {})
    merged_audit: Dict[str, Any] = {}

    if not preprocessors:
        return PreprocessorResult(content=content, metadata=metadata, audit=merged_audit)

    for idx, pre in enumerate(preprocessors):
        name = getattr(pre, "__name__", pre.__class__.__name__)
        try:
            result = _to_result(pre({"id": doc.get("id", ""), "content": content, "metadata": metadata}))
        except Exception as e:
            # Record failure in audit and continue
            merged_audit[f"{idx}:{name}"] = {"status": "error", "error": str(e)}
            continue

        # Update rolling state
        content = result.content if result.content is not None else content
        if result.metadata:
            # Shallow-merge metadata (later wins). Deep merge can be added if needed.
            metadata.update(result.metadata)

        # Merge audit under namespaced key
        merged_audit[f"{idx}:{name}"] = {"status": "ok", "details": result.audit or {}}

    return PreprocessorResult(content=content, metadata=metadata, audit=merged_audit)


# Convenience wrappers to adapt lightweight agent stubs into preprocessors.
# Each factory returns a callable(doc_dict) -> PreprocessorResult suitable for RAGConfig.preprocessors.

def preprocessor_from_pdpa_redactor():
    """
    Wrap src.agents.ingestion.pdpa_agent.redact into a pipeline preprocessor.
    Replaces content with cleaned_text and records audit findings under metadata.audit.pdpa.
    """
    from src.agents.ingestion import pdpa_agent  # lightweight stub

    def _pre(doc: Dict[str, Any]) -> PreprocessorResult:
        content = str(doc.get("content", ""))
        res = pdpa_agent.redact(content, doc.get("metadata"))
        md = dict(doc.get("metadata", {}) or {})
        audit = {"pdpa": res.findings.model_dump()}
        return PreprocessorResult(content=res.cleaned_text, metadata=md, audit=audit)

    return _pre


def preprocessor_from_taxonomy_classifier(top_n: int = 2):
    """
    Wrap src.agents.ingestion.taxonomy_agent.classify into a preprocessor.
    Adds metadata.taxonomy (list of {label, confidence}) and audit.taxonomy set to the same.
    """
    from src.agents.ingestion import taxonomy_agent  # lightweight stub

    def _pre(doc: Dict[str, Any]) -> PreprocessorResult:
        content = str(doc.get("content", ""))
        labels = taxonomy_agent.classify(content, doc.get("metadata"), top_n=top_n)
        md = dict(doc.get("metadata", {}) or {})
        md["taxonomy"] = [l.model_dump() for l in labels]
        audit = {"taxonomy": md["taxonomy"]}
        return PreprocessorResult(content=content, metadata=md, audit=audit)

    return _pre


def preprocessor_from_quality_scorer():
    """
    Wrap src.agents.ingestion.quality_agent.score into a preprocessor.
    Adds metadata.quality (QualityScore dict) and audit.quality.reasons list.
    """
    from src.agents.ingestion import quality_agent  # lightweight stub

    def _pre(doc: Dict[str, Any]) -> PreprocessorResult:
        content = str(doc.get("content", ""))
        q = quality_agent.score(content, doc.get("metadata"))
        md = dict(doc.get("metadata", {}) or {})
        md["quality"] = q.model_dump()
        audit = {"quality": {"reasons": list(q.reasons)}}
        return PreprocessorResult(content=content, metadata=md, audit=audit)

    return _pre


def preprocessor_from_safety_checker():
    """
    Wrap src.agents.ingestion.safety_agent.check_contraindications into a preprocessor.
    Adds metadata.safety_warnings (list[str]) and audit.safety.warnings.
    """
    from src.agents.ingestion import safety_agent  # lightweight stub

    def _pre(doc: Dict[str, Any]) -> PreprocessorResult:
        content = str(doc.get("content", ""))
        warns = safety_agent.check_contraindications(content, doc.get("metadata"))
        md = dict(doc.get("metadata", {}) or {})
        md["safety_warnings"] = list(warns)
        audit = {"safety": {"warnings": list(warns)}}
        return PreprocessorResult(content=content, metadata=md, audit=audit)

    return _pre
