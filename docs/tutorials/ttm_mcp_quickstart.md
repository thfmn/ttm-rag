# Tutorial — TTM‑MCP Expert Agent Quickstart

This tutorial gets you from zero to calling the TTM Core via the MCP adapter interface, following our Diataxis style. You will wire environment keys, build the gRPC/GraphQL facades (stubs), and prepare an MCP server skeleton that agent clients (e.g., Claude/Qwen) can discover. No automated installs; commands are documented for you to run manually.

## Prerequisites
- Python 3.11+ and uv package manager
- Docker (optional, for stack)
- A working clone of this repo and a virtualenv (see Development Setup guide)
- Docs served locally (optional): `make docs-serve` → http://localhost:8081

## Environment
Update `.env` based on `.env.example`. New keys for TTM/MCP:
- TTM_API_URL=http://localhost:8005
- TTM_API_KEY=your_ttm_api_key
- EMBED_MODEL_TH=sentence-transformers/all-MiniLM-L6-v2
- EMBED_MODEL_EN=sentence-transformers/all-MiniLM-L6-v2
- SEARCH_TOPK=10
- RAG_TOPK=5
- Optional: FIRECRAWL_API_KEY, LIGHTPANDA_API_KEY, CONTEXT7_API_KEY

## Install (documented, do not auto-run)
- Core services and gRPC/GraphQL:
  - uv pip install fastapi uvicorn pydantic pydantic-settings orjson sqlalchemy
  - uv pip install grpcio grpcio-tools strawberry-graphql
- MCP server adapter (skeleton):
  - uv pip install modelcontextprotocol orjson grpcio pydantic
- Testing:
  - uv pip install pytest pytest-cov pytest-xdist

## Step 1 — Generate gRPC stubs (read-only contracts)
Our proto lives at `src/api/grpc/ttm_core.proto`. Generate Python stubs to a package path (example below uses the current working directory as target; adjust to your desired output path and PYTHONPATH):

```bash
# Generate protobuf and gRPC Python files (run manually)
uv run python -m grpc_tools.protoc \
  -I src/api/grpc \
  --python_out=. \
  --grpc_python_out=. \
  src/api/grpc/ttm_core.proto
```

Expected files (example layout):
- ttm/core/v1/ttm_core_pb2.py
- ttm/core/v1/ttm_core_pb2_grpc.py

If imports fail when starting the gRPC server, ensure these files are importable on PYTHONPATH.

## Step 2 — Start the REST API (existing)
This repo already ships a FastAPI app. For development:

```bash
# Start FastAPI API with auto-reload
make dev
# Browse OpenAPI docs at
# http://localhost:8005/docs
```

## Step 3 — Start a gRPC server (manual runner)
We provide a scaffold at `src/api/grpc/grpc_server.py` that registers service servicers. To run a local gRPC server, create a small runner (example):

```python
# save as scripts/run_grpc_server.py (example)
import grpc
from concurrent import futures
from src.api.grpc.grpc_server import add_services, get_listen_address

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    add_services(server)
    server.add_insecure_port(get_listen_address())  # defaults to 0.0.0.0:50051
    server.start()
    print(f"gRPC listening on {get_listen_address()}")
    server.wait_for_termination()

if __name__ == "__main__":
    main()
```

Run it manually:
```bash
uv run python scripts/run_grpc_server.py
```

Note: The current implementation returns stubbed responses; wire them to your core modules incrementally.

## Step 4 — MCP server skeleton
We add a minimal MCP server under `tools/ttm-mcp/` (skeleton files). It will:
- Register resources: kg://herb/{id}, paper://pmid/{id}
- Register tools: tool.query_kg, tool.hybrid_search, tool.rag_answer, tool.find_contraindications, tool.ingest.run, tool.eval.run
- Use a gRPC client to call TTM Core services (never import core modules directly)
- Emit audit metadata (input/output hashes, seed, latency)

Install note (manual):
```bash
uv pip install modelcontextprotocol
```

Launching locally with MCP client(s) varies by client; see “How‑to → MCP Readiness Checks” for validation.

## Step 5 — Readiness checks
Use our script to verify surfaces (MCP discovery, ping, hybrid_search for ฟ้าทะลายโจร, rag_answer with ≥3 cites, eval.run returning metrics). See “How‑to → MCP Readiness Checks”.

## Validation
- FastAPI available at http://localhost:8005
- gRPC process started and listening (default 0.0.0.0:50051)
- MCP server skeleton visible to your client (tools/resources listed)
- Readiness checks pass or show actionable failures

## Troubleshooting
- Missing gRPC stubs: re-run grpc_tools.protoc and ensure PYTHONPATH includes generated package
- Imports fail during docs build: mock heavy deps in `docs/conf.py` via `autodoc_mock_imports`
- MCP server not visible: confirm client MCP settings, environment variables, and that the process is running
- No citations in answers: policy gates will withhold answers; wire retrieval→generation and ensure citations are returned

## Next steps
- Wire gRPC services to your retrieval/RAG modules
- Implement auditing in MCP tool wrappers
- Add curated bilingual eval set and tune SEARCH_TOPK/RAG_TOPK and τ
- Integrate optional MCP servers if they improve retrieval quality/latency

Takeaway: You now have a thin, auditable MCP socket over TTM Core surfaces. Wire the stubs to your modules and lock quality via readiness and eval.
