# Benchmarks

This directory holds benchmark results and reproducibility instructions. Each benchmark report should answer: What was measured, on what hardware, and how can it be reproduced?

## Layout

Each benchmark gets its own subdirectory:

```
benchmarks/
├── README.md (this file)
├── latency/
│   ├── REPORT.md
│   ├── results.csv
│   └── reproduce.sh
└── recall/
    ├── REPORT.md
    └── ...
```

## Planned Benchmarks

### Phase 2

- **Latency**: p50/p95/p99 search latency at 1k, 10k, 100k indexed images.
- **Throughput**: Requests per second at sustained load (Locust, 100 concurrent users).
- **Cache effectiveness**: Latency reduction with Redis vs without.

### Phase 3

- **Quantization**: FP32 vs FP16 vs INT8 (accuracy drop, latency, memory).
- **ANN algorithms**: HNSW vs IVF-PQ vs Flat (recall@10, latency, memory).
- **Cold start**: Time from container start to first response.

## Benchmark Hygiene

- Always note hardware (CPU, RAM, GPU model).
- Always note dataset size and characteristics.
- Run multiple iterations and report mean and standard deviation.
- Save raw data (CSV) alongside the markdown report.
- Include a `reproduce.sh` script so others can verify.
