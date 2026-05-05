"""Bulk indexing pipeline.

Reads images from disk, extracts embeddings in batches, and upserts them
into Qdrant. Designed to be resumable and to log progress for long runs.
"""

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

from src.core.logging import get_logger
from src.core.metrics import (
    indexed_documents_total,
    indexing_errors_total,
)
from src.services.embedding import SigLIPEmbedder
from src.services.search import QdrantSearchService

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass
class IndexingStats:
    total_seen: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0


class IndexingPipeline:
    """Coordinates embedder + search service for bulk indexing."""

    def __init__(
        self,
        embedder: SigLIPEmbedder,
        search_service: QdrantSearchService,
        batch_size: int = 32,
    ):
        self.embedder = embedder
        self.search_service = search_service
        self.batch_size = batch_size

    def index_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> IndexingStats:
        """Index all supported images in a directory.

        Args:
            directory: Path to the directory containing images.
            recursive: Whether to search subdirectories.

        Returns:
            IndexingStats summary of the run.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        self.search_service.ensure_collection()

        image_paths = list(self._iter_image_paths(directory, recursive))
        logger.info(
            "Starting indexing",
            directory=str(directory),
            image_count=len(image_paths),
        )

        stats = IndexingStats(total_seen=len(image_paths))

        with tqdm(total=len(image_paths), desc="Indexing", unit="img") as pbar:
            for batch_paths in self._batched(image_paths, self.batch_size):
                self._index_batch(batch_paths, stats)
                pbar.update(len(batch_paths))

        logger.info(
            "Indexing complete",
            total=stats.total_seen,
            succeeded=stats.succeeded,
            failed=stats.failed,
            skipped=stats.skipped,
        )
        return stats

    def _index_batch(self, batch_paths: list[Path], stats: IndexingStats) -> None:
        """Process one batch of image paths."""
        valid_images: list[Image.Image] = []
        valid_paths: list[Path] = []

        for path in batch_paths:
            try:
                img = Image.open(path).convert("RGB")
                valid_images.append(img)
                valid_paths.append(path)
            except (UnidentifiedImageError, OSError) as e:
                logger.warning(
                    "Failed to read image", path=str(path), error=str(e)
                )
                indexing_errors_total.labels(error_type="read_error").inc()
                stats.skipped += 1

        if not valid_images:
            return

        try:
            embeddings = self.embedder.embed_images_batch(valid_images)
        except Exception as e:
            logger.error("Embedding failed for batch", error=str(e))
            indexing_errors_total.labels(error_type="embedding_error").inc(
                len(valid_images)
            )
            stats.failed += len(valid_images)
            return

        ids = [self._stable_id(p) for p in valid_paths]
        payloads = [
            {
                "filename": p.name,
                "filepath": str(p),
                "size_bytes": p.stat().st_size,
            }
            for p in valid_paths
        ]

        try:
            self.search_service.upsert_batch(ids, embeddings, payloads)
            indexed_documents_total.inc(len(valid_paths))
            stats.succeeded += len(valid_paths)
        except Exception as e:
            logger.error("Qdrant upsert failed", error=str(e))
            indexing_errors_total.labels(error_type="upsert_error").inc(
                len(valid_paths)
            )
            stats.failed += len(valid_paths)

    @staticmethod
    def _iter_image_paths(directory: Path, recursive: bool) -> Iterator[Path]:
        """Yield image file paths matching supported extensions."""
        glob = directory.rglob if recursive else directory.glob
        for path in glob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path

    @staticmethod
    def _batched(items: list, batch_size: int) -> Iterator[list]:
        """Yield successive batches from a list."""
        for i in range(0, len(items), batch_size):
            yield items[i : i + batch_size]

    @staticmethod
    def _stable_id(path: Path) -> str:
        """Generate a deterministic UUID from the file path.

        This ensures re-indexing the same file produces the same ID,
        making the pipeline idempotent.
        """
        namespace = uuid.UUID("12345678-1234-5678-1234-567812345678")
        return str(uuid.uuid5(namespace, str(path.resolve())))
