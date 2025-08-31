#!/usr/bin/env python3
"""
Readiness Validation Script — Core + MCP Adapter

This script verifies that the core RAG components and the new MCP adapter scaffolding
are present and documented. It follows the project's manual/external-run policy:
- No network calls
- No server start/stop
- No package installs

It checks for:
1) Core modules and docs (RAG, API, DB, monitoring)
2) gRPC/GraphQL facades
3) MCP adapter scaffolding (config/logging/schemas/clients/server)
4) Diataxis docs for MCP (tutorial/how-to/reference/explanations)
5) Cline Memory Bank initialization
6) Environment keys presence in current shell (best-effort)
"""

import os
from pathlib import Path


def status_ok(name: str, path: Path) -> str:
    return f"✅ {name} exists @ {path}"


def status_fail(name: str, path: Path) -> str:
    return f"❌ {name} not found @ {path}"


def check_paths(title: str, pairs: list[tuple[str, Path]]) -> bool:
    print(f"\n== {title} ==")
    all_ok = True
    for name, p in pairs:
        if p.exists():
            print(status_ok(name, p))
        else:
            print(status_fail(name, p))
            all_ok = False
    return all_ok


def check_env(title: str, keys: list[str]) -> None:
    print(f"\n== {title} ==")
    for k in keys:
        val = os.getenv(k)
        if val:
            print(f"✅ {k} present")
        else:
            print(f"⚠️  {k} not set (optional in dev; set it before runtime checks)")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]

    core_ok = check_paths(
        "Core (RAG/API/DB/Monitoring)",
        [
            ("RAG module", project_root / "src" / "rag"),
            ("RAG implementation plan", project_root / "docs" / "rag_implementation_plan.md"),
            ("Kick-off summary", project_root / "docs" / "rag_kickoff_summary.md"),
            ("Final summary", project_root / "docs" / "final_summary.md"),
            ("Database config", project_root / "src" / "database" / "config.py"),
            ("API main", project_root / "src" / "api" / "main.py"),
            ("Dashboard", project_root / "src" / "dashboard"),
            ("Monitoring", project_root / "src" / "api" / "monitoring.py"),
            ("RAG tests (unit)", project_root / "tests" / "unit" / "test_rag.py"),
        ],
    )

    surfaces_ok = check_paths(
        "Facades (gRPC/GraphQL)",
        [
            ("gRPC proto", project_root / "src" / "api" / "grpc" / "ttm_core.proto"),
            ("gRPC server scaffold", project_root / "src" / "api" / "grpc" / "grpc_server.py"),
            ("GraphQL schema", project_root / "src" / "api" / "graphql" / "schema.py"),
            ("gRPC runner helper", project_root / "scripts" / "run_grpc_server.py"),
        ],
    )

    mcp_ok = check_paths(
        "MCP Adapter Scaffolding",
        [
            ("MCP config", project_root / "tools" / "ttm-mcp" / "config.py"),
            ("MCP logging/audit", project_root / "tools" / "ttm-mcp" / "logging.py"),
            ("MCP schemas", project_root / "tools" / "ttm-mcp" / "schemas.py"),
            ("MCP gRPC client", project_root / "tools" / "ttm-mcp" / "adapters" / "grpc_client.py"),
            ("MCP server skeleton", project_root / "tools" / "ttm-mcp" / "server.py"),
        ],
    )

    docs_ok = check_paths(
        "Docs (Diataxis) — MCP",
        [
            ("Tutorial — MCP Quickstart", project_root / "docs" / "tutorials" / "ttm_mcp_quickstart.md"),
            ("How-to — MCP Readiness Checks", project_root / "docs" / "how-to" / "mcp_readiness_checks.md"),
            ("Reference — MCP Contracts", project_root / "docs" / "reference" / "mcp_contracts.md"),
            ("Explanations — MCP Adapter Philosophy", project_root / "docs" / "explanations" / "mcp_adapter_philosophy.md"),
        ],
    )

    memory_ok = check_paths(
        "Cline Memory Bank",
        [
            ("projectbrief.md", project_root / "memory-bank" / "projectbrief.md"),
            ("productContext.md", project_root / "memory-bank" / "productContext.md"),
            ("systemPatterns.md", project_root / "memory-bank" / "systemPatterns.md"),
            ("techContext.md", project_root / "memory-bank" / "techContext.md"),
            ("activeContext.md", project_root / "memory-bank" / "activeContext.md"),
            ("progress.md", project_root / "memory-bank" / "progress.md"),
        ],
    )

    check_env(
        "Environment (best-effort; set in your shell or .env)",
        [
            "TTM_API_URL",
            "TTM_API_KEY",
            "EMBED_MODEL_TH",
            "EMBED_MODEL_EN",
            "SEARCH_TOPK",
            "RAG_TOPK",
            "GRPC_HOST",
            "GRPC_PORT",
        ],
    )

    print("\n== Next Steps (manual) ==")
    print("- Generate gRPC stubs (once): see docs/tutorials/ttm_mcp_quickstart.md")
    print("- Start API: make dev")
    print("- Start gRPC server: uv run python scripts/run_grpc_server.py")
    print("- Follow How-to: MCP Readiness Checks")

    all_ok = core_ok and surfaces_ok and mcp_ok and docs_ok and memory_ok
    if all_ok:
        print("\n🎉 Readiness scaffolding present for Core + MCP adapter.")
        return 0
    else:
        print("\n❌ Missing components found. Address the items above and re-run.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
