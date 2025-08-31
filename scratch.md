# Scratchpad / Decision Log

This document tracks key decisions, environment variables, and notes during the implementation of model selection and adapters for the TTM RAG system and Open-WebUI.

## Decisions

- Adapter/Registry Pattern:
  - Introduced a `BaseAdapter` interface with concrete adapters for Typhoon (Transformers), OpenAI, and Qwen3-code.
  - Added a lazy-loading `registry` that exposes a model catalog and returns adapter instances by id.
  - Pipeline delegates generation to an adapter only if a `model` parameter is provided per request.

- Response Schema Harmonization:
  - The RAG pipeline now returns `sources` and `combined_context` to satisfy existing unit tests and provide richer context.

- CPU-first Defaults:
  - TyphoonHFAdapter defaults to CPU inference and avoids heavy downloads during tests by using deterministic fallbacks when dependencies are unavailable.

- Open-WebUI Integration:
  - Backend: New `GET /api/v1/ttm_rag/models` and extended `POST /api/v1/ttm_rag/` to accept an optional `model`.
  - Frontend: Added a minimal dropdown near the TTM button to select an adapter model for each RAG query.

- Testing Approach:
  - Unit tests verify registry exposure and pipeline adapter delegation using mocks.
  - Integration tests verify Open-WebUI router endpoints using mocked pipeline/registry.

## Environment Variables

- OPENAI_API_KEY
  - Purpose: Authenticate OpenAI adapter.
  - Notes: Read at runtime; never logged.

- QWEN_BASE_URL
  - Purpose: Base URL for OpenAI-compatible endpoint used by Qwen adapter.

- QWEN_API_KEY
  - Purpose: API key for Qwen-compatible endpoint.

- DEFAULT_TTM_MODEL (optional)
  - Purpose: Select a default adapter id for deployments.

## UV Installation Commands (document only; do not auto-run)

- Transformers (Typhoon):
  - `uv pip install transformers`
- PyTorch (backend for Transformers):
  - `uv pip install torch`
- OpenAI SDK:
  - `uv pip install openai`
- HTTPX for Qwen:
  - `uv pip install httpx`
- Optional:
  - Accelerate for device_map auto placement:
    - `uv pip install accelerate`
  - Bitsandbytes for 4/8-bit quantization (aarch64 caveats):
    - `uv pip install bitsandbytes`

## Deployment Notes

- CPU Default:
  - TyphoonHFAdapter runs on CPU by default. This keeps local development light.

- Single-GPU:
  - If `accelerate` is installed, set `device_map="auto"` in adapter config for single GPU use.
  - Tune `max_new_tokens` and temperature as needed.

- Jetson Orin Nano (aarch64):
  - Use NVIDIA-provided PyTorch wheels compatible with CUDA/cuDNN for aarch64.
  - `bitsandbytes` may not be supported; consider quantization alternatives.
  - Future: add a llama.cpp-based adapter (GGUF) for better edge deployment characteristics.

## File Map (Key Changes)

- Plan: `implementation_plan.md`
- Pipeline / Schema:
  - `src/rag/pipeline.py`
  - `src/rag/generation.py` (added `assemble_prompt`)
- Adapters:
  - `src/rag/models/base.py`
  - `src/rag/models/registry.py`
  - `src/rag/models/hf_adapter.py`
  - `src/rag/models/openai_adapter.py`
  - `src/rag/models/qwen_adapter.py`
  - `src/rag/models/__init__.py`
- Open-WebUI Backend:
  - `open-webui/backend/open_webui/routers/ttm_rag.py` (GET /models, POST with model)
- Open-WebUI Frontend:
  - `open-webui/src/lib/types/ttm_rag.ts`
  - `open-webui/src/lib/apis/ttm_rag.ts`
  - `open-webui/src/lib/apis/index.ts` (re-exports)
  - `open-webui/src/lib/components/chat/MessageInput.svelte` (dropdown)
- Docs:
  - `docs/adapter_registry.md`
  - `docs/index.rst` (linked the page)

## Notes

- Frontend TS warnings in Open-WebUI existed pre-change. The dropdown additions follow existing patterns and should compile under the same conditions as before.
- Full Open-WebUI test suite expects its own environment; unit tests for the core TTM RAG pipeline and registry pass locally. Integration tests created here mock the router dependencies to avoid heavy requirements.
