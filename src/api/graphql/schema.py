"""
GraphQL read-only facade for TTM Core.

- Thin schema over core services (KG/Search/RAG)
- Mirrors gRPC types at a high level
- Keep logic minimal; delegate to internal modules or gRPC in the future

Install notes (manual, per project rules):
  uv pip install strawberry-graphql fastapi uvicorn

Example manual run (for local testing only):
  from strawberry.asgi import GraphQL
  from src.api.graphql.schema import schema
  app = GraphQL(schema)

Then mount this ASGI app into FastAPI or run a dedicated server.
"""

from __future__ import annotations

import os
from typing import List, Optional

import strawberry


@strawberry.type
class NamePair:
    th: str
    en: str


@strawberry.type
class Constituent:
    id: str
    name: str


@strawberry.type
class Indication:
    icdCode: str
    description: str


@strawberry.type
class Herb:
    id: str
    names: NamePair
    constituents: List[Constituent]
    indications: List[Indication]


@strawberry.type
class Hit:
    id: str
    type: str
    title: str
    snippet: str
    score: float
    source: str


# In a later step, resolvers will call gRPC clients. For now these stubs return empty or demo values.

@strawberry.type
class Query:
    @strawberry.field
    def herb(self, id: str) -> Herb:
        """
        Resolve a Herb by id (stub).
        Later: delegate to KGService.GetHerb via gRPC client.
        """
        return Herb(
            id=id,
            names=NamePair(th="", en=""),
            constituents=[],
            indications=[],
        )

    @strawberry.field
    def hybrid_search(self, query: str, lang: Optional[str] = "th", top_k: Optional[int] = 10) -> List[Hit]:
        """
        Hybrid search over BM25 + vectors (stub).
        Later: delegate to SearchService.HybridSearch via gRPC client.
        """
        _ = (query, lang, top_k)
        return []


schema = strawberry.Schema(query=Query)
