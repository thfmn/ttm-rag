#!/usr/bin/env python3
"""
Manual gRPC server runner for TTM Core (development helper).

Per project policy, servers are started manually by the user.
This script starts a basic gRPC server using the scaffolded services.

Prerequisites (run manually):
  - Generate gRPC stubs from src/api/grpc/ttm_core.proto:
      uv pip install grpcio grpcio-tools
      uv run python -m grpc_tools.protoc \
        -I src/api/grpc \
        --python_out=. \
        --grpc_python_out=. \
        src/api/grpc/ttm_core.proto
  - Ensure generated modules are importable on PYTHONPATH:
      export PYTHONPATH="$PYTHONPATH:$(pwd)"

Usage:
  uv run python scripts/run_grpc_server.py
  # Server listens on 0.0.0.0:50051 by default (override via GRPC_HOST/GRPC_PORT)

Notes:
  - The service implementations in src/api/grpc/grpc_server.py currently return
    stubbed data. Wire them to core modules incrementally.
"""

from __future__ import annotations

import os
import sys
from concurrent import futures

try:
    import grpc  # type: ignore
except Exception as e:
    sys.stderr.write(
        "Missing dependency 'grpcio'. Install it manually:\n  uv pip install grpcio\n"
    )
    raise

from src.api.grpc.grpc_server import add_services, get_listen_address  # type: ignore


def main() -> None:
    max_workers = int(os.getenv("GRPC_WORKERS", "8"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_services(server)
    addr = get_listen_address()
    server.add_insecure_port(addr)
    server.start()
    print(f"[gRPC] Listening on {addr} (workers={max_workers})")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[gRPC] Shutting down...")


if __name__ == "__main__":
    main()
