"""
Evaluation harness utilities (Phase 4).

This module provides helpers to:
- Build request payloads for the RAG API with optional agentic/policy flags
- Construct policy constraints from environment variables
- Construct headers from environment variables
- Compute simple retrieval KPIs from a list of API responses

Environment variables (optional):
- EVAL_TOP_K: int (default 5)
- EVAL_AGENTIC: "1"/"true"/"yes" to enable agentic path
- EVAL_USE_POLICY: "1"/"true"/"yes" to enable policy-based model routing
- EVAL_POLICY_ALLOW_EXTERNAL: "1"/"true"/"yes" to allow external provider models
- EVAL_POLICY_MAX_COST: float, maximum cost per call (e.g., 0.005)
- EVAL_MODEL: explicit adapter id (overrides policy)
- EVAL_USER_ROLE: header value for x-user-role (clinician|pharmacist|etc.)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import os


def _as_bool(val: Optional[str]) -> Optional[bool]:
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return None


def build_policy_constraints_from_env() -> Optional[Dict[str, Any]]:
    allow_external = _as_bool(os.getenv("EVAL_POLICY_ALLOW_EXTERNAL"))
    max_cost_raw = os.getenv("EVAL_POLICY_MAX_COST")
    max_cost: Optional[float]
    if max_cost_raw is None:
        max_cost = None
    else:
        try:
            max_cost = float(max_cost_raw)
        except Exception:
            max_cost = None

    constraints: Dict[str, Any] = {}
    if allow_external is not None:
        constraints["allow_external"] = allow_external
    if max_cost is not None:
        constraints["max_cost_per_call"] = max_cost
    return constraints if constraints else None


def build_headers_from_env() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    role = os.getenv("EVAL_USER_ROLE")
    if role:
        headers["x-user-role"] = role
    return headers


def build_payload(
    query: str,
    *,
    top_k: int = 5,
    return_context: bool = True,
    agentic: Optional[bool] = None,
    use_policy: Optional[bool] = None,
    policy_constraints: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
    filter_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "query": query,
        "top_k": int(top_k),
        "return_context": bool(return_context),
    }
    if model:
        payload["model"] = model
    if filter_metadata:
        payload["filter_metadata"] = filter_metadata
    if agentic is not None:
        payload["agentic"] = bool(agentic)
    if use_policy is not None:
        payload["use_policy"] = bool(use_policy)
    if policy_constraints:
        payload["policy_constraints"] = policy_constraints
    return payload


def build_payload_from_env(query: str) -> Dict[str, Any]:
    top_k = int(os.getenv("EVAL_TOP_K", "5"))
    agentic = _as_bool(os.getenv("EVAL_AGENTIC"))
    use_policy = _as_bool(os.getenv("EVAL_USE_POLICY"))
    constraints = build_policy_constraints_from_env()
    model = os.getenv("EVAL_MODEL") or None
    return build_payload(
        query,
        top_k=top_k,
        return_context=True,
        agentic=agentic,
        use_policy=use_policy,
        policy_constraints=constraints,
        model=model,
    )


def compute_kpis(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute simple retrieval KPIs from a list of API response dicts:
    - count
    - avg_retrieval_time
    - avg_num_results
    - pct_non_empty_context
    """
    if not results:
        return {
            "count": 0,
            "avg_retrieval_time": 0.0,
            "avg_num_results": 0.0,
            "pct_non_empty_context": 0.0,
        }

    n = len(results)
    times = []
    num_results = []
    non_empty = 0

    for r in results:
        try:
            times.append(float(r.get("retrieval_time", 0.0)))
        except Exception:
            times.append(0.0)
        try:
            num_results.append(int(r.get("num_results", 0)))
        except Exception:
            num_results.append(0)
        ctx = r.get("context") or []
        if isinstance(ctx, list) and len(ctx) > 0:
            non_empty += 1

    avg_time = sum(times) / n if n else 0.0
    avg_num = sum(num_results) / n if n else 0.0
    pct_non_empty = (non_empty / n) * 100.0 if n else 0.0

    return {
        "count": n,
        "avg_retrieval_time": float(avg_time),
        "avg_num_results": float(avg_num),
        "pct_non_empty_context": float(pct_non_empty),
    }
