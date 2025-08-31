# Context7 Usage Policy for Documentation

Purpose: clarify how we leverage Context7 (and MCP-based tooling) during authoring without making Sphinx builds network-bound or non-reproducible.

## Why not “Context7 for Sphinx” at build time?

- Reproducibility: Sphinx builds must be deterministic, offline-capable, and CI-friendly. Pulling remote content during `sphinx-build` would break this.
- Security and stability: Network fetches during builds introduce flakiness, rate limits, and secret-handling risks.
- Governance: Our documentation process must reflect tested, verified project behavior, not arbitrary remote content at build time.

Conclusion: We do not integrate Context7 as a Sphinx extension or runtime fetcher. Instead, we use it during authoring to research best practices and then commit curated, static docs.

## How we use Context7 (authoring workflow)

- Research-only via MCP: Authors can use an MCP server (e.g., Context7) during writing to discover, compare, and cite upstream docs (FastAPI, Pydantic, Diátaxis, MCP, etc.).
- Editorialization: Insights are distilled into our static pages (Tutorials, How-to, Reference, Explanations) with proper attribution in prose where appropriate.
- No network in builds: The Sphinx tree contains only committed sources. CI builds run `sphinx-build` without internet access.

## Where this shows up

- Explanations: Architectural rationale, patterns, and lifecycle are informed by research but captured as static markdown/RST (see `project_lifecycle.md`).
- How-to guides: Step recipes that reflect our tested environment and commands; references to external docs are links, not build-time fetches.
- Reference: Contracts and API docs are generated from our code and docstrings (autodoc/autosummary) — not from external sources.

## Author workflow checklist

1) Gather references via MCP tools (Context7 or otherwise) while authoring.
2) Update local docs files with curated content; include outbound links for background.
3) Run docs locally (manual):
   - Install (one-time):
     - uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild
   - Build:
     - uv run sphinx-build -b html docs docs/_build/html
   - Serve with reload:
     - uv run sphinx-autobuild -b html docs docs/_build/html
4) Commit static pages only. Do not add build-time network hooks.

## Status/roadmap source of truth

- Update docs/explanations/project_lifecycle.md first.
- Reflect changes in:
  - docs/current_state.md
  - docs/future_steps.md
  - docs/cto_assessment.md
- Rebuild and verify navigation and links.

## FAQs

- Q: Can we vendor snippets from external docs?
  - A: Keep excerpts minimal, attribute where appropriate, and prefer linking. Ensure licensing permits inclusion.
- Q: Can we add a Sphinx extension to fetch remote content?
  - A: Not for routine builds. If absolutely necessary, gate it behind a documented, opt-in target that is not used in CI or default builds.
- Q: How do we cite Context7 results?
  - A: Reference the upstream sources that Context7 surfaced (e.g., official project docs URLs). Context7 is a discovery mechanism, not the citation target.
