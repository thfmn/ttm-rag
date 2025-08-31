"""
Ingestion agents package.

This namespace provides lightweight, dependency-free stubs for:
- PDPA redaction
- Taxonomy labeling
- Quality scoring
- Safety checks
- Committee acceptance decision

These stubs return typed results using src/agents/common/types and can be
wired into the RAG pipeline preprocessors immediately. They are designed
to be upgraded later to Pydantic-AI agents without changing call sites.
"""

from . import pdpa_agent
from . import taxonomy_agent
from . import quality_agent
from . import safety_agent
from . import committee_agent

__all__ = [
    "pdpa_agent",
    "taxonomy_agent",
    "quality_agent",
    "safety_agent",
    "committee_agent",
]
