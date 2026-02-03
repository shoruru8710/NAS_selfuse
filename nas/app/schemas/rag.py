"""Pydantic schemas for RAG endpoints."""

from pydantic import BaseModel


class RAGSearchRequest(BaseModel):
    q: str
    top_k: int = 20


class SnippetResult(BaseModel):
    chunk_id: str
    text_excerpt: str
    source_hint: str


class SearchResultItem(BaseModel):
    file_id: str
    score: float
    snippets: list[SnippetResult]


class RAGSearchResponse(BaseModel):
    results: list[SearchResultItem]
    answer: str | None = None
