# Development Guide

This guide describes how to set up a local development environment, run the code, and contribute changes.

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Git
- A code editor (VS Code recommended)

## Initial Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/yourusername/visual-search-engine.git
cd visual-search-engine
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` if you need to change defaults (e.g., switch `EMBEDDING_DEVICE=cuda` if you have a GPU).

## Running the Stack

Start the supporting services:

```bash
make docker-up
```

This brings up Qdrant on port 6333 and Redis on port 6379. To also start the monitoring stack:

```bash
make docker-up-full
```

Build a small index from sample images:

```bash
python scripts/download_sample_dataset.py
python scripts/build_index.py --dataset data/raw/sample
```

Run the API:

```bash
make dev
```

In a separate terminal, run the demo UI:

```bash
make demo
```

Visit:
- API docs: http://localhost:8000/docs
- Demo UI: http://localhost:8501
- Qdrant dashboard: http://localhost:6333/dashboard
- Grafana (if monitoring stack is up): http://localhost:3000

## Project Structure

See the [Project Structure](../README.md#project-structure) section in the main README.

## Code Style

- Format with `black`. Run `make format`.
- Lint with `ruff`. Run `make lint`.
- Type-check with `mypy`. Included in `make lint`.
- Follow PEP 8 and use type hints everywhere.

## Testing

Run the full test suite:

```bash
make test
```

Run only fast tests:

```bash
pytest tests/unit -v
```

Tests that load the embedding model are slow. Mark them with `@pytest.mark.slow` if you want to skip them in CI's fast tier.

## Common Issues

### "Qdrant unreachable" errors

Make sure Docker is running and `make docker-up` has been executed. Verify with:

```bash
curl http://localhost:6333/healthz
```

### Slow embedding on first request

The first request loads the model into memory, which can take 10-20 seconds. Subsequent requests use the cached model. The lifespan handler in `src/api/main.py` warms the model on startup.

### Out of memory errors during indexing

Reduce `EMBEDDING_BATCH_SIZE` in your `.env` file. The default of 16 should work on 8GB RAM machines.

### Type errors with PyTorch tensors

Make sure your PyTorch installation matches the CUDA version on your machine. For CPU-only:

```bash
pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
```

## Adding a New Feature

1. Create a feature branch from `main`.
2. Write tests first (TDD).
3. Implement the feature.
4. Update relevant documentation in `docs/`.
5. Run `make lint` and `make test` before committing.
6. Open a pull request with a clear description and benchmark numbers if relevant.
