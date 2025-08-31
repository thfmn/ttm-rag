# Tech Context — TTM‑MCP Expert Agent

## Languages, Frameworks, Protocols
- Python 3.11+ (uv-managed)
- FastAPI (existing REST surface)
- gRPC (new authoritative read surface; high-performance internal API)
- GraphQL (new read surface; consumer-friendly queries)
- Model Context Protocol (MCP) for agent adapter
- SQLAlchemy (DB access)
- PostgreSQL + pgvector (production vector store), SQLite fallback (dev/local)
- Sphinx + MyST + Furo (documentation; Diataxis)
- pytest + pytest-cov (+ markers for integration/ethics)
- Docker + Docker Compose (deploy stack; optional OTel)

## Packaging and Tooling (Policy)
- uv required for all Python dependencies
- Never auto-install; document commands only
- Servers/processes started manually by user (Makefile/docs)
- Linux container targets; NVIDIA GPU optional for LLMs (Open WebUI/Ollama profiles)

## Core Services
- REST (existing): src/api/ with RAG endpoints, health, metrics
- New gRPC: src/api/grpc/ (protos + server implementations)
  - KGService: GetHerb, QueryPaths
  - SearchService: HybridSearch
  - RagService: Answer
  - EvalService: RunEval
  - IngestService: RunIngest
- New GraphQL: src/api/graphql/schema.py (read-only mirrors of gRPC types)
- MCP Server (adapter): tools/ttm-mcp/
  - server.py registers tools/resources
  - adapters/grpc_client.py for service access
  - schemas/ Pydantic I/O models
  - logging/audit and config modules

## RAG Core
- src/rag/: chunking, embeddings, retrieval, vector store
- embeddings: Thai-first (EMBED_MODEL_TH), English fallback (EMBED_MODEL_EN)
- retrieval: hybrid BM25 + vector; tunable via env SEARCH_TOPK/RAG_TOPK
- database: PostgreSQL+pgvector prod; SQLite fallback dev

## Observability
- audit.log (structured NDJSON): {ts, tool, in_hash, out_hash, seed, latency_ms, status}
- /health and /metrics for REST
- P95 latency tracked via audit; thresholds enforced in CI
- Optional OpenTelemetry compose profile for future tracing

## Env & Configuration (to be present in .env.example)
- Core API:
  - TTM_API_URL, TTM_API_KEY
- Retrieval:
  - EMBED_MODEL_TH, EMBED_MODEL_EN, SEARCH_TOPK, RAG_TOPK
- Optional MCP servers:
  - FIRECRAWL_API_KEY, LIGHTPANDA_API_KEY, CONTEXT7_API_KEY
- Existing env retained: DATABASE_URL, Redis, security, ports, etc.

## Dependencies (documented uv commands; do not auto-install)
- Core:
  - uv pip install fastapi uvicorn pydantic pydantic-settings orjson sqlalchemy
- gRPC:
  - uv pip install grpcio grpcio-tools
- GraphQL:
  - uv pip install strawberry-graphql
- MCP server:
  - uv pip install modelcontextprotocol orjson grpcio pydantic
- Testing:
  - uv pip install pytest pytest-cov pytest-xdist
- Docs:
  - uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild

## Directory Conventions
- src/api/grpc/: .proto and grpc_server.py
- src/api/graphql/: schema.py (+ modules)
- tools/ttm-mcp/: server.py, adapters/, schemas/, logging.py, config.py
- src/utils/: audit.py, determinism.py
- src/validation/: policy_gates.py
- scripts/: readiness/eval harness
- tests/unit and tests/integration

## External Integrations (Optional)
- Open WebUI (already present; integrates with API)
- firecrawl MCP (web search/scrape)
- lightpanda MCP (structured extraction/tabulation)
- context7 MCP (docs context)
- sequential-thinking MCP (planning)

## Constraints and Non-Functional Requirements
- Eval-first: metrics for retrieval/answer; readiness checks before prod
- Determinism: seed derived from input hash, stable results within tolerance
- Security: no secrets in logs; HTTPS middleware; CORS hardened in prod
- Performance targets: P95 hit ≤ 400ms; miss ≤ 1200ms; R@10 ≥ 0.80; factuality ≥ 0.90

## Testing Practices
- Unit tests: schema contracts, gates, audit/determinism helpers
- Integration: MCP↔gRPC; rate-limited; ≤3 results; 1s min delay
- Coverage: ≥80% for new code; 100% for policy/determinism utilities
- Make targets: make test, make test-integration, make test-cov

## Deployment Modes
- docker/deploy/compose.yml with profiles:
  - core (Open WebUI), api, db, llm, otel
- Host vs containerized Ollama supported
- Environment keys via .env; secrets never baked into images

Takeaway: Modern Python stack with uv, authoritative gRPC/GraphQL cores, a thin MCP adapter, and auditable/evaluable RAG—documented and test-first.
