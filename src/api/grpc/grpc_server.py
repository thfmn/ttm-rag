"""
gRPC server scaffolding for TTM Core services.

This is a thin facade over existing core modules (KG/Search/RAG). It intentionally
contains minimal logic and delegates to internal services. MCP will consume this
surface via a gRPC client (never importing core modules directly).

Notes:
- You must generate Python stubs from src/api/grpc/ttm_core.proto:
  Documented only, do not auto-run per project rules:
    uv pip install grpcio grpcio-tools
    python -m grpc_tools.protoc -I src/api/grpc --python_out=. --grpc_python_out=. src/api/grpc/ttm_core.proto

  Recommended layout for generated modules:
    ttm/core/v1/ttm_core_pb2.py
    ttm/core/v1/ttm_core_pb2_grpc.py

- This file provides no runnable entrypoint by default (servers are started manually).
"""

from __future__ import annotations

import logging
import os
from typing import Iterable

try:
    # Generated modules (paths depend on where protoc outputs files)
    # We assume a package layout "ttm/core/v1" for proto package "ttm.core.v1".
    from ttm.core.v1 import ttm_core_pb2 as pb2  # type: ignore
    from ttm.core.v1 import ttm_core_pb2_grpc as pb2_grpc  # type: ignore
except Exception as e:  # pragma: no cover - helpful message during scaffolding
    # Provide a friendly error to guide developers when stubs are missing
    raise RuntimeError(
        "Missing generated gRPC stubs for ttm.core.v1. "
        "Generate them from src/api/grpc/ttm_core.proto using grpc_tools.protoc.\n"
        "See header docstring in src/api/grpc/grpc_server.py for commands."
    ) from e


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class KGService(pb2_grpc.KGServiceServicer):
    """
    Read-only KG queries. Delegates into core KG/graph traversal components.
    """

    def GetHerb(self, request: pb2.GetHerbRequest, context) -> pb2.GetHerbResponse:
        # TODO: wire to core KG by herb id
        logger.info("KGService.GetHerb id=%s", request.id)
        # Minimal scaffold response (empty Herb)
        herb = pb2.Herb(id=request.id, names=pb2.NamePair(th="", en=""))
        return pb2.GetHerbResponse(herb=herb)

    def QueryPaths(self, request: pb2.QueryPathsRequest, context) -> pb2.QueryPathsResponse:
        # TODO: wire to core path queries
        logger.info(
            "KGService.QueryPaths start_type=%s start_id=%s pattern=%s max_depth=%s",
            request.start_type,
            request.start_id,
            request.pattern,
            request.max_depth,
        )
        return pb2.QueryPathsResponse(paths=[])


class SearchService(pb2_grpc.SearchServiceServicer):
    """
    Hybrid search (BM25 + vector). Delegates to retrieval core.
    """

    def HybridSearch(self, request: pb2.HybridSearchRequest, context) -> pb2.HybridSearchResponse:
        # TODO: wire to retrieval core (Thai-first; cross-lingual fallback)
        logger.info("SearchService.HybridSearch q=%s lang=%s top_k=%s", request.query, request.lang, request.top_k)
        # Minimal scaffold response (no hits)
        return pb2.HybridSearchResponse(hits=[])


class RagService(pb2_grpc.RagServiceServicer):
    """
    RAG answer generation with citations and scores. Enforce policy gates upstream.
    """

    def Answer(self, request: pb2.AnswerRequest, context) -> pb2.AnswerResponse:
        # TODO: wire to RAG pipeline (retrieve, policy gate, generate, cite)
        logger.info("RagService.Answer question=%s lang=%s top_k=%s", request.question, request.lang, request.top_k)
        return pb2.AnswerResponse(
            answer="",
            citations=[],
            retrieval_score=0.0,
            answer_conf=0.0,
        )


class EvalService(pb2_grpc.EvalServiceServicer):
    """
    Evaluation harness for retrieval/answer metrics.
    """

    def RunEval(self, request: pb2.RunEvalRequest, context) -> pb2.RunEvalResponse:
        # TODO: delegate to evaluation runner; compute metrics and report URI
        logger.info("EvalService.RunEval set=%s metrics=%s", request.set, list(request.metrics))
        return pb2.RunEvalResponse(metrics=[], report_uri="")


class IngestService(pb2_grpc.IngestServiceServicer):
    """
    Controlled ingest pipeline (dry-run first). Write path is sacred.
    """

    def RunIngest(self, request: pb2.RunIngestRequest, context) -> pb2.RunIngestResponse:
        # TODO: delegate to ingest pipeline; honor dry_run
        logger.info("IngestService.RunIngest dry_run=%s batch_size=%s", request.dry_run, len(request.batch))
        status = "queued" if not request.dry_run else "done"
        return pb2.RunIngestResponse(job_id="job-000", status=status, log_uri="")


def add_services(server) -> None:
    """
    Register all service servicers to a gRPC server instance.
    """
    pb2_grpc.add_KGServiceServicer_to_server(KGService(), server)
    pb2_grpc.add_SearchServiceServicer_to_server(SearchService(), server)
    pb2_grpc.add_RagServiceServicer_to_server(RagService(), server)
    pb2_grpc.add_EvalServiceServicer_to_server(EvalService(), server)
    pb2_grpc.add_IngestServiceServicer_to_server(IngestService(), server)


def get_listen_address() -> str:
    """
    Determine listen address from env or defaults.
    We do not start servers automatically; this is used by manual runners.
    """
    port = os.getenv("GRPC_PORT") or os.getenv("API_GRPC_PORT") or "50051"
    host = os.getenv("GRPC_HOST", "0.0.0.0")
    return f"{host}:{port}"


# No automatic __main__ – servers are started via explicit runner scripts/commands.
# Example manual runner (documented, not executed here):
#
#   import grpc
#   from concurrent import futures
#   from src.api.grpc.grpc_server import add_services, get_listen_address
#
#   server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
#   add_services(server)
#   server.add_insecure_port(get_listen_address())
#   server.start()
#   server.wait_for_termination()
#
# Prefer grpc.aio for async servers if needed in the future.
