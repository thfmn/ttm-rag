# Project Brief — TTM‑MCP Expert Agent

## Purpose
Build a Thai Traditional Medicine (TTM) knowledge system with a sharp, auditable core (gRPC/GraphQL/KG/Search/RAG) and expose a minimal, safe Model Context Protocol (MCP) adapter for LLM/agent clients. MCP is a thin socket; the core stays authoritative and performant.

## Scope
- Authoritative Read Surfaces: gRPC + GraphQL over existing REST, invoking internal KG/Search/RAG modules.
- MCP Adapter: Tools/resources for query_kg, hybrid_search, rag_answer, find_contraindications, ingest.run, eval.run; all auditable and deterministic.
- Evaluation‑first: Retrieval and answer quality measured continuously (R@k, MRR, factuality) with smoke checks and curated sets.
- Thai‑first: Default Thai tokenization + embeddings; cross‑lingual fallback to English.

Non‑Goals
- Clinical advice or diagnosis
- Regulatory guidance
- Uncontrolled write paths to the KG (writes are only through guarded pipelines)

## Guiding Principles
- MCP = Adapter: Thin, safe facade for agents. The core remains domain services (KG/Search/RAG).
- Separation of Concerns: Performance APIs (gRPC/GraphQL) ≠ external REST ≠ agent adapter (MCP).
- Eval‑first: No answer without retrieval and citations. Low confidence defers with cites listed.
- Determinism & Audit: Every tool call logs input/output hashes, deterministic seed, latency, status.
- Thai‑first: Cross‑lingual hybrid retrieval (BM25 + vectors), TH prioritized.

## Operating Modes (High‑Level)
- Research: Web/docs search (optional MCP servers) → link to KG/RAG → concise report with citations.
- Planning: Long‑horizon decomposition (optional sequential‑thinking MCP) → OKRs/WBS/risks.
- Ingest: PDF→OCR→NER→Linking→KG via guarded pipeline; dry‑run first; evaluate after.
- RAG‑QA: Normalize → retrieve → policy gates → answer with citations and scores.
- Evaluation: Load eval set → retrieval/answer eval → report & regression tracking.

## Success Metrics (Targets)
- Retrieval R@10 ≥ 0.80 (curated set)
- Answer factuality ≥ 0.90 (strict)
- P95 latency (hit) ≤ 400 ms; (miss) ≤ 1200 ms
- Uptime ≥ 99.5%
- Done criteria per session: ≥3 citations, scores present, explicit decision, clear next steps

## Deliverables (This Phase)
- New Facades: gRPC + GraphQL stubs calling existing RAG/KG/Search modules.
- MCP Server: tools/ttm-mcp/ with resources/tools wired to gRPC client; audit + determinism helpers.
- Readiness Checks: MCP discovery, ping, retrieval (ฟ้าทะลายโจร), rag answer (≥3 cites), eval.run.
- Docs (Diataxis): Quickstarts and references for MCP adapter, contracts, and readiness.
- Cline Memory Bank: Core files to persist context across sessions.

## Constraints & Policies
- Package management: uv only; document `uv pip install …`; never auto‑install.
- Servers: started manually by user (Makefile/docs guide).
- Write path: sacred. Only via controlled pipeline; block on schema drift or policy failure.
- Ethics & API usage in tests: rate‑limited, ≤3 results for integration tests, 1s min interval.

## Risks & Mitigations
- Schema drift between facades and core: Contract tests; block writes; surface health.
- Latency regression: Capture P95 in audit; thresholds in CI.
- Cross‑lingual quality: Curated bilingual evals; tunable top‑k and τ.
- Secret handling: Env‑only; never logged; encryption helpers where persisted.

## Interfaces (Initial)
- gRPC services: KGService (GetHerb, QueryPaths), SearchService (HybridSearch), RagService (Answer), EvalService (RunEval), IngestService (RunIngest).
- GraphQL: read‑only types mirroring gRPC, e.g., herb(id) { names {th en} constituents {name} indications {icdCode} }.
- MCP Tools/Resources: tool.query_kg, tool.hybrid_search, tool.rag_answer, tool.find_contraindications, tool.ingest.run, tool.eval.run; resources kg://herb/{id}, paper://pmid/{id}.

## Environment (Keys)
TTM_API_URL, TTM_API_KEY, FIRECRAWL_API_KEY (optional), LIGHTPANDA_API_KEY (optional), CONTEXT7_API_KEY (optional), EMBED_MODEL_TH, EMBED_MODEL_EN, SEARCH_TOPK, RAG_TOPK.

## Documentation (Diataxis)
- Tutorials: end‑to‑end MCP quickstart
- How‑to: readiness checks; adding optional MCP servers; audit verification
- Reference: MCP tool/resource contracts; gRPC/GraphQL schemas
- Explanations: MCP adapter philosophy; Thai‑first retrieval strategy

Takeaway: A verifiable, Thai‑first core with a thin, auditable MCP socket and evaluation baked into the loop.
