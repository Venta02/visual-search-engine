"""Health check endpoints."""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_search_service
from src.core.logging import get_logger
from src.models import HealthResponse
from src.services.search import QdrantSearchService

logger = get_logger(__name__)

router = APIRouter(tags=["health"])

VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health_check(
    search: QdrantSearchService = Depends(get_search_service),
) -> HealthResponse:
    """Liveness and readiness probe.

    Reports whether downstream services (Qdrant, Redis) are reachable
    and how many documents are currently indexed.
    """
    qdrant_reachable = True
    indexed_count = 0
    try:
        indexed_count = search.get_collection_size()
    except Exception as e:
        logger.warning("Qdrant unreachable in health check", error=str(e))
        qdrant_reachable = False

    # TODO: add a Redis ping when caching layer is wired in
    redis_reachable = True

    return HealthResponse(
        status="ok" if qdrant_reachable else "degraded",
        version=VERSION,
        qdrant_reachable=qdrant_reachable,
        redis_reachable=redis_reachable,
        indexed_count=indexed_count,
    )
