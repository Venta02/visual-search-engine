"""Pydantic schemas for request and response validation."""

from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """A single search hit."""

    id: str | int
    score: float = Field(ge=-1.0, le=1.0)
    payload: dict[str, Any] = Field(default_factory=dict)


class TextSearchRequest(BaseModel):
    """Request to search by a text query."""

    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)
    score_threshold: float | None = Field(default=None, ge=-1.0, le=1.0)
    filters: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    """Standard search response."""

    query_type: str
    latency_ms: float
    total_results: int
    results: list[SearchResult]


class HealthResponse(BaseModel):
    """Service health response."""

    status: str
    version: str
    qdrant_reachable: bool
    redis_reachable: bool
    indexed_count: int


class IndexingResponse(BaseModel):
    """Response after triggering indexing."""

    job_id: str
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    detail: str | None = None
