SHELL := /bin/bash

# Project name for docker compose
PROJECT := ttm-rag

# Compose base (run from this deploy/ directory)
COMPOSE_BASE := docker compose -p $(PROJECT) -f compose.yml

# Optional overrides (enable by setting HOST_OLLAMA=1, GPU=1, OTEL=1)
OVERRIDES :=
ifdef HOST_OLLAMA
OVERRIDES += -f compose.host-ollama.yml
endif
ifdef GPU
OVERRIDES += -f compose.gpu.yml
endif
ifdef OTEL
OVERRIDES += -f compose.otel.yml
endif

# Profiles to start (comma-separated)
# Defaults to full stack: Open WebUI + API + Ollama + Postgres
PROFILES ?= core,api,llm,db

# Convert PROFILES into repeated --profile flags
comma := ,
empty :=
space := $(empty) $(empty)
PROFILES_LIST := $(subst $(comma), ,$(PROFILES))
PROFILES_FLAGS := $(foreach p,$(PROFILES_LIST),--profile $(p))

# Ensure API gets the compose-friendly DB URL unless explicitly overridden
DATABASE_URL ?= postgresql://postgres:postgres@db:5432/ttm

# Final compose command with env override so we don't get tripped up by a top-level .env
COMPOSE := env DATABASE_URL=$(DATABASE_URL) $(COMPOSE_BASE) $(OVERRIDES)

# Health wait timeout (seconds)
TIMEOUT_SECS ?= 300

.PHONY: help
help:
	@echo "Deploy stack automation (docker compose + profiles)"
	@echo ""
	@echo "Usage:"
	@echo "  make up                # Start with PROFILES=$(PROFILES) (default full stack)"
	@echo "  make up-core           # Start Open WebUI only (expects host Ollama)"
	@echo "  make up-all            # Start everything incl. GPU + OTel"
	@echo "  make down              # Stop services (keep volumes)"
	@echo "  make destroy           # Stop and remove volumes"
	@echo "  make status            # Show services and health"
	@echo "  make logs              # Tail logs"
	@echo "  make health            # Print per-service health once"
	@echo "  make wait-health       # Wait with spinner until healthy (or timeout)"
	@echo "  make config            # Validate compose config"
	@echo "  make dry-run           # Preview actions without changing state"
	@echo "  make check-prereq      # Print manual uv install steps per repo rules"
	@echo ""
	@echo "Environment flags:"
	@echo "  HOST_OLLAMA=1          # Use host-installed Ollama (compose.host-ollama)"
	@echo "  GPU=1                  # Enable GPU override for Ollama container"
	@echo "  OTEL=1                 # Enable OpenTelemetry collector"
	@echo "  PROFILES=core,api,llm,db[,otel]   # Select profiles"
	@echo "  DATABASE_URL=...       # Override API DB URL (default is compose internal DB)"
	@echo ""

.PHONY: check-prereq
check-prereq:
	@echo "Run these manually (per .clinerules):"
	@echo "  uv pip install -r scripts/setup/requirements.txt"
	@echo "  uv pip install -e ."
	@echo "Ensure Docker Engine is running."

.PHONY: up
up:
	$(COMPOSE) $(PROFILES_FLAGS) up -d
	$(MAKE) wait-health

.PHONY: up-core
up-core:
	$(MAKE) HOST_OLLAMA=1 PROFILES=core up

.PHONY: up-all
up-all:
	$(MAKE) GPU=1 OTEL=1 PROFILES=core,api,llm,db,otel up

.PHONY: down
down:
	$(COMPOSE) down

.PHONY: destroy
destroy:
	$(COMPOSE) down -v

.PHONY: logs
logs:
	$(COMPOSE) logs -f --tail=200

.PHONY: status
status:
	$(COMPOSE) ps
	@echo ""
	@echo "Health:"
	@$(MAKE) --no-print-directory health

.PHONY: config
config:
	$(COMPOSE) config >/dev/null && echo "compose config OK"

.PHONY: dry-run
dry-run:
	$(COMPOSE) --dry-run up --build -d || true

.PHONY: health
health:
	@for s in $$($(COMPOSE) ps --services); do \
	  cid=$$($(COMPOSE) ps -q $$s); \
	  if [ -z "$$cid" ]; then \
	    printf "%-18s %s\n" $$s "inactive"; \
	  else \
	    st=$$( docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $$cid 2>/dev/null || echo "unknown" ); \
	    printf "%-18s %s\n" $$s $$st; \
	  fi; \
	done

.PHONY: wait-health
wait-health:
	@echo "Waiting for services to become healthy (timeout: $(TIMEOUT_SECS)s)..."
	@spin='|/-\\'; i=0; start=$$SECONDS; \
	while true; do \
	  all_ok=1; any_found=0; \
	  for s in $$($(COMPOSE) ps --services); do \
	    cid=$$($(COMPOSE) ps -q $$s); \
	    if [ -z "$$cid" ]; then continue; fi; \
	    any_found=1; \
	    st=$$( docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $$cid 2>/dev/null || echo "starting" ); \
	    if [ "$$st" != "healthy" ]; then all_ok=0; fi; \
	  done; \
	  if [ $$any_found -eq 0 ]; then \
	    printf "\rNo running services yet... "; \
	  elif [ $$all_ok -eq 1 ]; then \
	    echo "\nAll services healthy"; \
	    $(MAKE) --no-print-directory health; \
	    break; \
	  fi; \
	  if [ $$(( $$SECONDS - $$start )) -ge $(TIMEOUT_SECS) ]; then \
	    echo "\nTimeout waiting for health"; \
	    $(MAKE) --no-print-directory health; \
	    exit 1; \
	  fi; \
	  i=$$(( (i+1) % 4 )); printf "\rWaiting %s" "$${spin:$$i:1}"; sleep 2; \
	done
