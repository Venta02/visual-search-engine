"""Vector search service backed by Qdrant.

Encapsulates collection creation, insertion, and search. Higher-level
services should use this rather than calling the Qdrant client directly,
to keep the data model consistent.
"""

from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

from src.core.config import settings
from src.core.logging import get_logger
from src.core.metrics import vector_db_collection_size

logger = get_logger(__name__)


class QdrantSearchService:
    """Wrapper around the Qdrant client for the images collection."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection_name: str | None = None,
        embedding_dim: int | None = None,
    ):
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.embedding_dim = embedding_dim or settings.embedding_dimension

        self.client = QdrantClient(
            host=host or settings.qdrant_host,
            port=port or settings.qdrant_port,
            timeout=30.0,
        )

        self._distance_map = {
            "Cosine": qmodels.Distance.COSINE,
            "Dot": qmodels.Distance.DOT,
            "Euclid": qmodels.Distance.EUCLID,
        }
        self.distance = self._distance_map[settings.qdrant_distance_metric]

        logger.info(
            "Qdrant client initialized",
            host=host or settings.qdrant_host,
            collection=self.collection_name,
            distance=settings.qdrant_distance_metric,
        )

    def ensure_collection(self) -> None:
        """Create the collection if it does not exist.

        Idempotent - safe to call on every service startup.
        """
        try:
            self.client.get_collection(self.collection_name)
            logger.info("Collection already exists", name=self.collection_name)
            return
        except (UnexpectedResponse, ValueError):
            pass

        logger.info("Creating collection", name=self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=self.embedding_dim,
                distance=self.distance,
                on_disk=False,
            ),
            hnsw_config=qmodels.HnswConfigDiff(
                m=16,
                ef_construct=128,
                full_scan_threshold=10_000,
            ),
            optimizers_config=qmodels.OptimizersConfigDiff(
                memmap_threshold=20_000,
            ),
        )
        logger.info("Collection created", name=self.collection_name)

    def upsert_batch(
        self,
        ids: list[int | str],
        vectors: np.ndarray,
        payloads: list[dict[str, Any]],
    ) -> None:
        """Insert or update a batch of vectors.

        Args:
            ids: Unique identifiers (int or UUID string).
            vectors: Array of shape (N, embedding_dim).
            payloads: Metadata dicts attached to each vector.
        """
        if len(ids) != len(vectors) or len(ids) != len(payloads):
            raise ValueError("ids, vectors, and payloads must have equal length")

        points = [
            qmodels.PointStruct(
                id=pid,
                vector=vec.tolist(),
                payload=payload,
            )
            for pid, vec, payload in zip(ids, vectors, payloads)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=False,
        )
        logger.debug("Upserted batch", count=len(points))

    def search(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        score_threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for nearest neighbors of a query vector.

        Args:
            query_vector: Shape (embedding_dim,).
            limit: Number of results to return.
            score_threshold: Minimum similarity score (0..1 for cosine).
            filters: Optional payload filters, e.g. {"category": "cat"}.

        Returns:
            List of dicts with keys: id, score, payload.
        """
        qdrant_filter = self._build_filter(filters) if filters else None

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit,
            score_threshold=score_threshold,
            query_filter=qdrant_filter,
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload or {},
            }
            for hit in results
        ]

    def get_collection_size(self) -> int:
        """Return the current count of indexed points."""
        info = self.client.get_collection(self.collection_name)
        size = info.points_count or 0
        vector_db_collection_size.labels(collection=self.collection_name).set(size)
        return size

    @staticmethod
    def _build_filter(filters: dict[str, Any]) -> qmodels.Filter:
        """Convert a simple dict into a Qdrant Filter object.

        Currently supports equality matching on payload fields. Extend this
        method to support range queries, geo queries, etc.
        """
        must = [
            qmodels.FieldCondition(
                key=key,
                match=qmodels.MatchValue(value=value),
            )
            for key, value in filters.items()
        ]
        return qmodels.Filter(must=must)
