# Implementation Plan

[Overview]
Enable router/model selection in Open-WebUI and integrate three generation backends—Typhoon 7B (scb10x/typhoon-7b via Transformers), OpenAI, and Qwen3-code—using a pluggable adapter/registry pattern with minimal surface changes and TDD. The RAG pipeline will accept an optional per-request model override, maintain backward compatibility, and adjust its output schema to satisfy existing tests.

The current RAG pipeline handles chunking, embeddings, vector storage, retrieval, and a default text generator. We introduce a small model adapter layer that defers answer generation to the specified model when provided, while leaving chunking/retrieval untouched. Open-WebUI gains a GET /models endpoint to discover available adapters and a POST body field to select a model; the frontend exposes a minimal dropdown and includes the chosen model in requests.

Local constraints: default CPU inference for Typhoon 7B; optional single-GPU deployment config. Edge deployment on Jetson Orin Nano is documented with guidance (potential quantization, aarch64 constraints).

[Types]
Introduce optional model selection, model list payload, and adapter interfaces.

- Python (Pydantic)
  - TtmRagQueryForm (open-webui/backend/open_webui/routers/ttm_rag.py): add field model: Optional[str]
  - TtmRagModelsResponse schema (Python dict): { "models": [ { "id": str, "name": str, "provider": str, "capabilities": dict, "default": bool } ] }
  - Pipeline query result: include keys "sources": List[str or objects], and "combined_context": str, in addition to existing fields.

- TypeScript
  - open-webui/src/lib/types/ttm_rag.ts
    - export interface TtmRagModel { id: string; name: string; provider: string; capabilities?: Record<string, any>; default?: boolean; }
    - export interface TtmRagModelList { models: TtmRagModel[]; }

- Adapter Interfaces
  - BaseAdapter: generate(prompt: str, context: list[dict], **kwargs) -> str; model_info() -> dict

[Files]
Create new adapter modules and minimally modify existing files.

New files:
- src/rag/models/base.py: BaseAdapter definition and common utilities (timeouts, sanitization hooks)
- src/rag/models/registry.py: REGISTRY dict and get_adapter(id: str, config: dict) -> BaseAdapter
- src/rag/models/hf_adapter.py: Typhoon 7B adapter via Transformers pipeline/AutoModelForCausalLM
- src/rag/models/openai_adapter.py: OpenAI adapter using official SDK
- src/rag/models/qwen_adapter.py: Qwen3-code adapter via OpenAI-compatible or vendor SDK/HTTPX
- (Optional) src/rag/models/prompts.py: Prompt templates for Thai answer synthesis and context formatting

Modified files:
- src/rag/pipeline.py: 
  - query(query: str, top_k: Optional[int] = None, return_context: bool = True, model: Optional[str] = None)
  - Add "sources" and "combined_context" to response
  - If model provided, resolve adapter and delegate generation
- src/rag/generation.py:
  - Add assemble_prompt(query, context_chunks) helper; keep TextGenerator as default
- open-webui/backend/open_webui/routers/ttm_rag.py:
  - Add GET /api/v1/ttm_rag/models (behind auth)
  - Extend POST to accept model and pass to rag_pipeline.query(model=model)
- open-webui/src/lib/apis/ttm_rag.ts:
  - add getTtmRagModels(token)
  - extend queryTtmRag(token, query, model?) to include model in body
- open-webui/src/lib/types/ttm_rag.ts:
  - add TtmRagModel, TtmRagModelList types
- open-webui/src/lib/components/chat/MessageInput.svelte:
  - Add a small dropdown next to the TTM button to select the model; include in queryTtmRag call

Documentation:
- docs/ (Sphinx) pages update: API changes, adapter architecture, env vars, deployment notes (CPU, single GPU, Jetson)
- scratch.md: decision log and rationale

[Functions]
Add adapter factory and modify pipeline to allow per-request selection.

New functions:
- src/rag/models/registry.py:
  - get_model_list() -> list[dict]
  - get_adapter(adapter_id: str, config: dict) -> BaseAdapter
- src/rag/generation.py:
  - assemble_prompt(query: str, context_chunks: list[dict], max_context_chars: int = N) -> str
- Adapter methods in each adapter file:
  - generate(prompt, context, **kwargs) -> str
  - model_info() -> dict

Modified functions:
- src/rag/pipeline.RAGPipeline.query:
  - Add model param; produce "sources" and "combined_context" fields; use adapter when model is set
- open-webui/backend/open_webui/routers/ttm_rag.py:
  - New get_models() handler
  - Update query handler to accept model

[Classes]
Introduce BaseAdapter and three concrete adapters.

New classes:
- BaseAdapter (src/rag/models/base.py): Abstract base with generate/model_info; includes common safety wrappers (timeouts, sanitization callouts).
- TyphoonHFAdapter (src/rag/models/hf_adapter.py): 
  - Defaults: CPU inference; option to detect device_map for single-GPU; parameters for max_new_tokens, temperature, top_p; truncates combined_context.
  - Model: "scb10x/typhoon-7b" via transformers.pipeline or AutoModelForCausalLM + AutoTokenizer.
- OpenAIAdapter (src/rag/models/openai_adapter.py): 
  - Uses OPENAI_API_KEY; configurable model name; applies retries and timeouts; redacts keys in logs.
- QwenCodeAdapter (src/rag/models/qwen_adapter.py):
  - Uses OpenAI-compatible endpoint or vendor SDK via HTTPX; supports code-focused outputs; applies timeouts/retries.

Modified classes:
- None beyond pipeline’s method adjustments; TextGenerator remains for default behavior.

[Dependencies]
Add libraries with explanation (do not auto-install; follow uv-only policy).

- transformers: needed for Typhoon 7B local inference
  - uv pip install transformers
- torch: backend for Transformers (CPU wheel for local; CUDA wheel for GPU)
  - uv pip install torch
  - Note: For Jetson Orin Nano (aarch64), use NVIDIA-provided PyTorch wheels (documented in docs) and ensure CUDA/cuDNN compatibility.
- openai: official SDK for OpenAI adapter
  - uv pip install openai
- httpx: robust HTTP client for Qwen (or HF inference REST if used)
  - uv pip install httpx
- Optional:
  - accelerate (device_map="auto")
    - uv pip install accelerate
  - bitsandbytes (4/8-bit quantization); note aarch64 challenges on Jetson—document as optional
    - uv pip install bitsandbytes

[Testing]
Adopt TDD with unit + integration tests. Target >85% coverage for new code.

New unit tests:
- tests/unit/test_model_manager.py
  - registry.get_model_list() returns expected entries for hf-typhoon-7b, openai-..., qwen3-code
  - registry.get_adapter(id) returns correct class; invalid id raises error
- tests/unit/test_generation_integration.py
  - pipeline.query(..., model="hf-typhoon-7b") delegates to TyphoonHFAdapter.generate()
  - prompt assembly truncates combined_context safely; sanitization invoked
  - OpenAI and Qwen adapters mocked to validate request/response handling and error paths
- tests/unit/test_pipeline_response_shape.py
  - Asserts presence of "sources" and "combined_context" in pipeline.query result

Integration tests (mock external calls):
- tests/integration/test_openwebui_model_selection.py
  - GET /api/v1/ttm_rag/models returns model list under auth
  - POST /api/v1/ttm_rag/ with model routes to correct adapter (mocks), status 200

Update existing tests if necessary:
- Align tests/unit/test_rag_pipeline.py expectations with final schema (ensure sources/combined_context present)

[Implementation Order]
1. Write unit tests for registry and pipeline model override (failing initially).
2. Implement BaseAdapter, registry, and TyphoonHFAdapter (CPU default), OpenAIAdapter, QwenCodeAdapter (with mocks).
3. Modify pipeline.query to accept model and add sources/combined_context.
4. Implement Open-WebUI backend: GET /models and POST model param pass-through.
5. Implement frontend: getTtmRagModels, dropdown in MessageInput.svelte, payload with model.
6. Add integration tests for backend endpoints (mock adapters).
7. Update Sphinx docs and scratch.md; list uv commands and env vars (DEFAULT_TTM_MODEL, OPENAI_API_KEY, etc.).
8. Verify all tests pass via make test; do not start servers automatically.

Acceptance Criteria
- API: GET /api/v1/ttm_rag/models (auth-required) returns >=3 models; POST accepts model and routes to correct adapter.
- RAG pipeline: query returns answer, context[], sources[], combined_context; model override works; default behavior unchanged when no model given.
- Typhoon 7B: CPU inference path functional; optional single GPU supported via config; documented Jetson considerations.
- Security: keys never logged; sanitized inputs; timeouts/retries enforced.
- Tests: All new tests pass, coverage >85% for new code; no regressions.

Deployment Notes and Environment
- Local CPU default (Typhoon 7B with Transformers pipeline).
- Single-GPU deployment: set device_map="auto" if accelerate present; document max_new_tokens and VRAM utilization.
- Jetson Orin Nano: document NVIDIA aarch64 PyTorch wheel installation; warn about bitsandbytes compatibility; consider future llama.cpp adapter for GGUF.

UV Installation Commands (document only; do not auto-run)
- uv pip install transformers
- uv pip install torch
- uv pip install openai
- uv pip install httpx
- (optional) uv pip install accelerate
- (optional) uv pip install bitsandbytes

Server Management
- Do not auto-start servers. Request permission for any server runs.

Plan Document Navigation Commands
Use these to read sections from implementation_plan.md:
# Read Overview section
sed -n '/[Overview]/,/[Types]/p' implementation_plan.md | cat
# Read Types section
sed -n '/[Types]/,/[Files]/p' implementation_plan.md | cat
# Read Files section
sed -n '/[Files]/,/[Functions]/p' implementation_plan.md | cat
# Read Functions section
sed -n '/[Functions]/,/[Classes]/p' implementation_plan.md | cat
# Read Classes section
sed -n '/[Classes]/,/[Dependencies]/p' implementation_plan.md | cat
# Read Dependencies section
sed -n '/[Dependencies]/,/[Testing]/p' implementation_plan.md | cat
# Read Testing section
sed -n '/[Testing]/,/[Implementation Order]/p' implementation_plan.md | cat
# Read Implementation Order section
sed -n '/[Implementation Order]/,$p' implementation_plan.md | cat
