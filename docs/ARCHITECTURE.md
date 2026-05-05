# Architecture

This document describes the high-level design of the Visual Search Engine.

## System Overview

The system is composed of several decoupled services that communicate over well-defined interfaces:

- **API Gateway (FastAPI)** is the public entry point. It handles authentication, validation, rate limiting, and routes requests to the appropriate downstream service.
- **Embedding Service (SigLIP)** encodes images and text into a shared 768-dimensional vector space. Embeddings are L2-normalized so that cosine similarity equals dot product.
- **Vector Database (Qdrant)** stores embeddings together with metadata payloads. It serves approximate nearest neighbor (ANN) queries using the HNSW algorithm.
- **Cache (Redis)** stores precomputed embeddings for frequently queried text strings and frequently viewed image hashes. This avoids redundant embedding computation on hot queries.
- **Background Workers (Celery)** handle bulk indexing jobs, model warm-up, and scheduled re-indexing tasks asynchronously.
- **Monitoring (Prometheus + Grafana)** scrapes metrics from every service and exposes dashboards for latency, throughput, error rate, and cache hit ratio.

## Data Flow

### Indexing path

1. The indexing CLI or a worker reads images from a directory or object store.
2. Images are read into PIL Image objects and grouped into batches of N (default 32).
3. The embedding service runs each batch through SigLIP and returns a (N, 768) float32 array.
4. The Qdrant client upserts each vector along with a metadata payload (filename, path, size, custom labels).
5. Metrics for indexed count and error count are updated.

### Search path

1. A search request arrives at the FastAPI gateway.
2. The query (text or image) is normalized and the cache is checked.
3. On a cache miss, the embedding service produces a query vector and the result is cached with a TTL.
4. The Qdrant client runs an HNSW search with the requested top-K and optional metadata filters.
5. Results are serialized to the response model and returned.
6. Latency, status, and result count are emitted as metrics.

## Key Design Decisions

### Why SigLIP over CLIP

SigLIP uses a sigmoid loss instead of softmax over the full batch, which scales better and produces tighter alignments between text and image embeddings. Empirically it outperforms CLIP at retrieval tasks with smaller models. The base variant (~200M parameters) runs comfortably on CPU for inference and on a 4GB GPU for batch indexing.

### Why Qdrant over alternatives

Compared with Pinecone (managed, paid), Milvus (heavy infrastructure), or pgvector (limited at scale), Qdrant strikes a balance between operational simplicity and production performance. It runs as a single binary or container, supports gRPC, has well-tuned HNSW defaults, and provides strong filtering performance.

### Why HNSW over IVF-PQ for the first iteration

HNSW has high recall and predictable latency at the scales we care about (up to a few million vectors). IVF-PQ trades recall for memory savings, which is valuable at much larger scale. We will add an IVF-PQ comparison in Phase 3 once the baseline is stable.

### Why a separate cache layer

The embedding model dominates request latency on CPU (typically 50-150ms). Caching common text queries can drop end-to-end latency below 10ms, which makes the difference between a usable demo and a production-grade service.

## Failure Modes and Mitigations

| Failure | Impact | Mitigation |
|---------|--------|-----------|
| Qdrant unreachable | Search returns 503 | Health check fails so load balancer takes the instance out of rotation |
| Embedding OOM | Single batch fails | Catch and retry with smaller batch size; log and continue |
| Cache miss storm | Latency spike | Pre-warm cache with top-N popular queries on startup |
| Corrupt image during indexing | Single document skipped | Try/except per item, log and continue, increment error metric |

## Future Work

- Add gRPC alongside REST for service-to-service communication
- Move from Docker Compose to Kubernetes manifests for production
- Add a re-ranking layer using a cross-encoder for higher precision on top-10
- Multi-region deployment with Qdrant cluster mode
