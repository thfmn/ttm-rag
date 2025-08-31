"""
Integration test (optional): Dagster assets graph loads successfully.

This test is import-guarded and will be skipped automatically if Dagster
is not installed locally. It validates that our asset module can be imported
and returns a non-empty asset list without constructing a full job.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def test_dagster_assets_loadable():
    dagster = pytest.importorskip("dagster")
    from src.orchestration.assets.ingestion_assets import get_assets

    assets = get_assets()
    # Basic shape checks
    assert isinstance(assets, list)
    assert len(assets) >= 5  # raw_docs -> ... -> accepted_corpus
