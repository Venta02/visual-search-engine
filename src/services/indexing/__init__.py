"""Indexing service: bulk insert images into the search index."""

from src.services.indexing.pipeline import IndexingPipeline, IndexingStats

__all__ = ["IndexingPipeline", "IndexingStats"]
