# Source Code

Application source organized by responsibility:

| Folder | Purpose |
|--------|---------|
| `api/` | FastAPI application: routes, dependencies, lifespan handlers |
| `core/` | Cross-cutting concerns: configuration, logging, metrics |
| `services/` | Business logic: embedding, vector search, indexing |
| `models/` | Pydantic schemas for request/response validation |
| `workers/` | Celery tasks for async background work |
| `utils/` | Small helpers shared across modules |

## Module Boundaries

- `api/` depends on `services/` and `models/`. It must not import from `workers/`.
- `services/` depends on `core/` only. It must not import from `api/` or `models/`.
- `core/` depends on nothing else in this package.

This direction-of-dependency rule keeps the layers cleanly separated and makes the services testable in isolation.

## Adding a New Service

1. Create a new package under `services/`.
2. Expose a single class or set of functions through `__init__.py`.
3. Add unit tests under `tests/unit/`.
4. Wire it up via FastAPI dependencies in `api/dependencies.py` if it should be reachable through HTTP.
