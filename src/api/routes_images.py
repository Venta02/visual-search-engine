"""Image serving routes.

Serves indexed images by their Qdrant point ID, so the frontend can
display search results without direct disk access.
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from src.api.dependencies import get_search_service
from src.core.logging import get_logger
from src.services.search import QdrantSearchService

logger = get_logger(__name__)

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{point_id}")
async def get_image(
    point_id: str,
    search: QdrantSearchService = Depends(get_search_service),
) -> FileResponse:
    """Serve an indexed image by its point ID.

    Looks up the point's payload in Qdrant, then returns the image
    file from disk. The frontend uses this endpoint to display
    thumbnails of search results.
    """
    try:
        # Retrieve the point with its payload from Qdrant
        points = search.client.retrieve(
            collection_name=search.collection_name,
            ids=[point_id],
            with_payload=True,
            with_vectors=False,
        )
    except Exception as e:
        logger.error("Failed to retrieve point", point_id=point_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve image record",
        ) from e

    if not points:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id {point_id} not found",
        )

    payload = points[0].payload or {}
    filepath = payload.get("filepath")

    if not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image record has no filepath",
        )

    path = Path(filepath)
    if not path.is_absolute():
        # Resolve relative paths from project root (cwd when uvicorn started)
        path = Path.cwd() / path

    if not path.exists() or not path.is_file():
        logger.warning("Image file not found on disk", filepath=str(path))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk",
        )

    return FileResponse(
        path=str(path),
        media_type="image/jpeg",
    )