# How‑to — MCP Readiness Checks

Validate that the TTM‑MCP surfaces are discoverable and sane before using them in agents. This guide follows our eval‑first policy and Diataxis “how‑to” style.

## Prerequisites
- Environment configured from `.env.example` (TTM_API_URL, TTM_API_KEY, SEARCH_TOPK, RAG_TOPK, optional Firecrawl/Lightpanda/Context7 keys)
- FastAPI API running locally
- gRPC stubs generated and a local gRPC server started (stubbed OK)
- Optional MCP servers (firecrawl/lightpanda/context7) running if you want to test them

Commands are documented; run them manually per project rules (uv only).

## 1) Start core services (manual)
```bash
# API (FastAPI)
make dev

# gRPC (example runner)
# Ensure you generated stubs from src/api/grpc/ttm_core.proto
# uv run python scripts/run_grpc_server.py
```

Expected:
- API at http://localhost:8005/health and /docs
- gRPC listening (default 0.0.0.0:50051)

## 2) Verify environment
```bash
# Check critical keys are present in your shell
export | grep -E 'TTM_API_URL|TTM_API_KEY|SEARCH_TOPK|RAG_TOPK|EMBED_MODEL_(TH|EN)'
```

## 3) MCP discovery (server and tools/resources)
Depending on your MCP client (e.g., Claude Desktop, Qwen Code), ensure the server entry for “ttm-core” is configured (see client config examples in the task brief). Then list the MCP tools/resources in your client UI.

Expected tools/resources:
- tools: tool.query_kg, tool.hybrid_search, tool.rag_answer, tool.find_contraindications, tool.ingest.run, tool.eval.run
- resources: kg://herb/{id}, paper://pmid/{id}

If not visible, restart the MCP server process and re-open the client.

## 4) Healthcheck — tool.query_kg --dry --ping
Issue a dry‑run/ping via your MCP client. If your client allows arguments, pass a minimal payload:
```json
{ "start": { "type": "herb", "id": "ping" }, "max_depth": 0, "dry": true }
```
Expected: { "status": "ok" } or an equivalent healthy response.

## 5) Retrieval — Hybrid search (Thai‑first)
Run:
```json
{ "query": "ฟ้าทะลายโจร", "lang": "th", "top_k": 10 }
```
Expected:
- ≥ 5 hits with score ≥ τ (configured threshold)
- Each hit contains id, type, title/snippet, score, source

If empty: try lang="auto" or reduce top_k; check that embeddings and retrieval configs are set.

## 6) RAG answer — Citations and scores
Run:
```json
{ "question": "สรรพคุณของฟ้าทะลายโจรคืออะไร?", "lang": "th", "retrieval": { "top_k": 5 } }
```
Expected:
- Answer string AND ≥ 3 citations with retrieval_score/answer_conf
- If citations are < 3 or answer_conf < τ, policy gates may withhold the final answer and return citations only

## 7) Evaluation — Smoke metrics
Run:
```json
{ "set": "smoke", "metrics": ["R@k","MRR","factuality"] }
```
Expected:
- Metrics JSON and (optional) report_uri

## 8) Audit & determinism — Verify logs
Every tool call must emit a structured audit entry:
```
{ "ts": "...", "tool": "tool.hybrid_search", "in_hash": "...", "out_hash": "...", "seed": 123, "latency_ms": 123, "status": "ok" }
```
Check `audit.log` at repo root. Input/output hashes should change only when payload or results differ. Seed is derived from input hash.

## Troubleshooting
- Tools not listed: confirm MCP server is started and client has the server configured; restart client MCP manager.
- Healthcheck fails: verify API and gRPC are running; inspect server logs; ensure stubs import correctly.
- Empty hits: switch lang to "auto" and increase top_k; ensure embeddings exist/are configured.
- Low confidence answers: tune SEARCH_TOPK/RAG_TOPK; ensure Thai synonyms; verify citations pipeline.
- Audit missing: confirm audit logger is wired in MCP tool wrappers.

## Ethical usage
- Respect external API terms if optional MCP servers are used (rate limits; ≤3 results in tests; 1s delay).

Takeaway: Run discovery → ping → retrieval (Thai) → RAG answer → eval → audit verification. If any step fails, fix before production use.
