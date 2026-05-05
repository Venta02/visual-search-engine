"""Prometheus metrics for observability.

Centralizes metric definitions so they can be incremented from anywhere
in the codebase. The /metrics endpoint exposes these to a Prometheus scraper.
"""

from prometheus_client import Counter, Histogram, Gauge


# Search metrics
search_requests_total = Counter(
    "vse_search_requests_total",
    "Total number of search requests received",
    labelnames=["query_type", "status"],
)

search_latency_seconds = Histogram(
    "vse_search_latency_seconds",
    "End-to-end search latency in seconds",
    labelnames=["query_type"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0),
)

# Embedding metrics
embedding_requests_total = Counter(
    "vse_embedding_requests_total",
    "Total embeddings extracted",
    labelnames=["modality"],  # image | text
)

embedding_latency_seconds = Histogram(
    "vse_embedding_latency_seconds",
    "Embedding extraction latency in seconds",
    labelnames=["modality"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

# Cache metrics
cache_hits_total = Counter(
    "vse_cache_hits_total",
    "Total cache hits",
    labelnames=["cache_name"],
)

cache_misses_total = Counter(
    "vse_cache_misses_total",
    "Total cache misses",
    labelnames=["cache_name"],
)

# Indexing metrics
indexed_documents_total = Counter(
    "vse_indexed_documents_total",
    "Total documents indexed into the vector database",
)

indexing_errors_total = Counter(
    "vse_indexing_errors_total",
    "Total indexing errors by error type",
    labelnames=["error_type"],
)

# Vector database metrics
vector_db_collection_size = Gauge(
    "vse_vector_db_collection_size",
    "Number of points in the vector collection",
    labelnames=["collection"],
)
