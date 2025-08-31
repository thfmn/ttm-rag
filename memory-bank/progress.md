# Progress — TTM‑MCP Expert Agent

## What Works
- Memory Bank initialized with core files:
  - projectbrief.md, productContext.md, systemPatterns.md, techContext.md, activeContext.md
- Architecture plan aligned to repo: thin gRPC/GraphQL facades over existing modules; MCP as adapter
- Determinism & audit strategy defined (hashes, seeds, latency; audit.log)
- Policy gates defined (“no citation → no answer”, confidence threshold τ)
- Diataxis documentation plan prepared (tutorials/how‑to/reference/explanations)

## What’s Pending
- Extend .env.example with TTM/MCP and retrieval keys (TTM_API_URL, TTM_API_KEY, EMBED_MODEL_TH/EN, SEARCH_TOPK, RAG_TOPK, optional FIRECRAWL_API_KEY, LIGHTPANDA_API_KEY, CONTEXT7_API_KEY)
- Add Diataxis pages:
  - tutorials/ttm_mcp_quickstart.md
  - how-to/mcp_readiness_checks.md
  - reference/mcp_contracts.md
  - explanations/mcp_adapter_philosophy.md
- Scaffold:
  - src/api/grpc/ (protos + grpc_server.py)
  - src/api/graphql/schema.py
  - tools/ttm-mcp/ (server.py, adapters/grpc_client.py, schemas/, logging.py, config.py)
- Readiness script updates and tests (unit + integration)

## Current Status
- Session focus: initialize Memory Bank, prepare env keys, update docs, then scaffold facades and MCP.
- Repo integration approach locked: MCP only talks to core via gRPC (no direct imports).

## Known Issues / Risks
- Schema drift risk between Pydantic and .proto/GraphQL → add contract tests and block write path on mismatch.
- Latency regressions → track P95 in audit and enforce CI thresholds.
- Cross‑lingual retrieval tuning required (Thai/English embeddings) → curate bilingual eval set.
- Secrets handling → strictly env; never log secrets; use encryption utility if persisted.

## Decisions and Evolution
- Adopt uv-only package policy per .clinerules; document install commands without executing.
- MCP optional servers (firecrawl/lightpanda/context7) documented as optional accelerators, not hard dependencies.
- Deterministic seed derived from input hash; output hash excludes audit fields to prevent recursion.

## Next Steps (Short Horizon)
1) Append new keys to .env.example (non-destructive).
2) Create Diataxis docs stubs for MCP quickstart/how‑to/reference/explanations.
3) Add gRPC/GraphQL scaffolds and MCP skeleton (files only; tests to follow).
4) Extend scripts/validate_rag_readiness.py and add smoke tests.

Takeaway: Foundation documented and aligned; proceed to env keys, docs, then code scaffolds with readiness tests.
