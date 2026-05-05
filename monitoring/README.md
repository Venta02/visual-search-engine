# Monitoring

Prometheus and Grafana configs for local observability.

## Starting the Stack

```bash
docker compose up -d prometheus grafana
```

Then open:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

## Metrics Exposed

The API exposes Prometheus metrics at `http://localhost:8000/metrics`:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `vse_search_requests_total` | Counter | query_type, status | Search request count |
| `vse_search_latency_seconds` | Histogram | query_type | End-to-end search latency |
| `vse_embedding_requests_total` | Counter | modality | Embeddings extracted |
| `vse_embedding_latency_seconds` | Histogram | modality | Embedding extraction latency |
| `vse_cache_hits_total` | Counter | cache_name | Cache hits |
| `vse_cache_misses_total` | Counter | cache_name | Cache misses |
| `vse_indexed_documents_total` | Counter | - | Documents indexed |
| `vse_indexing_errors_total` | Counter | error_type | Indexing errors |
| `vse_vector_db_collection_size` | Gauge | collection | Collection size |

## Adding Dashboards

Place dashboard JSON files under `grafana/provisioning/dashboards/`. They will be auto-loaded on Grafana startup.

A starter dashboard with latency p50/p95/p99 panels is planned for Phase 2.
