# Documentation Refresh & Alignment Plan

Purpose: deliver an up-to-date, Diátaxis-aligned documentation set that reflects the current state of the system, enforces status sync, and documents our Context7 policy and MCP integration approach.

This plan is authoritative for docs operations. It complements .clinerules/documentation-rules.md, and references docs/explanations/project_lifecycle.md as the single source of truth for status/roadmap.

## Scope and Goals

- Align all docs to Diátaxis:
  - Tutorials: docs/tutorials/
  - How-to: docs/how-to/
  - Reference: docs/reference/
  - Explanations: docs/explanations/
- Enforce “status sync”: current_state, future_steps, cto_assessment mirror project_lifecycle.
- Modernize navigation and surface MCP adapter/integration docs.
- Clarify Context7 policy: research-only during authoring, not a Sphinx build-time dependency.
- Keep builds deterministic, offline-capable, and CI-safe.

## Source of Truth

- Update docs/explanations/project_lifecycle.md first.
- Reflect changes in:
  - docs/current_state.md
  - docs/future_steps.md
  - docs/cto_assessment.md
- Never diverge from lifecycle. Tests and endpoints must corroborate claims (TTD alignment).

## Action Items (Current Refresh)

1) Diátaxis structure
- Verify section indexes exist and list relevant pages:
  - getting-started/index.md
  - tutorials/index.md
  - how-to/index.md
  - reference/index.md
  - explanations/index.md
  - api/index.md (autosummary)
- Keep docs/index.rst landing page pointing to the 4 sections + API autosummary.
- Maintain test-required links:
  - final_summary
  - rag_implementation_plan

2) Status sync banners
- Add MyST note at top of each status doc:
  ```{note}
  Sync policy: This page mirrors docs/explanations/project_lifecycle.md. Update the lifecycle first, then reflect changes here.
  ```
- Applies to:
  - docs/current_state.md
  - docs/future_steps.md
  - docs/cto_assessment.md

3) MCP integration docs
- How-to: docs/how-to/ttm_mcp_integration.md
- Ensure it is listed in docs/how-to/index.md toctree.

4) Context7 documentation policy
- Explanations: docs/explanations/context7_docs_policy.md
  - Context7 used only during authoring via MCP (research, discovery, references)
  - Sphinx builds remain offline/deterministic
- Link it in explanations/index.md.

5) Navigation integrity
- explanations/index.md includes:
  - project_lifecycle
  - context7_docs_policy
  - docs_refresh_plan (this page)
  - other explanatory pages (architecture, plans, summaries)

6) Sphinx configuration hygiene
- docs/conf.py:
  - Use MyST and Furo
  - Intersphinx mapping’s second tuple element set to None (Sphinx 8)
  - Autodoc/autosummary config as per current setup

7) README affordances
- Add a “Project Documentation and Status” section:
  - Link to docs/explanations/project_lifecycle.md
  - Link the section indexes (Tutorials/How-to/Reference/Explanations/API)
  - Reiterate manual uv doc build/serve commands (per policy)

## PR Checklist (Docs)

Before merging:
- Structure
  - Content resides under the correct Diátaxis section
  - Section index updated and page appears in navigation
- Status Sync
  - project_lifecycle.md updated first when status/roadmap changed
  - current_state.md, future_steps.md, cto_assessment.md mirror lifecycle
- Accuracy
  - API paths and env vars validated against code
  - Pydantic v2 and FastAPI patterns consistent with current codebase
- Security & Ethics
  - No secrets; examples reference env usage
  - TTD: external API examples respect ethical usage guidance
- Build
  - Local build performed (manual commands below)
  - Visual check for broken links and nav placement

## TTD Alignment

- Claims must be backed by:
  - Passing tests
  - Verifiable endpoints
- Update test suites when adjusting feature claims.
- Prefer adding runnable curl examples (with safe defaults).

## Manual Commands (Author Runs)

Install (one-time):
- uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild

Build:
- uv run sphinx-build -b html docs docs/_build/html

Serve with reload:
- uv run sphinx-autobuild -b html docs docs/_build/html

## Risks and Mitigations

- Risk: Status drift between lifecycle and status pages
  - Mitigation: Sync note + PR checklist + policy in .clinerules
- Risk: Network-bound builds (Context7)
  - Mitigation: Strict policy; research-only via MCP; static content committed
- Risk: Doc claims outpace implementation
  - Mitigation: TTD gate; build docs only after tests confirm behavior

## Change Log (Docs Ops)

- 2025-08-31: Established this plan; added status sync notes; created Context7 policy doc; linked MCP how-to; validated Sphinx config for Sphinx 8.
