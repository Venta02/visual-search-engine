"""Celery task definitions.

Tasks are designed to be idempotent and resumable. A task that fails
mid-way through a batch should be safe to retry.
"""

from pathlib import Path

from celery import shared_task

from src.core.logging import get_logger
from src.services.embedding import SigLIPEmbedder
from src.services.indexing import IndexingPipeline
from src.services.search import QdrantSearchService

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def index_directory_task(self, directory: str, batch_size: int = 32) -> dict:
    """Index a directory of images asynchronously.

    Args:
        directory: Path to the directory containing images.
        batch_size: Number of images per embedding batch.

    Returns:
        A dict with indexing statistics.
    """
    logger.info(
        "Indexing task started",
        task_id=self.request.id,
        directory=directory,
        batch_size=batch_size,
    )

    try:
        embedder = SigLIPEmbedder(batch_size=batch_size)
        search_service = QdrantSearchService(embedding_dim=embedder.embedding_dim)
        pipeline = IndexingPipeline(
            embedder=embedder,
            search_service=search_service,
            batch_size=batch_size,
        )
        stats = pipeline.index_directory(Path(directory))

        return {
            "task_id": self.request.id,
            "directory": directory,
            "total_seen": stats.total_seen,
            "succeeded": stats.succeeded,
            "failed": stats.failed,
            "skipped": stats.skipped,
        }
    except Exception as exc:
        logger.error("Indexing task failed", error=str(exc))
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def warm_embedding_cache_task(queries: list[str]) -> int:
    """Pre-compute embeddings for a list of common queries.

    Useful at startup or after deployment to avoid cold-start latency
    for popular searches.

    Args:
        queries: List of text queries to pre-embed.

    Returns:
        Number of queries embedded.
    """
    logger.info("Warming embedding cache", count=len(queries))
    embedder = SigLIPEmbedder()
    for query in queries:
        embedder.embed_text(query)
    return len(queries)
