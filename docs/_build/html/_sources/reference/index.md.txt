# Reference

Authoritative, factual reference for APIs, configuration, and models.

- API docs are auto-generated from source with autosummary + autodoc.
- Configuration reference and environment variables are collected here.

```{toctree}
:maxdepth: 2

../api/index
mcp_contracts
```

## Configuration

- Environment variables: see `.env.example` at project root and `docs/how-to/index.md` for database and deployment guidance.
- Make targets: see `Makefile` for developer workflow.
- Pyproject/Dependencies: see `pyproject.toml` for core dependencies and extras.

```{note}
If imports fail during API doc generation (e.g., heavy or optional dependencies), set `autodoc_mock_imports = [...]` in `docs/conf.py` to mock them at build time.
```
