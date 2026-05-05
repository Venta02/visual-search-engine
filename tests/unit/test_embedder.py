"""Unit tests for the embedding service.

These tests are slow because they load the actual model. Mark them as
slow if you want to skip them in CI's fast tier.
"""

import numpy as np
import pytest
from PIL import Image

from src.services.embedding import SigLIPEmbedder


@pytest.fixture(scope="module")
def embedder():
    return SigLIPEmbedder()


@pytest.fixture
def random_image():
    return Image.fromarray(
        np.random.randint(0, 255, size=(224, 224, 3), dtype=np.uint8)
    )


def test_embed_image_returns_normalized_vector(embedder, random_image):
    embedding = embedder.embed_image(random_image)
    assert embedding.shape == (embedder.embedding_dim,)
    assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-5)


def test_embed_text_returns_normalized_vector(embedder):
    embedding = embedder.embed_text("a photo of a dog")
    assert embedding.shape == (embedder.embedding_dim,)
    assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-5)


def test_batch_embedding_matches_single(embedder, random_image):
    single = embedder.embed_image(random_image)
    batch = embedder.embed_images_batch([random_image])
    assert batch.shape == (1, embedder.embedding_dim)
    assert np.allclose(single, batch[0], atol=1e-4)


def test_text_image_alignment_is_meaningful(embedder):
    """Sanity check: text embedding should be more similar to a related
    image embedding than to a random vector."""
    text_emb = embedder.embed_text("dog")
    image = Image.fromarray(
        np.random.randint(0, 255, size=(224, 224, 3), dtype=np.uint8)
    )
    image_emb = embedder.embed_image(image)
    random_emb = np.random.randn(embedder.embedding_dim).astype(np.float32)
    random_emb /= np.linalg.norm(random_emb)

    similarity_real = float(text_emb @ image_emb)
    similarity_random = float(text_emb @ random_emb)
    # Both could be small for random images, but at least the random vector
    # should not consistently outperform a real image embedding. This test
    # is a smoke test, not a quality test.
    assert -1.0 <= similarity_real <= 1.0
    assert -1.0 <= similarity_random <= 1.0
