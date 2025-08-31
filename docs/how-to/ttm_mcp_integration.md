# Integrate the TTM Custom MCP Server (Adapter)

Purpose: document how to expose the project’s capabilities to agent clients via our thin, auditable MCP adapter. This guide is documentation-only and follows the project’s uv/manual policy—do not auto-install or run processes here.

Key ideas:
- Adapter pattern: MCP server is a thin facade over core services (gRPC). It does not import internal core modules directly.
- Transport‑agnostic: you can bind the handler functions to any MCP runtime (stdio or HTTP) without changing adapter logic.
- Audit and determinism: every tool call produces an audit record with hashes, latency, and a deterministic seed derived from inputs.

## What the adapter provides

Resources (read-only):
- `kg://herb/{id}` → Herb node info (stubbed fields in scaffold)
- `paper://pmid/{id}` → Paper resource shell (pmid/title/abstract/authors/links)

Tools:
- `tool.query_kg` → path queries (Herb → Constituent → Indication)
- `tool.hybrid_search` → hybrid BM25 + vector search (Thai-first, EN fallback)
- `tool.rag_answer` → retrieval‑augmented answer with citations and scores
- `tool.find_contraindications` → placeholder (wire to core later)
- `tool.ingest.run` → guarded ingest (dry_run first)
- `tool.eval.run` → retrieval/answer evaluation run

See code: `tools/ttm-mcp/`
- `config.py` → env/config model (`MCPConfig`)
- `logging.py` → audit utilities
- `schemas.py` → Pydantic I/O for tools/resources
- `server.py` → handler registry (`build_handlers`) and example dispatcher
- `adapters/grpc_client.py` → gRPC client shims to core services

## Environment configuration

Set these in your shell or `.env`:

```bash
# Core API / gRPC
export TTM_API_URL="http://localhost:8005"
export TTM_API_KEY="..."                # optional
export GRPC_HOST="0.0.0.0"
export GRPC_PORT="50051"                # or API_GRPC_PORT

# Retrieval defaults
export EMBED_MODEL_TH="sentence-transformers/all-MiniLM-L6-v2"
export EMBED_MODEL_EN="sentence-transformers/all-MiniLM-L6-v2"
export SEARCH_TOPK="10"
export RAG_TOPK="5"

# Optional (external MCP servers; not required)
export FIRECRAWL_API_KEY="..."
export LIGHTPANDA_API_KEY="..."
export CONTEXT7_API_KEY="..."

# Policy thresholds
export ANSWER_CONF_TAU="0.6"
```

## Dependencies (document-only)

Follow uv/manual policy; run these yourself if needed:

```bash
# Core libs for adapter + clients
uv pip install pydantic orjson grpcio

# If you will generate gRPC stubs locally:
uv pip install grpcio-tools
uv run python -m grpc_tools.protoc \
  -I src/api/grpc \
  --python_out=. \
  --grpc_python_out=. \
  src/api/grpc/ttm_core.proto

# MCP runtimes (optional, pick one)
uv pip install modelcontextprotocol   # stdio-based
# or third-party convenience runtimes like "fastmcp" if you prefer
```

## Binding the handlers to an MCP runtime (examples)

The adapter is transport‑agnostic. Use `build_handlers()` from `tools/ttm-mcp/server.py`, then bind to your runtime of choice.

Example: stdio (Model Context Protocol) — pseudo-code

```python
# mcp_server_stdio.py (example launcher; not committed by default)
from modelcontextprotocol import Server
from tools.ttm_mcp.config import load_config
from tools.ttm_mcp.server import build_handlers

def main():
    cfg = load_config()
    handlers = build_handlers()
    server = Server("ttm-mcp")

    # Tools
    server.add_tool("tool.query_kg", lambda params: handlers["tool.query_kg"](cfg, params))
    server.add_tool("tool.hybrid_search", lambda params: handlers["tool.hybrid_search"](cfg, params))
    server.add_tool("tool.rag_answer", lambda params: handlers["tool.rag_answer"](cfg, params))
    server.add_tool("tool.find_contraindications", lambda params: handlers["tool.find_contraindications"](cfg, params))
    server.add_tool("tool.ingest.run", lambda params: handlers["tool.ingest.run"](cfg, params))
    server.add_tool("tool.eval.run", lambda params: handlers["tool.eval.run"](cfg, params))

    # Resources (exposed as tools or via resource hook depending on runtime)
    server.add_tool("resource.kg.herb", lambda p: handlers["resource:kg:herb"](cfg, p["id"])[0])
    server.add_tool("resource.paper.pmid", lambda p: handlers["resource:paper:pmid"](cfg, p["pmid"])[0])

    server.run_stdio()

if __name__ == "__main__":
    main()
```

This demonstrates one way to wire handlers; adapt to your preferred MCP runtime’s registration API.

## Integrating with Cline (VS Code) — local launcher

In your Cline MCP settings JSON (manual edit), add an entry like:

```json
"ttm-mcp": {
  "command": "uv",
  "args": ["run", "python", "mcp_server_stdio.py"],
  "env": {
    "TTM_API_URL": "http://localhost:8005",
    "GRPC_HOST": "0.0.0.0",
    "GRPC_PORT": "50051",
    "SEARCH_TOPK": "10",
    "RAG_TOPK": "5"
  },
  "disabled": false,
  "autoApprove": []
}
```

Notes:
- Do not log secrets. Provide API keys via env.
- Keep the adapter read‑only; all writes go through controlled pipelines.
- If you prefer an HTTP transport, choose a runtime that supports it and map the same handlers.

## Tools & resources — I/O contracts

All inputs/outputs are Pydantic models in `tools/ttm-mcp/schemas.py`. At a glance:

- `tool.query_kg(QueryKGInput) → QueryKGOutput`
- `tool.hybrid_search(SearchInput) → SearchOutput`
- `tool.rag_answer(RagAnswerInput) → RagAnswerOutput`
- `tool.find_contraindications(ContraindicationsInput) → ContraindicationsOutput`
- `tool.ingest.run(IngestInput) → IngestOutput`
- `tool.eval.run(EvalInput) → EvalOutput`
- `resource:kg:herb(id: str) → HerbResource`
- `resource:paper:pmid(pmid: str) → PaperResource`

Each response embeds `audit` (hashes, latency, status) per adapter policy.

## Readiness checks

Once bound, verify the most basic flows (see also `docs/how-to/mcp_readiness_checks.md`):

1) KG resource:
```json
{"id": "some-herb-id"}
```
Call `resource.kg.herb` and expect a resource payload + audit.

2) Hybrid search:
```json
{"query":"ฟ้าทะลายโจร", "lang":"th", "top_k":5}
```
Call `tool.hybrid_search` and expect hits[] + audit.

3) RAG answer (retrieval-only generation OK at prototype stage):
```json
{"question":"สรรพคุณของฟ้าทะลายโจรคืออะไร", "lang":"th", "retrieval":{"top_k":5}}
```
Call `tool.rag_answer` and expect answer, citations[], scores{}, audit.

## Security and policy

- No secrets in logs; redact tokens.
- Enforce answerability/policy gates in core or at the adapter boundary (≥3 citations, confidence τ).
- Determinism: a seed is derived from input hash for stable behavior; avoid global static seeds.

## Troubleshooting

- gRPC connection refused:
  - Ensure core gRPC server is running and `GRPC_HOST/GRPC_PORT` are correct.
- Empty/stub responses:
  - Some handlers are scaffolded; wire gRPC stubs and core methods where noted.
- CORS/docs:
  - Adapter is separate from REST docs; for UI integration, see Open‑WebUI integration under `docs/adapter_registry.md`.

## Related docs

- Explanations → Project Lifecycle and Status: `docs/explanations/project_lifecycle.md`
- Explanations → MCP Adapter Philosophy: `docs/explanations/mcp_adapter_philosophy.md`
- How‑to → MCP Readiness Checks: `docs/how-to/mcp_readiness_checks.md`
- Reference → MCP Contracts: `docs/reference/mcp_contracts.md`
