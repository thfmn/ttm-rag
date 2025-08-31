"""
Unit test: scripts/ingestion/ingest_documents.py in DAGSTER_MODE should
emit JSON lines to stdout instead of performing HTTP POST requests.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import builtins


def test_ingest_documents_emits_json_when_dagster_mode(monkeypatch, tmp_path, capsys):
    # Prepare a tiny input file
    docs: List[Dict[str, Any]] = [
        {
            "pmid": "PMID-1",
            "title": "Herbal remedy overview",
            "abstract": "A brief abstract.",
            "journal": "JTTM",
            "publication_date": {"year": 2024},
            "authors": [{"name": "Author A"}],
        },
        {
            "pmid": "PMID-2",
            "title": "Thai herb dosage and preparation",
            "abstract": "Dosage info and preparation steps.",
            "journal": "JTTM",
            "publication_date": {"year": 2023},
            "authors": [{"name": "Author B"}],
        },
    ]
    input_path = tmp_path / "mini_docs.json"
    input_path.write_text(json.dumps(docs), encoding="utf-8")

    # Import target module
    import importlib
    mod = importlib.import_module("scripts.ingestion.ingest_documents")

    # Point the module to our temporary input file
    monkeypatch.setattr(mod, "INPUT_FILE", input_path)

    # Ensure requests.post is not called in DAGSTER_MODE
    called = {"count": 0}

    def fake_post(*_a, **_k):
        called["count"] += 1
        raise AssertionError("requests.post should not be called in DAGSTER_MODE")

    monkeypatch.setattr(mod.requests, "post", fake_post)

    # Enable DAGSTER_MODE
    monkeypatch.setenv("DAGSTER_MODE", "1")

    # Run the main()
    mod.main()
    out = capsys.readouterr().out

    # Validate output contains emitted JSON lines and no POST
    assert called["count"] == 0
    assert "DAGSTER_MODE=1" in out

    # Extract at least one JSON line (a line that looks like a JSON object)
    json_lines = [line for line in out.splitlines() if line.startswith("{") and line.endswith("}")]
    assert len(json_lines) >= 1
    parsed = json.loads(json_lines[0])
    assert parsed["id"] in {"PMID-1", "PMID-2"}
    assert isinstance(parsed.get("metadata"), dict)
