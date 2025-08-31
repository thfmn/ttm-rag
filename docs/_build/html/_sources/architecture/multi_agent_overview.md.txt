# Multi-Agent Ingestion & Curation Overview (Phase 2)

This document outlines the Phase 2 architecture for agentic continuous ingestion and curation, built to be dependency-light by default and optionally orchestrated via Dagster.

Goals:
- Ensure PDPA-safe preprocessing before chunking and storage.
- Add taxonomy labeling, quality scoring, safety checks, and a simple committee for acceptance.
- Support both script-driven ingestion and Dagster asset-based orchestration.
- Keep production posture (Postgres/pgvector primary) and preserve existing APIs.

## Components

1) Lightweight Agent Stubs (no external LLM deps)
- PDPA redaction: src/agents/ingestion/pdpa_agent.py
  - redact(text) -> RedactionResult (cleaned_text + PDPAFindings)
- Taxonomy labeling: src/agents/ingestion/taxonomy_agent.py
  - classify(content, metadata, top_n=2) -> list[TaxonomyLabel]
- Quality scoring: src/agents/ingestion/quality_agent.py
  - score(content, metadata) -> QualityScore
- Safety check: src/agents/ingestion/safety_agent.py
  - check_contraindications(content, metadata) -> list[str] warnings
- Committee decision: src/agents/ingestion/committee_agent.py
  - decide({...}) -> AcceptanceDecision

These are simple heuristics designed to be replaced by Pydantic-AI agents later without changing call sites.

2) Pipeline Preprocessor Wrappers
- src/rag/pipeline_ext.py provides:
  - apply_preprocessors(doc, preprocessors)
  - wrappers: preprocessor_from_pdpa_redactor(), preprocessor_from_taxonomy_classifier(), preprocessor_from_quality_scorer(), preprocessor_from_safety_checker()
- RAGPipeline now accepts preprocessors in RAGConfig and applies them before chunking.

3) Ingestion Script Compatibility
- scripts/ingestion/ingest_documents.py supports DAGSTER_MODE=1 to emit JSON Lines to stdout (instead of posting to API).
- This enables streaming into Dagster assets or other offline processing without changing the script's structure.

4) Dagster Orchestration (Optional)
- Assets: src/orchestration/assets/ingestion_assets.py
  - raw_docs -> redacted_docs -> labeled_docs -> scored_docs -> safe_docs -> accepted_corpus
  - Import-guarded; requires manual install of Dagster.
- Definitions: src/orchestration/dagster_defs.py (exposes defs)
- Resources scaffold: src/orchestration/resources.py (DB engine, object store placeholder, KMS, policy)
- Makefile target: make dagster-dev

## Data Flow

Input (raw JSON) -> PDPA Redaction -> Taxonomy Labels -> Quality Scores -> Safety Warnings -> Committee Decision -> Accepted Corpus

Accepted corpus can be used for downstream indexing, evaluation, or export.

## PDPA and Safety

- Redaction runs first to minimize data risk.
- Audit trails are recorded in metadata.audit for PDPA, taxonomy, quality, and safety stages.
- Committee can enforce a minimum overall quality threshold and penalize safety warnings.

## Next Upgrades

- Replace stubs with Pydantic-AI agents using tool/validator patterns and structured outputs.
- Integrate model gateway policies for specialized models (Thai NER, clinical safety) behind feature flags.
- Add evaluation harness and nightly KPIs (Phase 4).
- Expand PV (pharmacovigilance) agents and secure alerting pathways (Phase 5).
