"""Search API routes.

Endpoints:
- POST /search/text: text-to-image search
- POST /search/image: image-to-image search (multipart upload)
"""

import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from src.api.dependencies import get_embedder, get_search_service
from src.core.logging import get_logger
from src.core.metrics import (
    search_latency_seconds,
    search_requests_total,
)
from src.models import SearchResponse, SearchResult, TextSearchRequest
from src.services.embedding import SigLIPEmbedder
from src.services.search import QdrantSearchService

logger = get_logger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/text", response_model=SearchResponse)
async def search_by_text(
    request: TextSearchRequest,
    embedder: SigLIPEmbedder = Depends(get_embedder),
    search: QdrantSearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search images by a text query.

    The query is encoded into the shared embedding space, then nearest
    neighbors are retrieved from the vector database.
    """
    start = time.perf_counter()
    query_type = "text"

    try:
        query_vector = embedder.embed_text(request.query)
        hits = search.search(
            query_vector=query_vector,
            limit=request.limit,
            score_threshold=request.score_threshold,
            filters=request.filters,
        )
    except Exception as e:
        search_requests_total.labels(query_type=query_type, status="error").inc()
        logger.error("Text search failed", query=request.query, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again.",
        ) from e

    elapsed = time.perf_counter() - start
    search_latency_seconds.labels(query_type=query_type).observe(elapsed)
    search_requests_total.labels(query_type=query_type, status="success").inc()

    return SearchResponse(
        query_type=query_type,
        latency_ms=round(elapsed * 1000, 2),
        total_results=len(hits),
        results=[SearchResult(**hit) for hit in hits],
    )


@router.post("/image", response_model=SearchResponse)
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = 10,
    embedder: SigLIPEmbedder = Depends(get_embedder),
    search: QdrantSearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search by uploading a query image.

    The image is encoded with SigLIP and used to retrieve visually similar
    images from the index.
    """
    start = time.perf_counter()
    query_type = "image"

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be between 1 and 100",
        )

    try:
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB cap
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image exceeds 10MB limit",
            )
        from io import BytesIO

        image = Image.open(BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError as e:
        search_requests_total.labels(query_type=query_type, status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image",
        ) from e

    try:
        query_vector = embedder.embed_image(image)
        hits = search.search(query_vector=query_vector, limit=limit)
    except Exception as e:
        search_requests_total.labels(query_type=query_type, status="error").inc()
        logger.error("Image search failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again.",
        ) from e

    elapsed = time.perf_counter() - start
    search_latency_seconds.labels(query_type=query_type).observe(elapsed)
    search_requests_total.labels(query_type=query_type, status="success").inc()

    return SearchResponse(
        query_type=query_type,
        latency_ms=round(elapsed * 1000, 2),
        total_results=len(hits),
        results=[SearchResult(**hit) for hit in hits],
    )
