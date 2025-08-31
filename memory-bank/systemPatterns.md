# System Patterns — TTM‑MCP Expert Agent

## Architecture Overview
- Core = Authoritative Services (internal):
  - REST (existing FastAPI) for current RAG endpoints
  - New gRPC and GraphQL read surfaces (thin facades) calling internal modules:
    - KG/Search/RAG orchestration under src/rag/, src/pipelines/, src/database/
- Adapter = MCP Server (external consumption):
  - Python MCP server (tools/ttm-mcp/) exporting minimal, auditable tools/resources
  - MCP speaks to core via gRPC client only (never imports core modules directly)

High-level flow:
Client (Claude/Qwen) → MCP (tools) → gRPC Services → Core Modules (KG/Search/RAG) → DB/Vector Store → Results (+audit)

## Components and Responsibilities
- src/api/
  - rest/ (existing): FastAPI routers, health/metrics, RAG endpoints
  - grpc/: proto files + grpc_server.py implementations (call into core)
  - graphql/: schema + resolvers (read-only, call into core)
- src/rag/: chunking, embeddings, vector store, retrieval primitives
- src/pipelines/: ingest and orchestration steps
- src/database/: SQLAlchemy models and connection management (SQLite/PG w/ pgvector)
- src/utils/:
  - audit.py: canonical JSON, SHA-256 hashing, latency capture, structured logs
  - determinism.py: seed derivation from input hashes
- src/validation/policy_gates.py: “no citation → no answer”, confidence thresholds τ
- tools/ttm-mcp/:
  - server.py: MCP server entry; registers resources and tools
  - adapters/grpc_client.py: typed clients to gRPC services
  - schemas/: Pydantic models for inputs/outputs (stable contracts)
  - logging.py: audit wrapper per call
  - config.py: env parsing; top‑k, embeddings, endpoints
- scripts/: readiness checks, evaluation harness
- tests/: unit (schemas/gates/audit) + integration (MCP↔gRPC) with rate-limit rules

## Key Design Patterns
- Facade: gRPC/GraphQL provide clean read-only contracts over internal modules
- Adapter: MCP tools map natural task boundaries to core service calls
- Policy Gate: centralized, testable constraints on answerability and confidence
- Deterministic Pipeline: seeds derived from hashed inputs to stabilize stochastic ops
- CQRS-lite: write path (ingest pipeline) is gated; read paths go through read surfaces
- Anti-corruption Layer: MCP never links directly into core module imports; only gRPC

## Data and Control Flow
- Retrieval:
  1) Request → tool.hybrid_search (MCP) → gRPC SearchService → core retrieval → results (hits[], scores)
  2) Audit: input hash, latency, seed; output hash (without audit)
- RAG Answer:
  1) Request → tool.rag_answer (MCP) → gRPC RagService → core retrieval + generation adapter → answer + cites + scores
  2) Policy: enforce “≥3 citations” and τ threshold; otherwise defer with cites only
  3) Audit logged per tool call
- Ingest (controlled write):
  1) tool.ingest.run (dry_run first) → pipeline execution → controlled KG writes (if enabled)
  2) On completion: tool.eval.run to produce metrics receipt

## Contracts and Compatibility
- Contracts defined in Pydantic models (tools/ttm-mcp/schemas/…) and .proto messages
- Backward-compatible evolution:
  - Additive changes only (new optional fields)
  - Version tagging via release notes in docs/reference/ and proto package version
  - Contract tests in tests/unit/mcp/test_tool_schemas.py and tests/unit/api/test_proto_contracts.py
- GraphQL schema ports read-only models mirroring .proto; resolvers call gRPC for parity

## Observability and Audit
- Every tool call writes a structured log line to audit.log:
  {ts, tool, in_hash, out_hash, seed, latency_ms, status, error?}
- P95 latency tracking derived from audit logs; thresholds alarmed in CI
- Health endpoints for API; readiness script verifies MCP surface

## Failure Handling and Retries
- Tool timeout (>P95): reduce top‑k; consult cache; backoff 1s/2s/4s
- Empty hits: reformulate query (lang=auto, Thai synonyms); secondary tool fallback (optional firecrawl/context7)
- Low confidence: withhold answer; list citations; request human curation
- Schema drift: 4xx schema errors → compatibility resolver; block write path

## Security and Secrets
- Env-only secrets; never logged (keys redacted)
- HTTPS/redirection enforced by middleware for external REST; gRPC typically internal network only
- CORS constrained for production
- Optional data encryption helpers where persisted metadata is sensitive

## Performance Considerations
- Hybrid retrieval: BM25 + vector retrieval; top‑k defaults via env SEARCH_TOPK
- Embeddings:
  - Thai-first (EMBED_MODEL_TH), English fallback (EMBED_MODEL_EN)
  - Batch operations in core; cache where safe
- DB:
  - pgvector for production; SQLite fallback for local; SQL/idx tuned for similarity

## Critical Paths
- tool.rag_answer: retrieve → gate → answer (generation adapter) → citations
- tool.hybrid_search: fast retrieval path; ensure sub-400 ms P95 on hits
- tool.ingest.run: dry-run validations; guarded write; post-eval receipt

## Evolution Plan (Safe Extensions)
- Add new MCP tools only if they compose existing gRPC services
- Keep MCP server stateless; no direct DB access
- Incremental rollout: feature flags via env; readiness checks must pass before enabling

Takeaway: MCP stays a thin, auditable adapter over stable gRPC/GraphQL facades; policy gates and determinism centralize safety while the core delivers performance and Thai‑first retrieval.
