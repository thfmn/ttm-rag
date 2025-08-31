# Stack deployment (Docker Compose + Makefile)

This repository includes a modular, production-friendly Docker Compose stack with health checks and a Makefile wrapper that adds simple progress/wait-for-health commands. It supports both:
- Containerized Ollama (profile: llm)
- Host-installed Ollama (override: compose.host-ollama.yml)
- Optional PostgreSQL (profile: db)
- Open WebUI (profile: core)
- Your FastAPI RAG API (profile: api)
- Optional OpenTelemetry Collector (profile: otel)

The design aims to be:
- Simple to run (one-liners)
- Modular (opt-in services via profiles)
- Secure-by-default (non-root where possible, dropped caps, no-new-privileges)
- Observable (health checks, status, optional OTel collector)

## Prerequisites

- Docker Engine (Linux). For GPU, install NVIDIA drivers + Docker GPU runtime.
- uv (Python package manager) installed on host (for local development).
- Optional: Ollama installed on host if you prefer not to run the Ollama container.

Per project rules, do not auto-install anything. Run these manually if you haven't:
- uv pip install -r scripts/setup/requirements.txt
- uv pip install -e .

## Files

- deploy/compose.yml
  - Services: open-webui (core), api (FastAPI), db (Postgres), ollama (LLM)
  - Strict health checks and least-privilege defaults
- deploy/compose.host-ollama.yml
  - Override to use host-installed Ollama (http://host.docker.internal:11434)
- deploy/compose.gpu.yml
  - NVIDIA GPU pass-through for ollama container
- deploy/compose.otel.yml and docker/otel-collector-config.yaml
  - Optional OTel collector to receive OTLP traces/metrics/logs
- deploy/Makefile
  - Orchestration wrapper with progress spinner and health/status commands
- docker/Dockerfile.api
  - Slim uv-based FastAPI image (non-root), runs src.api.main:app on :8005

## Environment variables

Create and edit .env from .env.example. The deployment uses only a small subset:
- WEBUI_SECRET_KEY (change the default)
- OPEN_WEBUI_PORT (default 8080)
- API_PORT (default 8005)
- OLLAMA_PORT (default 11434)
- TZ (default UTC)
- Optional GPU vars: GPU_COUNT (default all), OLLAMA_GPU_DRIVER (default nvidia)

Note: The Compose stack uses an internal Postgres with POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB defaulted to postgres/postgres/ttm inside the stack. Your application DATABASE_URL is overridden for Compose runs by deploy/Makefile so it targets the stack’s DB unless you set DATABASE_URL explicitly.

## Quick start commands

All commands are run from the deploy/ directory (or use make -C deploy ...).

1) Validate your Compose configuration:
- make config

2) Start full stack (Open WebUI + API + Ollama + Postgres):
- make up
- This is equivalent to: docker compose -p ttm-rag -f compose.yml --profile core --profile api --profile llm --profile db up -d
- Wait for health:
  - The Makefile automatically waits and prints per-service health.

3) Open the UI:
- Open WebUI at http://localhost:8080
- API at http://localhost:8005/docs

4) Tail logs or check status:
- make logs
- make status

5) Stop the stack:
- make down
- Remove volumes (data loss): make destroy

## Host-installed Ollama

If you already run Ollama on the host (default port 11434) and only want Open WebUI:

- make up-core (equivalent to HOST_OLLAMA=1 PROFILES=core make up)
- Open http://localhost:8080
- Open WebUI is configured to call http://host.docker.internal:11434

To run Open WebUI + your API while using host Ollama:
- HOST_OLLAMA=1 PROFILES=core,api,db make up
- API docs: http://localhost:8005/docs

## GPU

To enable GPU for the containerized Ollama service:
- GPU=1 make up
- This includes deploy/compose.gpu.yml and requests NVIDIA GPUs for the ollama container.

Environment hints:
- OLLAMA_GPU_DRIVER=nvidia
- GPU_COUNT=all (or a number)

## OpenTelemetry (optional)

To run an OTel collector (logging exporter by default):
- OTEL=1 PROFILES=core,api,llm,db,otel make up
- OTLP HTTP: 4318, OTLP gRPC: 4317
- The current collector config logs received telemetry to stdout; wire to your backend later.

## Health checks and progress

- Open WebUI: GET /health should return {"status": true}
  - Health check unsets http_proxy/https_proxy to avoid proxy issues inside the container.
- API: GET /health returns status JSON
- Ollama (container): GET /api/tags
- DB: pg_isready

The Makefile’s wait-health target prints a spinner and times out (default 300s).

## Configuration and ports

Edit .env to override defaults:
- OPEN_WEBUI_PORT=8080
- API_PORT=8005
- OLLAMA_PORT=11434
- WEBUI_SECRET_KEY=change-me
- TZ=UTC

Compose project name: ttm-rag.

## Security defaults

- Containers run with no-new-privileges and dropped capabilities where possible.
- Open WebUI uses WEBUI_SECRET_KEY; change it.
- Avoid placing secrets in Compose files; use environment variables or secret files.

## Troubleshooting

- Open WebUI unhealthy with proxies:
  - The healthcheck unsets proxies. If your environment injects proxies, ensure no proxy is required for localhost calls.
- Linux host connectivity from containers:
  - The stack maps host.docker.internal to host gateway so containers can reach host services when needed.
- Port conflicts:
  - Adjust OPEN_WEBUI_PORT, API_PORT, OLLAMA_PORT in .env.
- Validate your compose:
  - make config
- Dry run:
  - make dry-run (shows what Compose would do)

## Using Docker CLI directly (no Makefile)

Full stack:
- docker compose -p ttm-rag -f deploy/compose.yml --profile core --profile api --profile llm --profile db up -d

Host Ollama + Open WebUI only:
- docker compose -p ttm-rag -f deploy/compose.yml -f deploy/compose.host-ollama.yml --profile core up -d

GPU:
- add -f deploy/compose.gpu.yml and ensure your system supports NVIDIA containers.

## Next steps

- If you need HTTPS and public exposure, add a reverse proxy (Caddy/NGINX) in a new profile (edge) with TLS certificates.
- For Kubernetes later, start from: docker compose bridge convert -o k8s and refine probes/resources/secrets/ingress.
