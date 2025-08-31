"""
TTM MCP Adapter — Server Skeleton (transport-agnostic)

Purpose:
- Provide thin, auditable tool/resource handlers that call TTM Core via gRPC
- Keep logic minimal; enforce policy gates outside or in core as needed
- Be transport-agnostic: you can wrap these handlers with any MCP server runtime

Transport options (documented only; do not auto-install here):
- Python MCP (modelcontextprotocol) stdio server
- FastMCP (third-party convenience wrapper)
- Dockerized entrypoint (see docs/config snippets)

Dependencies (document only):
  uv pip install pydantic orjson grpcio

Generated stubs (document only):
  uv pip install grpcio-tools
  uv run python -m grpc_tools.protoc \
    -I src/api/grpc \
    --python_out=. \
    --grpc_python_out=. \
    src/api/grpc/ttm_core.proto

How to use this skeleton:
- Import build_handlers() to get a registry dict of tool/resource callables.
- Bind them to your chosen MCP runtime (stdio/http) and wire input/output schemas.

This file intentionally does not import any MCP runtime to avoid hard deps.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from .config import MCPConfig, load_config
from .logging import make_audit, append_audit
from .schemas import (
    Citation,
    ContraResult,
    ContraindicationsInput,
    ContraindicationsOutput,
    EvalInput,
    EvalOutput,
    HerbResource,
    Hit,
    IngestInput,
    IngestItem,
    IngestOutput,
    KGNode,
    Metric,
    PaperResource,
    QueryKGInput,
    QueryKGOutput,
    RagAnswerInput,
    RagAnswerOutput,
    RetrievalParams,
    SearchInput,
    SearchOutput,
    StartNode,
)
from .adapters.grpc_client import TTMGrpcClients


class ToolError(Exception):
    pass


def _now_ns() -> int:
    return time.time_ns()


def _ensure_clients(cfg: MCPConfig) -> TTMGrpcClients:
    # Adapter must call gRPC; do not import core modules directly.
    return TTMGrpcClients.connect(cfg.grpc_host, cfg.grpc_port)


# -------------- Resources --------------

def get_kg_herb(cfg: MCPConfig, herb_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Resource: kg://herb/{id}
    Returns (payload, audit) pair
    """
    started = _now_ns()
    input_payload = {"uri": f"kg://herb/{herb_id}"}

    clients = _ensure_clients(cfg)
    # gRPC response is currently stubbed in grpc_server; wire to real core later
    resp = clients.kg.get_herb(herb_id=herb_id)

    data = HerbResource(
        id=resp.herb.id,
        # names/constituents/indications are stubbed empty in scaffold
    ).model_dump()

    payload = data
    audit = make_audit("resource.kg.herb", input_payload, payload, started)
    append_audit(audit)
    return payload, audit


def get_paper_pmid(cfg: MCPConfig, pmid: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Resource: paper://pmid/{id}
    Returns (payload, audit) pair
    """
    started = _now_ns()
    input_payload = {"uri": f"paper://pmid/{pmid}"}

    # Placeholder: integrate with core paper metadata (when available)
    data = PaperResource(pmid=pmid, title="", abstract=None, authors=[], journal=None, year=None, links=[]).model_dump()

    payload = data
    audit = make_audit("resource.paper.pmid", input_payload, payload, started)
    append_audit(audit)
    return payload, audit


# -------------- Tools --------------

def tool_query_kg(cfg: MCPConfig, params: QueryKGInput) -> Dict[str, Any]:
    """
    tool.query_kg — Path queries (Herb→Constituent→Indication)
    """
    started = _now_ns()
    input_payload = params.model_dump()

    clients = _ensure_clients(cfg)
    resp = clients.kg.query_paths(
        start_type=params.start.type,
        start_id=params.start.id,
        pattern=params.pattern or "",
        max_depth=params.max_depth,
    )

    paths: List[List[KGNode]] = []
    for p in resp.paths:
        seq: List[KGNode] = []
        for n in p.nodes:
            seq.append(KGNode(id=n.id, type=n.type, label=getattr(n, "label", "")))
        paths.append(seq)

    payload = QueryKGOutput(paths=paths, audit={}).model_dump()
    audit = make_audit("tool.query_kg", input_payload, payload, started)
    payload["audit"] = audit
    append_audit(audit)
    return payload


def tool_hybrid_search(cfg: MCPConfig, params: SearchInput) -> Dict[str, Any]:
    """
    tool.hybrid_search — BM25 + vector (Thai/English)
    """
    started = _now_ns()
    input_payload = params.model_dump()

    clients = _ensure_clients(cfg)
    resp = clients.search.hybrid_search(query=params.query, lang=params.lang, top_k=params.top_k)

    hits: List[Hit] = []
    for h in resp.hits:
        hits.append(Hit(id=h.id, type=h.type, title=h.title, snippet=h.snippet, score=h.score, source=h.source))

    payload = SearchOutput(hits=hits, audit={}).model_dump()
    audit = make_audit("tool.hybrid_search", input_payload, payload, started)
    payload["audit"] = audit
    append_audit(audit)
    return payload


def tool_rag_answer(cfg: MCPConfig, params: RagAnswerInput) -> Dict[str, Any]:
    """
    tool.rag_answer — Answer with citations and scores (policy-gated upstream)
    """
    started = _now_ns()
    input_payload = params.model_dump()

    top_k = (params.retrieval.top_k if params.retrieval else None) or cfg.rag_topk

    clients = _ensure_clients(cfg)
    resp = clients.rag.answer(question=params.question, lang=params.lang, top_k=top_k)

    citations: List[Citation] = []
    for c in resp.citations:
        citations.append(Citation(id=c.id, uri=c.uri, title=c.title, span=getattr(c, "span", None)))

    payload = RagAnswerOutput(
        answer=resp.answer,
        citations=citations,
        scores={"retrieval": resp.retrieval_score, "answer_conf": resp.answer_conf},  # type: ignore
        audit={},
    ).model_dump()
    audit = make_audit("tool.rag_answer", input_payload, payload, started)
    payload["audit"] = audit
    append_audit(audit)
    return payload


def tool_find_contraindications(cfg: MCPConfig, params: ContraindicationsInput) -> Dict[str, Any]:
    """
    tool.find_contraindications — Placeholder (wire to core once implemented)
    """
    started = _now_ns()
    input_payload = params.model_dump()

    # Placeholder empty result until core support exists
    payload = ContraindicationsOutput(results=[], audit={}).model_dump()
    audit = make_audit("tool.find_contraindications", input_payload, payload, started)
    payload["audit"] = audit
    append_audit(audit)
    return payload


def tool_ingest_run(cfg: MCPConfig, params: IngestInput) -> Dict[str, Any]:
    """
    tool.ingest.run — Guarded ingest. Dry-run first.
    """
    started = _now_ns()
    input_payload = params.model_dump()

    clients = _ensure_clients(cfg)
    batch_items = []
    for item in params.batch:
        batch_items.append(
            # Build gRPC IngestItem
            # Note: generated types are under pb2, but we keep this skeleton transport-agnostic.
            # When wiring, use: pb2.IngestItem(uri=item.uri, lang=item.lang, doc_type=item.doc_type)
            # Here we pass None; grpc client will expect proper pb2 items when fully wired.
            # Placeholder: leave empty list to keep scaffold compilable without stubs at import time.
        )

    resp = clients.ingest.run_ingest(dry_run=params.dry_run, batch=[])  # wire real batch later

    payload = IngestOutput(job_id=resp.job_id, status=resp.status, log_uri=getattr(resp, "log_uri", None), audit={}).model_dump()
    audit = make_audit("tool.ingest.run", input_payload, payload, started)
    payload["audit"] = audit
    append_audit(audit)
    return payload


def tool_eval_run(cfg: MCPConfig, params: EvalInput) -> Dict[str, Any]:
    """
    tool.eval.run — Retrieval/answer evaluation
    """
    started = _now_ns()
    input_payload = params.model_dump()

    clients = _ensure_clients(cfg)
    # Pass params_json as a simple stringified object when needed
    resp = clients.eval.run_eval(set_name=params.set, metrics=[*params.metrics], params_json="")

    metrics: List[Metric] = []
    for m in resp.metrics:
        metrics.append(Metric(name=m.name, value=m.value))

    payload = EvalOutput(metrics=metrics, report_uri=getattr(resp, "report_uri", None), audit={}).model_dump()
    audit = make_audit("tool.eval.run", input_payload, payload, started)
    payload["audit"] = audit
    append_audit(audit)
    return payload


# -------------- Registry --------------

def build_handlers() -> Dict[str, Any]:
    """
    Return a registry mapping tool/resource identifiers to callables accepting (cfg, params/ids).
    MCP runtime should:
      - parse env into MCPConfig()
      - validate inputs with Pydantic models
      - call the appropriate handler
      - return JSON with embedded 'audit'
    """
    return {
        # Resources (use helper signatures that return (payload, audit))
        "resource:kg:herb": get_kg_herb,          # call with (cfg, herb_id)
        "resource:paper:pmid": get_paper_pmid,    # call with (cfg, pmid)

        # Tools
        "tool.query_kg": tool_query_kg,                         # (cfg, QueryKGInput)
        "tool.hybrid_search": tool_hybrid_search,               # (cfg, SearchInput)
        "tool.rag_answer": tool_rag_answer,                     # (cfg, RagAnswerInput)
        "tool.find_contraindications": tool_find_contraindications,  # (cfg, ContraindicationsInput)
        "tool.ingest.run": tool_ingest_run,                     # (cfg, IngestInput)
        "tool.eval.run": tool_eval_run,                         # (cfg, EvalInput)
    }


# -------------- Example binding (pseudo-code) --------------
# The following illustrates how a runtime could invoke handlers; it does not run by default.

def example_invoke(tool_name: str, raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example dispatcher (not used by MCP runtime directly).
    """
    cfg = load_config()
    handlers = build_handlers()

    if tool_name not in handlers:
        raise ToolError(f"Unknown tool: {tool_name}")

    fn = handlers[tool_name]

    # Minimal parse by tool name; real runtime should route via schema binding
    if tool_name == "tool.query_kg":
        return fn(cfg, QueryKGInput(**raw_input))
    if tool_name == "tool.hybrid_search":
        return fn(cfg, SearchInput(**raw_input))
    if tool_name == "tool.rag_answer":
        return fn(cfg, RagAnswerInput(**raw_input))
    if tool_name == "tool.find_contraindications":
        return fn(cfg, ContraindicationsInput(**raw_input))
    if tool_name == "tool.ingest.run":
        return fn(cfg, IngestInput(**raw_input))
    if tool_name == "tool.eval.run":
        return fn(cfg, EvalInput(**raw_input))

    # Resources (not typically dispatched by tool_name in real MCP)
    raise ToolError(f"Dispatcher does not handle: {tool_name}")
