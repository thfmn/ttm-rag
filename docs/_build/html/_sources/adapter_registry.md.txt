# TTM RAG Model Adapter & Registry

This document describes the pluggable generation adapter/registry architecture used by the Thai Traditional Medicine RAG system and its Open-WebUI integration.

## Overview

The RAG pipeline performs chunking, embeddings, storage, and retrieval. Answer synthesis is delegated to a generation backend through a small adapter layer:

- Base interface: `src/rag/models/base.py` (`BaseAdapter`)
- Registry: `src/rag/models/registry.py` (model catalog + lazy adapter factory)
- Concrete adapters:
  - `TyphoonHFAdapter` (Transformers, id: `hf-typhoon-7b`)
  - `OpenAIAdapter` (OpenAI SDK, id: `openai-gpt-4o-mini`)
  - `QwenCodeAdapter` (OpenAI-compatible HTTP endpoint, id: `qwen3-code`)

Open-WebUI gains:
- GET `/api/v1/ttm_rag/models` — returns available adapters
- POST `/api/v1/ttm_rag/` — accepts `{"query": "...", "model": "adapter-id"}`

The frontend surfaces a dropdown next to the TTM button to select the model on a per-request basis.

## Public Model Catalog

Registry exposes a model list for UI use:

- `hf-typhoon-7b` — Typhoon 7B (Transformers), provider: `huggingface`
- `openai-gpt-4o-mini` — OpenAI GPT-4o-mini, provider: `openai`
- `qwen3-code` — Qwen3-Code, provider: `qwen`

Each includes optional `capabilities` and a `default` flag.

## Adapters

All adapters implement:

- `generate(prompt: str, context: list[dict], **kwargs) -> str`
- `model_info() -> dict`

They apply safe fallbacks when dependencies or network access are unavailable to keep local development lightweight (tests pass on CPU without downloading large models).

### TyphoonHFAdapter (Transformers)

- Default CPU inference for local dev
- Optional `device_map="auto"` (requires `accelerate`) for single-GPU
- Lazy-loads model/tokenizer on first use
- Falls back to context summarization if transformers/PyTorch are not available

Config keys (optional):
- `hf_model_id` (default `scb10x/typhoon-7b`)
- `max_new_tokens` (default 256)
- `temperature` (default 0.3)
- `top_p` (default 0.95)
- `device_map` (e.g., `"auto"`)

### OpenAIAdapter

- Lazy loads `openai` SDK if present
- Reads `OPENAI_API_KEY` at runtime; never logs secrets
- Uses modern Responses API if available; falls back to Chat/Completions for older SDKs
- Safe summary fallback if SDK or API key is missing

Config keys (optional):
- `model_name` (default `gpt-4o-mini`)
- `request_timeout` (seconds, default 30.0)

Environment:
- `OPENAI_API_KEY` required for network calls

### QwenCodeAdapter (OpenAI-compatible)

- Uses `httpx` to call an OpenAI-compatible API
- Expects a Chat Completions or Responses-like endpoint
- Safe fallback if base URL or key missing

Config keys / Environment:
- `base_url` or `QWEN_BASE_URL`
- `api_key` or `QWEN_API_KEY`
- `model_name` (default `qwen3-code`)
- `timeout` (seconds, default 30.0)

## RAG Pipeline Integration

`RAGPipeline.query(query, top_k=None, return_context=True, model=None)`

- If `model` is provided, the pipeline uses the registry to load the adapter and generate the answer
- Response includes:
  - `answer` (string)
  - `context` (list of chunks)
  - `sources` (list of source identifiers)
  - `combined_context` (string concatenation of retrieved chunks)

## Open-WebUI Integration

Backend:
- `open-webui/backend/open_webui/routers/ttm_rag.py`
  - GET `/models` (auth required)
  - POST `/` accepts `{"query": "...", "model": "adapter-id"}`

Frontend:
- API:
  - `open-webui/src/lib/apis/ttm_rag.ts`
    - `getTtmRagModels(token)`
    - `queryTtmRag(token, query, model?)`
- Types:
  - `open-webui/src/lib/types/ttm_rag.ts`
- UI:
  - `open-webui/src/lib/components/chat/MessageInput.svelte` (adds a model dropdown)

## Environment Variables

- `OPENAI_API_KEY` — required for OpenAI adapter (not logged)
- `QWEN_BASE_URL` — base URL for Qwen OpenAI-compatible endpoint
- `QWEN_API_KEY` — API key for Qwen endpoint
- `DEFAULT_TTM_MODEL` — optional default adapter id for deployments

## Security

- Keys are read from environment at runtime and are not logged
- Inputs are sanitized; timeouts and retries used where practical (HTTP adapters)

## Performance & Deployment

- Default: CPU inference for Typhoon 7B in dev
- Single-GPU: set `device_map="auto"` if `accelerate` is installed
- Future edge: consider quantization; `bitsandbytes` may not be available on aarch64

### Jetson Orin Nano (aarch64)

- Install NVIDIA-provided PyTorch wheels for aarch64
- Ensure CUDA/cuDNN compatibility
- `bitsandbytes` often not supported; plan alternatives (e.g., llama.cpp adapter via GGUF) for future

## UV Installation Commands (document only)

Follow project policy: do not auto-install; use `uv` and document the purpose.

- Transformers for Typhoon:
  - `uv pip install transformers`
- PyTorch backend:
  - `uv pip install torch`
- OpenAI SDK:
  - `uv pip install openai`
- HTTP client for Qwen endpoint:
  - `uv pip install httpx`
- Optional:
  - Accelerate (for `device_map="auto"`): `uv pip install accelerate`
  - Bitsandbytes (4/8-bit quantization; aarch64 caveats): `uv pip install bitsandbytes`

## Testing

- Unit tests verify registry exposure and pipeline adapter delegation (mocks)
- Integration tests verify Open-WebUI endpoints (mocks)
- Coverage target: > 85% for new code; critical paths at 100% where feasible
