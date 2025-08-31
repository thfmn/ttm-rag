"""
Orchestration package for Dagster-based ingestion & curation (Phase 2).

This package intentionally avoids importing Dagster at module import time.
Use src.orchestration.dagster_defs to access Dagster Definitions when
Dagster is installed, or src.orchestration.assets.ingestion_assets.get_assets()
to retrieve asset callables in a lazy-import fashion.
"""
__all__ = []
