"""Integration tests for the Qdrant search service.

Requires a running Qdrant instance on localhost:6333. Start with:
    docker compose up -d qdrant
"""

import uuid

import numpy as np
import pytest

from src.services.search import QdrantSearchService


@pytest.fixture(scope="module")
def search_service():
    """Create an isolated test collection per test run."""
    test_collection = f"test_collection_{uuid.uuid4().hex[:8]}"
    service = QdrantSearchService(
        collection_name=test_collection,
        embedding_dim=128,
    )
    service.ensure_collection()
    yield service
    # Clean up
    try:
        service.client.delete_collection(test_collection)
    except Exception:
        pass


@pytest.mark.integration
def test_ensure_collection_is_idempotent(search_service):
    """Calling ensure_collection twice should not fail."""
    search_service.ensure_collection()
    search_service.ensure_collection()


@pytest.mark.integration
def test_upsert_and_search(search_service):
    """Inserted vectors should be retrievable by similarity."""
    rng = np.random.default_rng(42)
    vectors = rng.standard_normal((10, 128)).astype(np.float32)
    # Normalize for cosine
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    ids = list(range(10))
    payloads = [{"index": i, "label": f"item_{i}"} for i in range(10)]

    search_service.upsert_batch(ids=ids, vectors=vectors, payloads=payloads)

    # Query with the first vector exactly - should be the top hit
    results = search_service.search(query_vector=vectors[0], limit=3)
    assert len(results) == 3
    assert results[0]["id"] == 0
    assert results[0]["score"] > 0.99


@pytest.mark.integration
def test_search_with_filters(search_service):
    """Filter should restrict results to matching payload values."""
    rng = np.random.default_rng(123)
    vectors = rng.standard_normal((20, 128)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    ids = list(range(100, 120))
    payloads = [
        {"category": "A" if i < 110 else "B"} for i in range(100, 120)
    ]

    search_service.upsert_batch(ids=ids, vectors=vectors, payloads=payloads)

    query = vectors[0]
    results = search_service.search(
        query_vector=query, limit=20, filters={"category": "A"}
    )
    for hit in results:
        assert hit["payload"]["category"] == "A"
