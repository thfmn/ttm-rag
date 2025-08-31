# MCP Adapter Philosophy — Thin, Auditable, and Safe

This document explains why our MCP server is a thin adapter over the TTM Core and how this design enforces safety, determinism, and maintainability. It follows our Separation of Concerns policy and eval‑first culture.

## Why MCP is an Adapter (not the core)
- Clean interface: MCP exposes a small set of well‑defined tools/resources for agents.
- Stability: The authoritative performance APIs live in gRPC/GraphQL. MCP composes them.
- Security: MCP never touches the database; all writes go through guarded pipelines.
- Portability: MCP can run in different transports (STDIO/HTTP) without changing core logic.

## Design Principles
- Separation of Concerns:
  - Core (gRPC/GraphQL) provides read surfaces to KG/Search/RAG.
  - MCP (adapter) exposes agent‑facing tools/resources with minimal glue code.
- Eval‑first:
  - “No citation → no answer” enforced upstream or at policy gates.
  - Tools must surface metrics (retrieval score, conf) and pass readiness checks.
- Determinism and Audit:
  - Input/output hashed; deterministic seed derived from input hash.
  - Every call logs {ts, tool, in_hash, out_hash, seed, latency_ms, status} to audit.log.
- Thai‑first Retrieval:
  - Default TH tokenization/embeddings; cross‑lingual fallback to EN when needed.

## What MCP Does (and Does Not)
- Does:
  - Validate input/output against stable Pydantic schemas
  - Call gRPC services and transform into compact JSON outputs
  - Emit audit entries and return embedded “audit” objects
- Does not:
  - Implement business logic or persistence directly
  - Bypass policy gates or write paths
  - Store secrets or non‑audited state

## Contracts and Evolution
- Contracts are documented in Reference → MCP Contracts.
- Additive evolution only: new optional fields, no breaking changes.
- Keep gRPC/GraphQL and MCP models aligned; contract tests block drift.

## Failure and Retry Strategy (Adapter View)
- Timeout (>P95): reduce top‑k; check cache; retry with backoff (1s/2s/4s)
- Empty hits: reformulate query (lang=auto; add Thai synonyms)
- Low confidence: withhold answer; return citations and scores; request curation
- Schema drift: surface error; block write path; require compatibility resolver

## Operational Notes
- Servers started manually (per project policy). Install via uv only; no auto‑installs.
- Readiness checks required before production:
  - Tool discovery, ping, hybrid_search("ฟ้าทะลายโจร"), rag_answer (≥3 cites), eval.run (metrics)
- Audit log is the source of truth for regression analysis and latency budgeting.

## Architecture Snapshot
```
Agent (Claude/Qwen)
   │
   ▼
MCP Adapter (tools/resources) ──► gRPC Clients ──► Core Services (gRPC/GraphQL)
   │                                  │
   │                                  └─► KG/Search/RAG Modules ──► DB/Vector Store
   └─► audit.log (in/out hashes, seed, latency, status)
```

Takeaway: Keep the adapter thin and auditable; keep the core authoritative and performant. This separation makes the system safer, faster to evolve, and easier to reason about.
