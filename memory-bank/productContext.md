# Product Context — TTM‑MCP Expert Agent

## Why This Exists
Thai Traditional Medicine (TTM) knowledge is fragmented across academic papers, Thai journals, practitioner manuals, and government sources. Researchers and engineers need an auditable, high‑precision system to retrieve, connect, and summarize this knowledge with credible citations. The TTM‑MCP Expert Agent provides a thin, standards‑based socket (MCP) over a performant, domain‑specific core (KG/Search/RAG) to enable agent clients (Claude/Qwen/etc.) to consume results safely and deterministically.

## Problems We Solve
- Fragmented sources: unify Thai‑first retrieval across heterogeneous data (TH⇄EN).
- Credibility: enforce “no citation → no answer” and expose metrics/scores.
- Auditability: hash inputs/outputs; deterministic seeds and structured logs.
- Separation of concerns: production‑grade APIs for internal performance vs. external consumption vs. agent adapter.

## Target Users
- TTM researchers and data engineers integrating pipelines and evaluation.
- ML engineers building QA/research agents with MCP tooling.
- Platform teams needing deterministic, logged, and policy‑gated tool calls.

## What “Good” Looks Like
- Accurate Thai‑first retrieval with cross‑lingual fallback (EN) when needed.
- Answers include ≥3 citations with retrieval and confidence scores.
- All tool calls produce audit metadata (in_hash, out_hash, seed, latency).
- Clear readiness checks; regression‑resistant evaluation harness.

## Core User Journeys
1) Research (Literature & State‑of‑Practice)
   - Query via MCP optional web tools (firecrawl/context7)
   - Link KG/RAG hits; produce a concise, cited report with findings table

2) RAG‑QA (Production answers)
   - Normalize → hybrid retrieval → policy gates → cited answer with scores

3) Ingest (PDF→KG)
   - Define batch spec → dry‑run → process (OCR/NER/Linking) → guarded KG write → post‑eval receipt

4) Evaluation
   - Load eval set → run retrieval/answer eval → report trend/regression

## Product Constraints
- MCP remains read‑only to KG by default; writes occur only via controlled pipelines.
- Determinism logs are mandatory for every tool; no chain‑of‑thought exposure.
- Thai‑first defaults; embeddings and tokenization configured via env.

## Experience Goals
- Fast to adopt: documented Diataxis (tutorials/how‑to/reference/explanations)
- Reproducible: uv‑based installs (document commands; never auto‑install)
- Observable: One‑line readiness checks with crisp pass/fail expectations
- Portable: Docker/Compose targets; sample MCP client configs for Claude/Qwen

## Out‑of‑Scope (Non‑Goals)
- Medical or regulatory advice; patient‑specific guidance
- Unreviewed write paths to KG
- Non‑audited tool calls or free‑form generation without citations

## Operating Principles
- MCP = Adapter: thin, safe; core is authoritative APIs (gRPC/GraphQL/REST).
- Eval‑first: gate responses by retrieval quality and confidence thresholds.
- Fail fast: timeouts/backoff strategies; escalate to secondary tools on miss.
- Thai‑first: retrieval configured for Thai by default with bilingual coverage.

## Success Metrics (Product)
- Retrieval R@10 ≥ 0.80 on curated bilingual eval set
- Answer factuality ≥ 0.90 (strict)
- P95 latency ≤ 400 ms (hit), ≤ 1200 ms (miss)
- Readiness checks green; no citation violations in production

## Interfaces (Consumption)
- MCP tools/resources:
  - tool.query_kg, tool.hybrid_search, tool.rag_answer, tool.find_contraindications, tool.ingest.run, tool.eval.run
  - kg://herb/{id}, paper://pmid/{id}
- Optional MCP servers:
  - firecrawl (web search/scrape), lightpanda (structured extraction), context7 (docs), sequential‑thinking (planning)
- Read surfaces (internal authoritative):
  - gRPC, GraphQL over core KG/Search/RAG modules

## Documentation & Onboarding
- Tutorials: End‑to‑end MCP quickstart
- How‑to: Readiness checks; optional MCP servers; auditing determinism
- Reference: MCP I/O contracts; gRPC/GraphQL schemas
- Explanations: Adapter architecture; Thai‑first retrieval design
- README: Entry points (API, docs, Open WebUI), model dropdown and RAG API usage

## Risks & Mitigations (Product)
- Retrieval drift across Thai/English: curated bilingual evals and thresholds
- Latency regressions: audit P95 in CI; rollback policy
- Schema drift: contract tests; block write path on mismatch
- Key management: env‑only; never log secrets; encryption for persisted metadata

Takeaway: Deliver a credible, Thai‑first knowledge experience via a thin MCP socket over a robust, measurable core—always cited, deterministic, and auditable.
