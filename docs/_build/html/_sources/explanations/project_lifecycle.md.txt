# Project Lifecycle and Status

Authoritative source of truth for the current status, roadmap, and key decisions of the Thai Traditional Medicine RAG Bot project. Keep this file updated as part of any significant change (feature, architecture, security, or deployment).

Sync policy:
- This file is authoritative for status and roadmap.
- The following must remain consistent with this document at all times:
  - docs/current_state.md
  - docs/future_steps.md
  - docs/cto_assessment.md
- When updating any of the above, update this file first, then reflect changes in those documents.

---

## 1) Executive Summary

Purpose: Build a production-grade, auditable, Thai-first Retrieval-Augmented Generation (RAG) system that unifies fragmented TTM knowledge and serves credible, cited answers. The system emphasizes evaluation-first (“no citation → no answer”), determinism, and security-by-default.

Business outlook (from CTO assessment): Strong buy recommendation (4.25/5). Clear market need, solid architecture, professional engineering practices, and first-mover advantage in a specialized domain. Immediate focus: close security gaps and achieve MVP completeness.

---

## 2) Evidence From Tests (TTD Lens)

What the test suites tell us is stable and expected to work:
- Unit tests cover:
  - API contracts, model and schema validation (Pydantic v2 idioms), rate limiting, retry/backoff utilities
  - PubMed connector (search, fetch, parsing), query builder, exceptions
  - RAG pipeline interfaces (chunking, embeddings, retrieval glue)
  - Dashboard endpoints and basic database operations
- Integration tests validate end-to-end behavior across:
  - PubMed and PMC integration (ethical limits and rate-limiting respected)
  - Database integration paths (pg/SQLite)
  - Open-WebUI model selection surface
  - Rate limiting in realistic flows

Implication: The following are suitable to document as “working” features and reliable usage paths:
- PubMed search → fetch → parse
- RAG ingest and retrieval prototype (chunking, embedding, pgvector similarity)
- REST API endpoints for RAG and health/metrics
- Basic dashboard metrics
- Error handling, retry, and rate limiting patterns

---

## 3) Current State (Developer-Focused)

Core capabilities:
- PubMed connector with TTM-specific query builder, robust error handling, rate limiting
- RAG prototype:
  - Chunking, embeddings, vector storage (PostgreSQL + pgvector), semantic retrieval
  - REST API: /api/v1/rag/documents, /api/v1/rag/query, /api/v1/rag/statistics, /api/v1/rag/health
- Security & Ops:
  - Input sanitization, HTTPS enforcement, CORS controls, audit logging
  - Prometheus metrics and health checks
  - Dockerized PostgreSQL setup; Makefile orchestration; deployment docs
- Observability & Control:
  - Simple dashboard with real-time UI updates
- Quality Engineering:
  - 20+ tests across unit/integration; CI guidance; clear Makefile targets for test/lint/docs

Known limitations:
- Generation component not yet integrated (RAG is retrieval-only prototype)
- Data validation pipeline not implemented
- Single-source dependency risk (PubMed); PMC connector integration is planned but not yet finalized for production
- Authentication layer missing for production-grade API hardening

---

## 4) Roadmap (Diátaxis-aligned, execution-ready)

We use Diátaxis to structure docs and development: Tutorials (from zero to success), How-to (task recipes), Reference (contracts/config), Explanations (design/why). This roadmap tracks work items that must be reflected across docs and tests.

Phase 1 — MVP Readiness (immediate)
- Security gap closure (Critical)
  - Implement OAuth2 auth (FastAPI security) and enforce endpoint protection
  - Confirm CORS constraints for prod; preserve permissive dev defaults
  - Extend audit logging where missing; verify no secrets in logs
- Generation integration (High)
  - Add generation adapter (e.g., Typhoon/OpenAI/Qwen adapters already designed under adapter_registry patterns)
  - Policy gates: “≥3 citations” and confidence threshold τ enforced on answerability
  - Evaluation: Create minimal answer evaluation harness (factuality sampling and regression tracking)
- Data quality (Medium)
  - Implement data validation pipeline (normalization, deduplication, quality scores)
- Data sources (High)
  - Add PMC Open Access connector to mitigate single-source risk
  - Add at least one Thai journal connector (Tier-1)

Success criteria:
- All API endpoints authenticated in production
- Generation answers respect “no citation → no answer,” include ≥3 citations when available
- Second source live (PMC OA), with validation pipeline demonstrating ≥95% acceptance
- All new features covered by unit + integration tests; docs updated

Phase 2 — RAG Enhancement & Optimization
- Retrieval quality and performance
  - Hybrid search (BM25 + vectors), Thai-first embeddings with cross-lingual fallback
  - Embedding model fine-tuning on TTM corpora (where permitted)
- Production ops
  - Grafana dashboards on top of Prometheus metrics
  - Structured logging for debugging
  - Caching strategies (Redis) for hot paths

Phase 3 — Scale & UX
- Distributed ingest (Celery or equivalent)
- Admin dashboard and comprehensive web UI for end users
- Horizontal scaling, improved DB pooling, performance tuning
- Advanced features: query rewriting, multi-hop retrieval, summarization workflows

---

## 5) Architecture & Patterns (Why it works)

- Modular and testable: connectors, pipelines, API, DB layers separated, interfaces are explicit
- Patterns:
  - Builder (query construction for PubMed/PMC)
  - Strategy (pluggable adapters for generation models)
  - Repository (DB abstractions)
  - Policy gates (centralized answerability logic)
- Determinism & audit: hash in/out, seed control; latency tracking; “no secrets in logs”

---

## 6) Risks & Mitigations

- Single-source dependency (High) → Add PMC and Thai journal connectors; cache/replication buffers
- Missing auth (Critical) → OAuth2 now; short-term IP allowlists if necessary; harden CORS
- Scaling constraints (Medium) → Redis caching, DB pooling; profiling and performance budgets
- Cross-lingual retrieval drift (Medium) → Curated bilingual eval sets; tune top-k and τ
- Schema drift risk between docs and implementation (Medium) → TTD discipline; contract tests; docs sync policy below

---

## 7) Documentation Operations (Diátaxis + Sync Policy)

- Authoritative status/roadmap lives here. The three status docs must match:
  - docs/current_state.md (developer-facing current state)
  - docs/future_steps.md (execution plan and next steps)
  - docs/cto_assessment.md (stakeholder snapshot)
- Workflow (required):
  1) Update this file first (status + roadmap)
  2) Update current_state.md, future_steps.md, cto_assessment.md to match
  3) Run “make docs-rebuild” and visually verify
  4) Update tests or plans if status changed (TTD loop)
- Structure standards:
  - Tutorials: start at docs/tutorials/ (e.g., ttm_mcp_quickstart.md)
  - How-to: repeatable task guides (e.g., development_setup.md, deploy.md)
  - Reference: contracts/config/API (e.g., mcp_contracts.md)
  - Explanations: design rationale (e.g., mcp_adapter_philosophy.md, this doc)

---

## 8) Pointers & Entry Points

- API docs (local): http://localhost:8005/docs
- Health: /health; Metrics: /metrics
- Local docs server: make docs-serve → http://localhost:8081
- Deployment stack (Compose + Makefile): see docs/deploy.md
- Open-WebUI integration: adapter registry + endpoints; see docs/adapter_registry.md

---

## 9) Change Log (Status-level)

- 2025-08-31: Introduced authoritative lifecycle doc with TTD-aligned sync policy; planned security and MVP-complete generation integration
- 2025-08-29: CTO assessment (4.25/5); RAG prototype validated; detailed recommendations recorded
