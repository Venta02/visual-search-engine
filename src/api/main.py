"""FastAPI application entry point.

Run with:
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.api.dependencies import get_embedder, get_search_service
from src.api.routes_health import router as health_router
from src.api.routes_search import router as search_router
from src.core.config import settings
from src.core.logging import get_logger, setup_logging
from src.api.routes_images import router as images_router

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and tear down resources on app startup and shutdown."""
    logger.info("Application starting", env=settings.app_env)

    # Warm the model and Qdrant collection so the first request is fast.
    get_embedder()
    get_search_service()

    logger.info("Application ready")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Visual Search Engine",
    description="Multi-modal image retrieval using SigLIP + Qdrant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(search_router)
app.include_router(images_router)

@app.get("/", tags=["root"])
async def root():
    return {
        "service": "Visual Search Engine",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/metrics", tags=["monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
