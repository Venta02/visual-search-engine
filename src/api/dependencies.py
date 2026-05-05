"""FastAPI dependency injection.

Provides cached singletons for the embedding model and search service so
they are loaded once per process, not per request.
"""

from functools import lru_cache

from src.services.embedding import SigLIPEmbedder
from src.services.search import QdrantSearchService


@lru_cache
def get_embedder() -> SigLIPEmbedder:
    """Cached embedding model instance."""
    return SigLIPEmbedder()


@lru_cache
def get_search_service() -> QdrantSearchService:
    """Cached search service instance."""
    service = QdrantSearchService()
    service.ensure_collection()
    return service
