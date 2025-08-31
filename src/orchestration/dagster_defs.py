"""
Dagster Definitions module for Phase 2 assets.

This file is import-guarded to avoid hard dependency on Dagster during normal
unit test runs. When Dagster is installed, it exposes a `defs` object that
Dagster can load via: uv run dagster dev -m src.orchestration.dagster_defs
"""

from __future__ import annotations

from typing import Any, List

def _ensure_dagster():
    try:
        import dagster as _dag  # noqa: F401
    except Exception as e:
        raise ImportError(
            "Dagster is required to use orchestration definitions.\n"
            "Install with:\n"
            "  uv pip install \"dagster>=1.7\" \"dagster-webserver>=1.7\""
        ) from e


def _load_defs():
    _ensure_dagster()
    from dagster import Definitions
    from src.orchestration.assets.ingestion_assets import get_assets

    assets = get_assets()
    return Definitions(assets=assets)


# Public object for Dagster CLI
try:
    defs = _load_defs()
except Exception as _e:  # pragma: no cover
    # Provide a helpful message if someone tries to import without Dagster installed
    defs = None
