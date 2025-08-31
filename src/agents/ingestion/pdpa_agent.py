"""
PDPA redaction agent (lightweight stub).

Provides a dependency-free redact() function that detects simple PII
patterns (emails, phone numbers, long digit IDs) and returns a typed
RedactionResult with cleaned text and audit findings.

This stub can be upgraded to a Pydantic-AI agent later without changing
call sites.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Tuple

from src.agents.common.types import RedactionResult, PDPAFindings


# Simple PII patterns (extend as needed)
EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b")
LONG_DIGITS_RE = re.compile(r"\b\d{10,}\b")  # crude long number detector (IDs, etc.)


def _collect_spans(text: str) -> List[Tuple[int, int, str]]:
    spans: List[Tuple[int, int, str]] = []
    for m in EMAIL_RE.finditer(text):
        spans.append((m.start(), m.end(), "EMAIL"))
    for m in PHONE_RE.finditer(text):
        spans.append((m.start(), m.end(), "PHONE"))
    for m in LONG_DIGITS_RE.finditer(text):
        spans.append((m.start(), m.end(), "ID"))
    # Sort and merge overlaps (keep label of first span encountered)
    spans.sort(key=lambda x: (x[0], x[1]))
    merged: List[Tuple[int, int, str]] = []
    for s, e, lab in spans:
        if not merged:
            merged.append((s, e, lab))
            continue
        ps, pe, plab = merged[-1]
        if s <= pe:  # overlap
            merged[-1] = (ps, max(pe, e), plab)
        else:
            merged.append((s, e, lab))
    return merged


def _apply_redactions(text: str, spans: List[Tuple[int, int, str]]) -> str:
    if not spans:
        return text
    out: List[str] = []
    cursor = 0
    for s, e, lab in spans:
        if cursor < s:
            out.append(text[cursor:s])
        # Insert a standard token; keep it short to avoid ballooning the text
        out.append("[REDACTED]")
        cursor = e
    if cursor < len(text):
        out.append(text[cursor:])
    return "".join(out)


def redact(text: str, metadata: Dict[str, Any] | None = None) -> RedactionResult:
    """
    Redact PII from text and return a RedactionResult with audit details.

    Args:
        text: Input text
        metadata: Optional metadata (unused in this stub)

    Returns:
        RedactionResult with cleaned_text and PDPAFindings
    """
    spans = _collect_spans(text)
    cleaned = _apply_redactions(text, spans)
    findings = PDPAFindings(
        pii_found=bool(spans),
        redactions=[(s, e, lab) for s, e, lab in spans],
        notes=None,
    )
    return RedactionResult(cleaned_text=cleaned, findings=findings, audit_id=str(uuid.uuid4()))
