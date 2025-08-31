# Reference — MCP Contracts (Tools and Resources)

Authoritative I/O specifications for the TTM‑MCP Expert Agent adapter. These contracts are stable, additive‑evolving, and map 1:1 to gRPC/GraphQL read surfaces. All tool calls return audit metadata.

## Conventions
- Canonical JSON for hashing (sorted keys)
- Thai‑first defaults, cross‑lingual fallback allowed
- No chain‑of‑thought; citations mandatory for answers
- Additive changes only (new optional fields)

## Resources

### kg://herb/{id}
- Description: Return a herb node with relations
- Response:
```json
{
  "id": "string",
  "names": {"th": "string", "en": "string"},
  "parts": ["string"],
  "constituents": [{"id":"string","name":"string"}],
  "indications": [{"icdCode":"string","description":"string"}],
  "sources": ["string"]
}
```

### paper://pmid/{id}
- Description: Curated PubMed/PMC study metadata
- Response:
```json
{
  "pmid": "string",
  "title": "string",
  "abstract": "string",
  "authors": ["string"],
  "journal": "string",
  "year": 2024,
  "links": ["string"]
}
```

## Tools

### tool.query_kg
- Purpose: Path queries (e.g., Herb→Constituent→Indication)
- Input:
```json
{
  "start": {"type": "herb|constituent|indication", "id": "string"},
  "pattern": "optional-string",
  "filters": {"optional": "object"},
  "max_depth": 3
}
```
- Output:
```json
{
  "paths": [
    [{"id":"H1","type":"herb","label":"..."}, {"id":"C9","type":"constituent","label":"..."}, {"id":"I05","type":"indication","label":"..."}]
  ],
  "audit": {"in_hash":"...","out_hash":"...","latency_ms":123,"seed":123,"status":"ok"}
}
```

### tool.hybrid_search
- Purpose: BM25 + vector (TH/EN)
- Input:
```json
{
  "query": "string",
  "lang": "th|en|auto",
  "filters": {"optional": "object"},
  "top_k": 10
}
```
- Output:
```json
{
  "hits": [
    {"id":"string","type":"herb|paper|chunk|...","title":"string","snippet":"string","score":0.87,"source":"string"}
  ],
  "audit": {"in_hash":"...","out_hash":"...","latency_ms":123,"seed":456,"status":"ok"}
}
```

### tool.rag_answer
- Purpose: Answer with citations & scores (policy‑gated)
- Input:
```json
{
  "question": "string",
  "lang": "th|en|auto",
  "retrieval": {"top_k": 5}
}
```
- Output:
```json
{
  "answer": "string",
  "citations": [{"id":"string","uri":"string","title":"string","span":"optional-string"}],
  "scores": {"retrieval": 0.80, "answer_conf": 0.72},
  "audit": {"in_hash":"...","out_hash":"...","latency_ms":345,"seed":789,"status":"ok"}
}
```
Policy: If citations < 3 or answer_conf < τ → withhold final answer; return citations and scores only.

### tool.find_contraindications
- Purpose: Check contraindications/interactions
- Input:
```json
{
  "herb_ids": ["string"],
  "formulation_ids": ["string"]
}
```
- Output:
```json
{
  "results": [
    {"entity_id":"string","type":"herb|formulation","contraindication":"string","evidence":"string","strength":"low|moderate|high"}
  ],
  "audit": {"in_hash":"...","out_hash":"...","latency_ms":120,"seed":321,"status":"ok"}
}
```

### tool.ingest.run
- Purpose: PDF→OCR→NER→Linking→KG (guarded write)
- Input:
```json
{
  "dry_run": true,
  "batch": [{"uri": "file:///path.pdf", "lang":"th|en|auto", "doc_type":"pdf"}],
  "ocr": {"provider":"string","params":{"k":"v"}},
  "ner": {"provider":"string","params":{"k":"v"}}
}
```
- Output:
```json
{
  "job_id": "string",
  "status": "queued|running|done|error",
  "log_uri": "string",
  "audit": {"in_hash":"...","out_hash":"...","latency_ms":987,"seed":654,"status":"ok"}
}
```

### tool.eval.run
- Purpose: Retrieval/answer eval (R@k, MRR, factuality)
- Input:
```json
{
  "set": "smoke|curated|custom",
  "metrics": ["R@k","MRR","factuality"],
  "params": {"optional": "object"}
}
```
- Output:
```json
{
  "metrics": [{"name":"R@10","value":0.83}, {"name":"factuality","value":0.92}],
  "report_uri": "string",
  "audit": {"in_hash":"...","out_hash":"...","latency_ms":231,"seed":159,"status":"ok"}
}
```

## Audit & Determinism
- in_hash: SHA‑256( canonical_json(input) )
- seed: first 8 bytes of in_hash (hex→int)
- out_hash: SHA‑256( canonical_json(output minus audit) )
- latency_ms: end‑start wall time
- status: ok|error; error details logged out‑of‑band

## Status Codes and Errors
- Tools return domain errors in a structured way:
```json
{"error": {"code":"INVALID_ARG","message":"top_k must be >0"},"audit":{...}}
```
- MCP transport errors are surfaced by the client; tool wrappers should avoid leaking internal stack traces.

## Versioning
- Contracts evolve additively; breaking changes require a new tool name or version suffix.
- Keep gRPC/GraphQL models aligned with these contracts; add contract tests.

Takeaway: Minimal, sharp, auditable shapes for reliable agent integration.
