# Getting Started

Cookbook-first onboarding to the Thai Traditional Medicine RAG Bot. Start here for a fast path to working docs and a local API.

## You&#39;ll learn
- How to install documentation dependencies with `uv`
- How to build and live-reload the Sphinx docs
- Where to find tutorials, how-tos, reference, and explanations

## Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) installed
- Git checkout of this repository

## Install doc dependencies (manual, one-time)

Run these commands manually (we never auto-install):

```bash
uv pip install sphinx myst-parser furo sphinx-design sphinx-copybutton sphinx-autodoc-typehints sphinx-sitemap sphinxext-opengraph sphinxcontrib-mermaid linkify-it-py sphinx-autobuild
```

Optional for notebooks:

```bash
# choose one
uv pip install myst-nb
# or
uv pip install jupyter-sphinx
```

## Build the docs

```bash
uv run sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser.

## Live reload during authoring

```bash
uv run sphinx-autobuild -b html docs docs/_build/html
```

This will watch the docs and rebuild on changes. Open the served URL it prints.

## Structure at a glance (Diátaxis)

- Tutorials: guided learning from zero to working
- How-to guides: task-focused recipes
- Reference: API/autosummary, configuration, and data models
- Explanations: architecture, design decisions, testing strategy

## Legacy content

We are migrating existing pages into the new structure. You can still access them via the section landing pages.

```{toctree}
:hidden:
:maxdepth: 2

../introduction
../project_overview
../development_setup
../onboarding
../onboarding_summary
```
