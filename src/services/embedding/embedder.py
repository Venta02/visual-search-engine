"""SigLIP embedding extraction service.

Wraps the Hugging Face SigLIP model to extract embeddings for both images
and text queries. Handles batching, normalization, and device placement.

Usage:
    embedder = SigLIPEmbedder()
    image_emb = embedder.embed_image(pil_image)
    text_emb = embedder.embed_text("a photo of a dog")
    similarity = (image_emb @ text_emb.T).item()
"""

import time
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

from src.core.config import settings
from src.core.logging import get_logger
from src.core.metrics import (
    embedding_latency_seconds,
    embedding_requests_total,
)

logger = get_logger(__name__)


class SigLIPEmbedder:
    """Wrapper around the SigLIP model for image and text embedding."""

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
    ):
        self.model_name = model_name or settings.embedding_model_name
        self.device = self._resolve_device(device or settings.embedding_device)
        self.batch_size = batch_size or settings.embedding_batch_size

        logger.info(
            "Loading embedding model",
            model_name=self.model_name,
            device=self.device,
            batch_size=self.batch_size,
        )

        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

        # Cache embedding dimension for downstream services
        self.embedding_dim = self.model.config.vision_config.hidden_size

        logger.info(
            "Embedding model loaded",
            embedding_dim=self.embedding_dim,
        )

    @staticmethod
    def _resolve_device(requested: str) -> str:
        """Fall back to CPU if the requested device is unavailable."""
        if requested == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            return "cpu"
        if requested == "mps" and not torch.backends.mps.is_available():
            logger.warning("MPS requested but not available, falling back to CPU")
            return "cpu"
        return requested

    @torch.inference_mode()
    def embed_image(self, image: Image.Image | str | Path) -> np.ndarray:
        """Embed a single image into a normalized vector.

        Args:
            image: A PIL Image or a path to an image file.

        Returns:
            A numpy array of shape (embedding_dim,), L2-normalized.
        """
        start = time.perf_counter()

        if isinstance(image, (str, Path)):
            image = Image.open(image).convert("RGB")
        elif image.mode != "RGB":
            image = image.convert("RGB")

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        features = self.model.get_image_features(**inputs)
        embedding = self._normalize(features).cpu().numpy()[0]

        embedding_latency_seconds.labels(modality="image").observe(
            time.perf_counter() - start
        )
        embedding_requests_total.labels(modality="image").inc()

        return embedding

    @torch.inference_mode()
    def embed_images_batch(
        self, images: Iterable[Image.Image | str | Path]
    ) -> np.ndarray:
        """Embed a batch of images for indexing.

        Args:
            images: An iterable of PIL Images or paths.

        Returns:
            A numpy array of shape (N, embedding_dim), L2-normalized.
        """
        start = time.perf_counter()

        loaded = []
        for img in images:
            if isinstance(img, (str, Path)):
                img = Image.open(img).convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")
            loaded.append(img)

        all_embeddings = []
        for i in range(0, len(loaded), self.batch_size):
            batch = loaded[i : i + self.batch_size]
            inputs = self.processor(images=batch, return_tensors="pt").to(self.device)
            features = self.model.get_image_features(**inputs)
            embeddings = self._normalize(features).cpu().numpy()
            all_embeddings.append(embeddings)

        result = np.vstack(all_embeddings)

        elapsed = time.perf_counter() - start
        embedding_latency_seconds.labels(modality="image").observe(elapsed / len(loaded))
        embedding_requests_total.labels(modality="image").inc(len(loaded))

        logger.debug(
            "Batch image embedding complete",
            count=len(loaded),
            elapsed_seconds=round(elapsed, 3),
            throughput_per_second=round(len(loaded) / elapsed, 2),
        )
        return result

    @torch.inference_mode()
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a text query into a normalized vector.

        Args:
            text: The text to embed.

        Returns:
            A numpy array of shape (embedding_dim,), L2-normalized.
        """
        start = time.perf_counter()

        inputs = self.processor(
            text=[text],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
        ).to(self.device)
        features = self.model.get_text_features(**inputs)
        embedding = self._normalize(features).cpu().numpy()[0]

        embedding_latency_seconds.labels(modality="text").observe(
            time.perf_counter() - start
        )
        embedding_requests_total.labels(modality="text").inc()

        return embedding

    @staticmethod
    def _normalize(features: torch.Tensor) -> torch.Tensor:
        """L2-normalize a batch of feature vectors."""
        return features / features.norm(dim=-1, keepdim=True).clamp(min=1e-12)
