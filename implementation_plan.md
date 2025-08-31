# Implementation Plan

[Overview]
Design and introduce a production-ready, multi-agent RAG platform for Thai Traditional Medicine with continuous batch ingestion (Dagster), PDPA-safe preprocessing, agentic query planning/guardrails, and cloud-compatible deployment, while preserving existing APIs and data models.

This plan establishes three high-value multi-agent capabilities aligned with Thai 2025 needs: (1) Agentic Continuous Ingestion & Curation (foundation), (2) Query Planner & Router for Thai/English clinical workflows (differentiation), and (3) Pharmacovigilance Signal Detection (strategic B2B). Each capability is operationalized through Pydantic AI agents and optionally composed with pydantic-graph for deterministic control. We integrate Dagster for scheduled/batch ingestion and backfills, and we maintain cloud posture with Postgres/pgvector, object storage, Kubernetes, and KMS-backed secrets.

The implementation minimally extends existing RAG code (pipeline/chunker/embeddings/vector_store) with explicit hooks for preprocessing (PDPA redaction, quality) and retrieval filtering, adds a model-driven agent layer, and introduces robust evaluation/observability (Safety Adjudicator, usage limits, Logfire/Otel). All changes align with .clinerules and testing practices.

[Types]  
Introduce typed agent I/O and pipeline extension types to enforce PDPA safety, taxonomy, quality scoring, and structured query answers.

- src/agents/common/types.py
  - class PDPAFindings(BaseModel):
    - pii_found: bool
    - redactions: list[tuple[int, int, str]]  # (start, end, label)
    - notes: Optional[str]
  - class RedactionResult(BaseModel):
    - cleaned_text: str
    - findings: PDPAFindings
    - audit_id: str
  - class TaxonomyLabel(BaseModel):
    - label: str
    - confidence: float
  - class QualityScore(BaseModel):
    - completeness: float
    - coherence: float
    - citation_presence: float
    - overall: float
    - reasons: list[str]
  - class AcceptanceDecision(BaseModel):
    - accepted: bool
    - reasons: list[str]
    - votes: dict[str, float]
  - class IngestionDoc(BaseModel):
    - id: str
    - content: str
    - metadata: dict[str, Any] = {}
  - class SafeChunk(BaseModel):
    - document_id: str
    - content: str
    - metadata: dict[str, Any] = {}
  - class AnswerChunk(BaseModel):
    - content: str
    - score: float
    - document_id: str
    - chunk_index: int
  - class QueryPlan(BaseModel):
    - persona: Literal["clinician","pharmacist","wellness","tourist"]
    - language: Literal["th","en","mixed"]
    - domain_route: Literal["interactions","dosage","contraindications","preparation","general"]
    - retrieval_mix: dict[str, float]  # e.g., {"bm25":0.3,"dense":0.7}
    - top_k: int = 5
  - class PlannedAnswer(BaseModel):
    - answer: str
    - citations: list[str]
    - grounded: bool
    - disclaimers: list[str]
    - safety_score: float

- src/rag/pipeline_ext.py
  - class PreprocessorResult(BaseModel):
    - content: str
    - metadata: dict[str, Any]
    - audit: dict[str, Any] = {}

- src/agents/pv/types.py
  - class EventRecord(BaseModel):
    - source_id: str
    - text: str
    - timestamp: datetime
    - metadata: dict[str, Any] = {}
  - class Signal(BaseModel):
    - key: str
    - strength: float
    - evidence: list[str]
    - triage_level: Literal["low","medium","high"]

[Files]
Add agent modules, orchestration, and pipeline extension points; evolve API and vector filters; no deletions in this phase.

- New files
  - src/agents/common/__init__.py
  - src/agents/common/types.py
  - src/agents/ingestion/__init__.py
  - src/agents/ingestion/pdpa_agent.py
  - src/agents/ingestion/taxonomy_agent.py
  - src/agents/ingestion/quality_agent.py
  - src/agents/ingestion/safety_agent.py
  - src/agents/ingestion/committee_agent.py
  - src/agents/query/__init__.py
  - src/agents/query/intent_agent.py
  - src/agents/query/router_agent.py
  - src/agents/query/planner_agent.py
  - src/agents/query/synthesizer_agent.py
  - src/agents/query/safety_adjudicator.py
  - src/agents/pv/__init__.py
  - src/agents/pv/types.py
  - src/agents/pv/ner_agent.py
  - src/agents/pv/dedup_causality_agent.py
  - src/agents/pv/triage_agent.py
  - src/orchestration/__init__.py
  - src/orchestration/dagster_defs.py          # Definitions, schedules, sensors
  - src/orchestration/assets/ingestion_assets.py # Dagster assets mapping to agent pipeline
  - src/orchestration/resources.py              # DB, object store, KMS, model gateway configs
  - src/rag/pipeline_ext.py                     # Preprocessor hooks (PDPA/quality/taxonomy)
  - scripts/evaluation/eval_harness.py          # Quality/cost/safety eval harness (KnowledgeOps)
  - scripts/evaluation/kpis_daily_report.py
  - docs/architecture/multi_agent_overview.md
  - docs/operations/dagster_deploy.md

- Modified files
  - src/api/rag_router.py
    - Add model: Optional[str] to QueryRequest, forward to pipeline.query(model=model)
    - Add GET /models to expose registry.get_model_list()
    - Add optional filter_metadata: dict on /query to support constrained retrieval
  - src/rag/vector_store.py
    - Implement filter_metadata in pgvector SQL and numpy fallback
  - src/rag/pipeline.py
    - Accept optional list of preprocessors (callables) in RAGConfig
    - Apply preprocessors before chunking; include audit info in metadata
    - Ensure query() forwards model param and unify context schema with agents
  - scripts/ingestion/ingest_documents.py
    - Optional: emit batches to Dagster materialization (stdout JSON lines) when env DAGSTER_MODE=1

- Configuration updates
  - docs/deployment.md: add Dagster deployment guidance (local+K8s), secrets via env/KMS
  - Makefile: targets for dagster dev, tests, eval dashboards

[Functions]
Add clean, typed agent tools and pipeline hooks; modify existing functions for filters and adapter routing.

- New functions
  - src/rag/pipeline_ext.py
    - def apply_preprocessors(doc: IngestionDoc, preprocessors: list[Callable]) -> PreprocessorResult
  - src/agents/ingestion/pdpa_agent.py
    - Pydantic-AI agent with tool def redact(ctx, text: str) -> RedactionResult
  - src/agents/ingestion/taxonomy_agent.py
    - classify(content: str, metadata: dict) -> list[TaxonomyLabel]
  - src/agents/ingestion/quality_agent.py
    - score(content: str, metadata: dict) -> QualityScore
  - src/agents/ingestion/safety_agent.py
    - check_contraindications(content: str, metadata: dict) -> list[str]
  - src/agents/ingestion/committee_agent.py
    - decide(inputs: dict) -> AcceptanceDecision
  - src/agents/query/intent_agent.py
    - analyze(query: str, headers: dict) -> tuple[persona, language]
  - src/agents/query/router_agent.py
    - route(persona, query) -> domain_route
  - src/agents/query/planner_agent.py
    - plan(query, persona, route) -> QueryPlan
  - src/agents/query/synthesizer_agent.py
    - synthesize(query, chunks: list[AnswerChunk]) -> PlannedAnswer
  - src/agents/query/safety_adjudicator.py
    - adjudicate(answer: PlannedAnswer) -> PlannedAnswer  # may add disclaimers or request more retrieval
  - src/agents/pv/ner_agent.py
    - extract(record: EventRecord) -> dict  # entities and relations
  - src/agents/pv/dedup_causality_agent.py
    - cluster_and_score(events: list[dict]) -> list[Signal]
  - src/agents/pv/triage_agent.py
    - triage(signals: list[Signal]) -> list[Signal]  # with triage_level set

- Modified functions
  - src/api/rag_router.py
    - class QueryRequest: add model: Optional[str], filter_metadata: Optional[Dict[str, Any]]
    - query_rag(): pass model and filter_metadata to pipeline.query
  - src/rag/vector_store.py
    - similarity_search(): when filter_metadata present, add WHERE JSON filtering in Postgres:
      WHERE (chunk_metadata->>:key) = :value ... (conjunction over provided keys)
      For SQLite fallback, filter in Python before ranking.
  - src/rag/pipeline.py
    - __init__(): accept preprocessors in RAGConfig; store on self
    - process_documents(): call apply_preprocessors() before chunking; merge audit into chunk metadata
    - query(): generate context_chunks compatible with synthesizer; keep adapter model routing

- Removed functions
  - None in this phase (preserve compatibility).

[Classes]
Introduce agent wrappers and preprocessor plumbing; keep core RAG classes intact.

- New classes
  - src/rag/pipeline_ext.py
    - class DocPreprocessor(Protocol): def __call__(self, doc: IngestionDoc) -> PreprocessorResult
  - Agent wrappers (Pydantic-AI based)
    - src/agents/ingestion/*_agent.py: module-level Agent instances with typed tools
    - src/agents/query/*: planner/router/synthesizer agents
    - src/agents/pv/*: pv agents
  - src/orchestration/dagster_defs.py
    - Dagster Definitions, Jobs, Schedules, Sensors
  - src/orchestration/assets/ingestion_assets.py
    - Software-defined assets: raw_docs → redacted_docs → labeled_docs → chunks → accepted_corpus

- Modified classes
  - src/api/rag_router.py: Pydantic models augmented as above
  - src/rag/pipeline.py: RAGConfig extended; RAGPipeline integrates preprocessors

- Removed classes
  - None.

[Dependencies]
Add minimal, rationale-driven packages via uv (manual execution only).

- Core agents and graphs
  - uv pip install "pydantic-ai>=0.0.16"
  - uv pip install "pydantic-graph>=0.4.0"
  Rationale: Typed agents with tool/DI/validator support; optional FSM for complex flows.

- Orchestration
  - uv pip install "dagster>=1.7" "dagster-webserver>=1.7"
  Rationale: Asset-based scheduling/backfills for continuous ingestion.

- Thai language quality (optional but recommended)
  - uv pip install "pythainlp>=5.0"
  Rationale: Better Thai sentence splitting/NER; improves chunking and PV extraction accuracy.

- Observability (optional, enable in staging)
  - uv pip install "pydantic-logfire>=0.5" "opentelemetry-sdk>=1.25.0"
  Rationale: Deep tracing of agent/tool usage and latency.

- Testing
  - uv pip install "pytest>=8" "pytest-asyncio>=0.23"
  - uv pip install "httpx>=0.27"  # for any HTTP tools
  Follow .clinerules: no auto-install, commands provided for manual run.

[Testing]
Adopt TDD on agent modules and pipeline extensions; comprehensive unit/integration tests with ethical API usage.

- Unit tests (tests/unit/)
  - tests/unit/agents/ingestion/test_pdpa_agent.py  # FunctionModel stubs, no network
  - tests/unit/agents/query/test_planner_router.py
  - tests/unit/agents/query/test_safety_adjudicator.py
  - tests/unit/rag/test_vector_store_filters.py     # metadata filter behavior (sqlite and mocked pgvector)
  - tests/unit/rag/test_pipeline_preprocessors.py   # PDPA + quality integration paths
  - tests/unit/models/test_model_registry.py        # already present pattern (extend for /models endpoint)
- Integration tests (tests/integration/)
  - tests/integration/test_dagster_assets.py  # mark as integration; 1s min between external calls; max 3 results/query
  - tests/integration/test_query_end_to_end.py # with small fixture corpus; evaluate citations/groundedness
  - tests/integration/test_openwebui_model_selection.py (existing) remains
- Markers and rate limits
  - Use pytest markers @pytest.mark.integration
  - Sleep(1) between any external API calls; cap result counts at 3
- Coverage
  - Target >80% for new code; critical paths 100% (preprocessors, router, safety adjudication)
- Commands (manual)
  - make test
  - make test-integration
  - make test-cov

[Implementation Order]
Execute in phases to minimize risk, unlock ROI quickly, and keep API stable.

1. Extend core RAG for safety hooks and retrieval filters
   - Add preprocessors support in RAGConfig / RAGPipeline
   - Implement filter_metadata in vector_store (Postgres+fallback)
   - Update rag_router to accept model and filters; add /models endpoint
2. Implement Agentic Continuous Ingestion & Curation (Dagster)
   - Implement ingestion agents (pdpa/taxonomy/quality/safety/committee) with Pydantic-AI
   - Add Dagster assets: raw_docs → redacted → labeled → chunks → accepted_corpus
   - Wire to existing pipelines/connectors; keep REST ingestion script working
3. Implement Query Planner & Router agents
   - Intent/language, router, planner, synthesizer, safety adjudicator
   - Integrate planner into query flow (optionally behind feature flag)
4. KnowledgeOps evaluation + cost-aware routing (initial)
   - scripts/evaluation, nightly KPIs, simple model gateway policy (use registry)
5. Pharmacovigilance pilot
   - Event aggregator (public/regulatory first), NER/RE, dedup/causality, triage
   - Secure outputs and alerting pathways; mark as enterprise preview
6. Documentation and deployment
   - Update docs (architecture/multi_agent_overview.md, operations/dagster_deploy.md)
   - K8s manifests and secrets guidance (KMS); logging/tracing enablement
