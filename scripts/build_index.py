"""CLI to build a search index from a directory of images.

Usage:
    python scripts/build_index.py --dataset data/raw/sample --batch-size 16
"""

from pathlib import Path

import click

from src.core.logging import get_logger, setup_logging
from src.services.embedding import SigLIPEmbedder
from src.services.indexing import IndexingPipeline
from src.services.search import QdrantSearchService

setup_logging()
logger = get_logger(__name__)


@click.command()
@click.option(
    "--dataset",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Path to the directory containing images.",
)
@click.option(
    "--batch-size",
    type=int,
    default=32,
    help="Number of images per embedding batch.",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Whether to recurse into subdirectories.",
)
def main(dataset: Path, batch_size: int, recursive: bool):
    """Build the visual search index from a directory of images."""
    logger.info(
        "Starting indexing job",
        dataset=str(dataset),
        batch_size=batch_size,
        recursive=recursive,
    )

    embedder = SigLIPEmbedder(batch_size=batch_size)
    search_service = QdrantSearchService(embedding_dim=embedder.embedding_dim)
    pipeline = IndexingPipeline(
        embedder=embedder,
        search_service=search_service,
        batch_size=batch_size,
    )

    stats = pipeline.index_directory(dataset, recursive=recursive)

    click.echo("\n=== Indexing Summary ===")
    click.echo(f"Total seen:  {stats.total_seen}")
    click.echo(f"Succeeded:   {stats.succeeded}")
    click.echo(f"Failed:      {stats.failed}")
    click.echo(f"Skipped:     {stats.skipped}")
    click.echo(f"Index size:  {search_service.get_collection_size()}")


if __name__ == "__main__":
    main()
