"""
gRPC client adapters for the TTM Core services.

This module provides thin, typed clients that the MCP server will use to
call the authoritative core surfaces. It intentionally carries no business
logic and only translates between Python objects and gRPC messages.

Requirements (document only; do not auto-install):
  uv pip install grpcio

Stub generation (document only):
  uv pip install grpcio-tools
  uv run python -m grpc_tools.protoc \
    -I src/api/grpc \
    --python_out=. \
    --grpc_python_out=. \
    src/api/grpc/ttm_core.proto

Generated modules are expected at:
  ttm/core/v1/ttm_core_pb2.py
  ttm/core/v1/ttm_core_pb2_grpc.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

try:
    import grpc  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing dependency 'grpcio'. Install it manually:\n  uv pip install grpcio"
    ) from e

try:
    # Generated gRPC modules (paths depend on your protoc output settings)
    from ttm.core.v1 import ttm_core_pb2 as pb2  # type: ignore
    from ttm.core.v1 import ttm_core_pb2_grpc as pb2_grpc  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing generated stubs for ttm.core.v1. Generate from src/api/grpc/ttm_core.proto.\n"
        "See tools/ttm-mcp/adapters/grpc_client.py docstring for commands."
    ) from e


@dataclass
class GRPCConfig:
    host: str = "0.0.0.0"
    port: int = 50051
    # TODO: TLS / credentials when needed


class TTMGrpcClients:
    """
    Connection manager for core service stubs.
    Usage:
        clients = TTMGrpcClients.from_env()
        hits = clients.search.hybrid_search("ฟ้าทะลายโจร", lang="th", top_k=10)
    """

    def __init__(self, channel: grpc.Channel) -> None:
        self._channel = channel
        self.kg = KGServiceClient(pb2_grpc.KGServiceStub(channel))
        self.search = SearchServiceClient(pb2_grpc.SearchServiceStub(channel))
        self.rag = RagServiceClient(pb2_grpc.RagServiceStub(channel))
        self.eval = EvalServiceClient(pb2_grpc.EvalServiceStub(channel))
        self.ingest = IngestServiceClient(pb2_grpc.IngestServiceStub(channel))

    @classmethod
    def connect(cls, host: str, port: int) -> "TTMGrpcClients":
        target = f"{host}:{port}"
        channel = grpc.insecure_channel(target)
        return cls(channel)

    @classmethod
    def from_env(cls) -> "TTMGrpcClients":
        import os

        host = os.getenv("GRPC_HOST", "0.0.0.0")
        port = int(os.getenv("GRPC_PORT") or os.getenv("API_GRPC_PORT") or "50051")
        return cls.connect(host, port)


class KGServiceClient:
    def __init__(self, stub: pb2_grpc.KGServiceStub) -> None:
        self._stub = stub

    def get_herb(self, herb_id: str) -> pb2.GetHerbResponse:
        req = pb2.GetHerbRequest(id=herb_id)
        return self._stub.GetHerb(req)

    def query_paths(
        self, start_type: str, start_id: str, pattern: Optional[str] = None, max_depth: int = 3
    ) -> pb2.QueryPathsResponse:
        req = pb2.QueryPathsRequest(
            start_type=start_type,
            start_id=start_id,
            pattern=pattern or "",
            max_depth=max_depth,
        )
        return self._stub.QueryPaths(req)


class SearchServiceClient:
    def __init__(self, stub: pb2_grpc.SearchServiceStub) -> None:
        self._stub = stub

    def hybrid_search(self, query: str, lang: str = "th", top_k: int = 10) -> pb2.HybridSearchResponse:
        req = pb2.HybridSearchRequest(query=query, lang=lang, top_k=top_k)
        return self._stub.HybridSearch(req)


class RagServiceClient:
    def __init__(self, stub: pb2_grpc.RagServiceStub) -> None:
        self._stub = stub

    def answer(self, question: str, lang: str = "th", top_k: int = 5) -> pb2.AnswerResponse:
        req = pb2.AnswerRequest(question=question, lang=lang, top_k=top_k)
        return self._stub.Answer(req)


class EvalServiceClient:
    def __init__(self, stub: pb2_grpc.EvalServiceStub) -> None:
        self._stub = stub

    def run_eval(self, set_name: str, metrics: List[str], params_json: str = "") -> pb2.RunEvalResponse:
        req = pb2.RunEvalRequest(set=set_name, metrics=metrics, params_json=params_json)
        return self._stub.RunEval(req)


class IngestServiceClient:
    def __init__(self, stub: pb2_grpc.IngestServiceStub) -> None:
        self._stub = stub

    def run_ingest(
        self,
        dry_run: bool,
        batch: Optional[List[pb2.IngestItem]] = None,
        ocr_json: str = "",
        ner_json: str = "",
    ) -> pb2.RunIngestResponse:
        req = pb2.RunIngestRequest(
            dry_run=dry_run,
            batch=batch or [],
            ocr_json=ocr_json,
            ner_json=ner_json,
        )
        return self._stub.RunIngest(req)
