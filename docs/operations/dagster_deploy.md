# Dagster Deployment Guide (Phase 2)

This guide describes how to run the optional Dagster asset graph for agentic continuous ingestion & curation. Dagster is not required for the core API and is import-guarded throughout the codebase.

The orchestration is designed per .clinerules:
- Dependencies are installed manually by you via uv.
- Servers are started manually by you.
- Documentation explicitly lists required dependencies and their purpose.

## What you get

- Asset graph (import-guarded) implementing:
  raw_docs -> redacted_docs -> labeled_docs -> scored_docs -> safe_docs -> accepted_corpus

- Sources:
  - Assets: src/orchestration/assets/ingestion_assets.py
  - Definitions: src/orchestration/dagster_defs.py (exposes `defs`)
  - Resources scaffold: src/orchestration/resources.py
  - Agents (stubs): src/agents/ingestion/*.py
  - Preprocessor wrappers: src/rag/pipeline_ext.py

## Install dependencies (manual)

Install Dagster only if you plan to use the orchestration:

- uv pip install "dagster>=1.7" "dagster-webserver>=1.7"

Rationale:
- dagster: asset-based orchestration and UI.
- dagster-webserver: local dev webserver.

Optional (if you plan to work with Postgres or add custom resources):
- uv pip install "psycopg2-binary>=2.9.0" "sqlalchemy>=2.0.0"

## Run the Dagster webserver

- make dagster-dev

This will:
- Launch Dagster dev server at http://localhost:3000
- Load asset definitions from src/orchestration/dagster_defs.py

If you install Dagster in a different environment, you may also run:

- uv run dagster dev -m src.orchestration.dagster_defs

## Configure input data

The assets expect an input JSON document array (e.g. PubMed fixture schema):

- Set INGEST_INPUT_JSON to point to a JSON file:
  - export INGEST_INPUT_JSON=data/raw/pubmed_ttm_100_articles.json

Each element should contain keys like:
- pmid, title, abstract, journal, publication_date: { "year": 2024 }, authors: [{ "name": "..." }]

The loader normalizes to:
- { id, content, metadata }

## Asset graph

- raw_docs: loads JSON via INGEST_INPUT_JSON
- redacted_docs: PDPA redaction (src/agents/ingestion/pdpa_agent.py), audit in metadata.audit.pdpa
- labeled_docs: taxonomy labels (metadata.taxonomy)
- scored_docs: quality score (metadata.quality)
- safe_docs: safety warnings (metadata.safety_warnings)
- accepted_corpus: committee decision (metadata.committee), returns accepted subset

You can materialize assets from the Dagster UI. The accepted_corpus output can be exported or wired to downstream indexing.

## Using the ingestion script with DAGSTER_MODE

The standard ingestion script can emit JSON lines to stdout instead of calling the API:

- export DAGSTER_MODE=1
- python scripts/ingestion/ingest_documents.py

Behavior:
- For each doc, the script prints a JSON object to stdout and does not call the POST /documents API.
- Useful for command-line pipelines or connecting to other tools.

## Resources (scaffold)

src/orchestration/resources.py provides helpers. To define Dagster resource definitions (optional):

- get_dagster_resource_defs() (import-guarded; requires Dagster)

Placeholders:
- DatabaseConfig and create_db_engine()
- ObjectStoreConfig and create_object_store_client()
- KMSConfig (env)
- ModelGatewayPolicy (default model id)

Future work:
- Replace placeholders with real clients/providers as needed (boto3, GCS, Vault).

## Development notes

- The agent stubs are dependency-light and safe for unit tests.
- Pydantic-AI agents can later replace stubs without changing call sites.
- PDPA-first design: redaction precedes labeling/scoring/safety to reduce risk exposure.
- All audit/curation info is attached to metadata to preserve provenance.

## Troubleshooting

- "ImportError: dagster not installed": Install Dagster via uv and retry.
- Asset loading fails due to bad JSON:
  - Validate INGEST_INPUT_JSON path.
  - Ensure file is a JSON array of objects.
- Postgres dependencies missing:
  - Install psycopg2-binary and confirm DATABASE_URL is set.
- Segmentation fault after tests (pytest passes):
  - This can be environment-related. Prefer running pytest directly:
    - pytest
    - pytest -k "unit"  (or use make test-integration for integration suite)
