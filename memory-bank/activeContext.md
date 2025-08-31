# Active Context — TTM‑MCP Expert Agent

## Current Focus (this session)
- Initialize Cline Memory Bank (core files) to preserve context across sessions.
- Align design with repo: add thin gRPC/GraphQL facades and a minimal MCP adapter over existing RAG/KG/Search modules.
- Keep docs up to date using Diataxis; add MCP quickstart/how‑to/reference/explanations.
- Extend .env.example with TTM/MCP keys and Thai‑first retrieval parameters.

## Recent Changes
- Added Memory Bank:
  - projectbrief.md (purpose/scope/principles/metrics/interfaces)
  - productContext.md (users, journeys, constraints, success metrics)
  - systemPatterns.md (architecture, flows, contracts, audit, gates)
  - techContext.md (stack, env, packaging, testing, deployment)
- Audited .env.example (pending: add TTM_API_URL/KEY, EMBED_MODEL_TH/EN, SEARCH_TOPK, RAG_TOPK, optional MCP keys).
- Planned Diataxis additions for MCP: tutorials/how‑to/reference/explanations.

## Next Steps (implementation sequence)
1) Memory Bank
   - Create progress.md and keep it updated as the source of truth.
2) Environment
   - Append TTM/MCP/embedding keys to .env.example (no destructive edits).
3) Documentation (Diataxis)
   - tutorials/ttm_mcp_quickstart.md (end‑to‑end)
   - how-to/mcp_readiness_checks.md
   - reference/mcp_contracts.md (Pydantic I/O schema specs)
   - explanations/mcp_adapter_philosophy.md
   - Update section index pages to include new docs.
4) Scaffolding
   - src/api/grpc/: proto files + grpc_server.py (stubs wired to existing modules)
   - src/api/graphql/schema.py (read‑only)
   - tools/ttm-mcp/: server.py, adapters/grpc_client.py, schemas/, logging.py, config.py
5) Readiness & Tests
   - Extend scripts/validate_rag_readiness.py
   - Add unit tests (schemas/gates/audit) + integration tests (MCP↔gRPC)

## Decisions (immutable until revised)
- MCP = adapter; must call core via gRPC, not import internal modules.
- “No citation → no answer” enforced in policy gates.
- Determinism: seed derived from input hash; audit every call with in/out hashes and latency.
- Thai‑first retrieval with cross‑lingual fallback; env‑tunable top‑k and thresholds.

## Risks & Mitigations
- Schema drift: proto/Pydantic contract tests; block write path.
- Latency regression: track P95 in audit.log; add CI thresholds.
- Cross‑lingual recall: curated bilingual eval set; tune τ and top‑k.
- Secrets exposure: env only; redact logs; optional encryption util for persisted metadata.

## Open Questions (to resolve during integration)
- Which exact embedding models for EMBED_MODEL_TH/EN as defaults? (placeholder env keys for now)
- Any existing gRPC/GraphQL codegen preferences in repo? (default to grpcio-tools, strawberry)
- Final URI scheme mapping for kg://herb/{id} and paper://pmid/{id} into core data access (read‑only).

Takeaway: Execute Memory Bank + env + docs first, then scaffold thin gRPC/GraphQL and the MCP adapter with audit and readiness tests.
