"""Integration tests for the FastAPI application.

These tests exercise the full HTTP layer with a real embedding model
and a real Qdrant instance. They are slow and should be run before
merging to main, not on every commit.
"""

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture(scope="module")
def client():
    """Provide a TestClient with the lifespan handler triggered."""
    from src.api.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.integration
@pytest.mark.slow
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "Visual Search Engine"


@pytest.mark.integration
@pytest.mark.slow
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "indexed_count" in body


@pytest.mark.integration
@pytest.mark.slow
def test_text_search(client):
    response = client.post(
        "/search/text",
        json={"query": "a photo of a cat", "limit": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["query_type"] == "text"
    assert "latency_ms" in body
    assert isinstance(body["results"], list)


@pytest.mark.integration
@pytest.mark.slow
def test_image_search_with_uploaded_file(client):
    # Build a small in-memory PNG
    img = Image.fromarray(
        np.random.randint(0, 255, size=(224, 224, 3), dtype=np.uint8)
    )
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/search/image",
        files={"file": ("test.png", buffer, "image/png")},
        params={"limit": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["query_type"] == "image"


@pytest.mark.integration
@pytest.mark.slow
def test_image_search_rejects_non_image(client):
    response = client.post(
        "/search/image",
        files={"file": ("not_an_image.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.integration
def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "vse_search_requests_total" in response.text
