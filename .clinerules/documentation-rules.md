# Documentation Rules — Thai Traditional Medicine RAG Bot

Purpose: define standards and operational rules for authoring, maintaining, and validating project documentation. These rules are binding for PRs that change features, architecture, or public behavior.

## 0) Scope

This policy covers:
- Sphinx docs under docs/
- README.md and top-level onboarding files
- Memory Bank sync for context
- Status/roadmap synchronization across status documents

This policy complements existing .clinerules:
- Package management: uv only, do not auto-install
- Servers/processes: started manually by the user
- Test-driven development preferred; ethical API usage

## 1) Diátaxis Structure (mandatory)

Use Diátaxis for all content:
- Tutorials (from zero to working): docs/tutorials/
- How-to guides (task recipes): docs/how-to/
- Reference (contracts, schemas, configuration, API): docs/reference/
- Explanations (architecture and rationale): docs/explanations/

Navigation:
- docs/index.rst is the single entry point and must only point to the 4 sections (+ API autosummary)
- Each section maintains an index file listing its content

## 2) Authoritative Status & Roadmap (single source of truth)

Authoritative file:
- docs/explanations/project_lifecycle.md

Documents that MUST remain consistent with it:
- docs/current_state.md (developer-facing snapshot)
- docs/future_steps.md (execution plan and next steps)
- docs/cto_assessment.md (stakeholder snapshot)

Required workflow for any change that affects status/roadmap:
1) Update docs/explanations/project_lifecycle.md FIRST
2) Reflect changes in docs/current_state.md, docs/future_steps.md, docs/cto_assessment.md
3) Rebuild docs (manually) and visually verify
4) Adjust tests and plans if the status changed (close the TTD loop)

## 3) Review Checklist (PR gate)

Before merging docs changes:
- Structure
  - Content placed in the correct Diátaxis section
  - Section index updated and docs build navigates to the page
- Status sync
  - project_lifecycle.md updated when relevant
  - current_state.md, future_steps.md, cto_assessment.md reflect lifecycle updates
- Accuracy
  - API paths, env vars, and commands verified
  - Version-specific notes for Pydantic v2, FastAPI patterns, and our adapters
- Security & ethics
  - No secrets in examples; mention env usage
  - Ethical API usage preserved in tests (rate limits, ≤3 results, ≥1s interval)

## 4) TTD Alignment

- Derive “what works” from tests first (unit/integration)
- Docs claims about capabilities must be supported by tests or verifiable endpoints
- When adding features:
  - Write or update tests
  - Update Reference (contracts/schemas)
  - Add/adjust How-to/Tutorials as needed
  - Update project_lifecycle.md and synchronized status docs

## 5) Commands & Local Build (manual, uv policy)

Do not auto-install. Provide commands for the user to run:
- Install docs deps (one time):
  - uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild
- Build docs:
  - uv run sphinx-build -b html docs docs/_build/html
- Serve with reload:
  - uv run sphinx-autobuild -b html docs docs/_build/html

## 6) Style & Quality

- Use MyST markdown features appropriately; prefer code fences with language hints
- Provide runnable curl examples for API when feasible
- Use Pydantic v2 idioms (ConfigDict, model_dump, field_validator)
- Reference gold standards (FastAPI, Pydantic, Diátaxis, MCP) where applicable

## 7) MCP & External Servers

- We DO NOT require running context7 locally; treat external MCP references as optional integrations
- If MCP tools are used to inform content, cite sources and summarize results; do not hard-depend on runtime MCP servers for docs build
- Context7/Sphinx policy: do not fetch external content at build time; Context7 is authoring-time only. Commit curated, static docs. See docs/explanations/context7_docs_policy.md
- Status sync enforcement: status pages must include the MyST note banner and mirror docs/explanations/project_lifecycle.md

## 8) Breaking Changes

- When removing or renaming important pages:
  - Update section index
  - Consider providing a redirect note or a “where did this content go?” pointer
- Record noteworthy decisions and changes in project_lifecycle.md Change Log

## 9) Docstrings & API

- Ensure docstrings for public classes/functions reflect actual behavior
- Keep FastAPI OpenAPI responses aligned (response_model, status_code, descriptions)

## 10) Validation Procedure (manual)

- Rebuild docs
- Scan critical pages:
  - Home (docs/index.rst)
  - Explanations index and project_lifecycle.md
  - Any updated How-to/Reference pages
- Click through section navigation and check for broken links
- If feasible, run a link checker (optional) against docs/_build/html

This file governs the documentation lifecycle. PRs that change docs must acknowledge these rules in the PR description with a short checklist referencing sections 2–4 and 10.
