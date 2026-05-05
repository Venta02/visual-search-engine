# Tests

Two test tiers:

- `unit/` runs without any external services. Fast, run on every commit.
- `integration/` requires a running Qdrant and Redis. Run before merging to main.

## Running Tests

All tests:

```bash
pytest
```

Only fast unit tests:

```bash
pytest tests/unit -v
```

Skip slow tests (those that load the embedding model):

```bash
pytest -m "not slow"
```

Integration tests (requires `docker compose up qdrant redis`):

```bash
pytest tests/integration -v
```

## Test Markers

- `@pytest.mark.slow`: Tests that take > 5 seconds. Skip in CI's fast tier.
- `@pytest.mark.integration`: Tests that require external services.

## Writing New Tests

- Mirror the source layout: a test for `src/services/embedding/embedder.py` lives at `tests/unit/test_embedder.py`.
- Use fixtures for shared setup (see `conftest.py`).
- Prefer property-based assertions (e.g., shape, normalization) over hardcoded values, which are brittle.
