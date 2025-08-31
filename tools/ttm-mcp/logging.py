"""
Audit logging and determinism utilities for the TTM MCP adapter.

- Canonical JSON via orjson with sorted keys
- Input/output hashing (SHA-256)
- Deterministic seed derived from input hash (first 8 bytes)
- NDJSON audit log at project root: audit.log

Install note (documented only):
  uv pip install orjson
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import orjson  # type: ignore
except Exception as e:  # pragma: no cover - guard missing optional dep in scaffolding
    raise RuntimeError(
        "Missing dependency 'orjson'. Install it manually:\n  uv pip install orjson"
    ) from e


AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "audit.log")


def canonical_json(obj: Any) -> bytes:
    """
    Return canonical JSON bytes with sorted keys for stable hashing.
    """
    return orjson.dumps(obj, option=orjson.OPT_SORT_KEYS)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive_seed_from_in_hash(in_hash: str) -> int:
    """
    Deterministic seed from first 8 bytes of input hash (hex -> int).
    """
    return int(in_hash[:16], 16)


@dataclass
class AuditMeta:
    in_hash: str
    out_hash: str
    seed: int
    latency_ms: int
    status: str = "ok"
    error: Optional[str] = None


def make_audit(
    tool_name: str,
    input_payload: Dict[str, Any],
    output_payload: Dict[str, Any],
    started_at_ns: int,
    status: str = "ok",
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Construct an audit record. Output hash excludes audit fields to avoid recursion.
    """
    now_ns = time.time_ns()
    latency_ms = int((now_ns - started_at_ns) / 1_000_000)

    in_hash = sha256_hex(canonical_json(input_payload))

    # Exclude 'audit' field from output when hashing
    output_copy = dict(output_payload)
    output_copy.pop("audit", None)
    out_hash = sha256_hex(canonical_json(output_copy))

    seed = derive_seed_from_in_hash(in_hash)

    record = {
        "ts": int(time.time()),
        "tool": tool_name,
        "in_hash": in_hash,
        "out_hash": out_hash,
        "seed": seed,
        "latency_ms": latency_ms,
        "status": status,
    }
    if error:
        record["error"] = error
    return record


def append_audit(record: Dict[str, Any]) -> None:
    """
    Append a single NDJSON line to the audit log.
    """
    line = orjson.dumps(record).decode("utf-8")
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
