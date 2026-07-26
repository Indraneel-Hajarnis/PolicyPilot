"""
PolicyPilot — FastAPI application entrypoint.

Configures middleware, registers routers, and manages application lifecycle.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import get_logger, setup_logging
from app.db.database import create_tables, dispose_engine
from app.services.embedder import embedder
from app.services.vector_store import vector_store

# ── Logging ──────────────────────────────────────────────────────────────────
setup_logging()
logger = get_logger("main")


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("PolicyPilot starting up...")

    # Ensure directories exist
    settings.ensure_directories()

    # Create database tables
    await create_tables()

    # Load or initialize the FAISS index
    loaded = vector_store.load()
    if loaded:
        logger.info("FAISS index loaded: %d vectors", vector_store.size)
    else:
        logger.info("No existing FAISS index — will be created on first upload")

    # Pre-warm the embedding model (lazy load)
    try:
        _ = embedder.dimension
        logger.info("Embedding model ready (dim=%d)", embedder.dimension)
    except Exception as e:
        logger.warning("Embedding model pre-load failed: %s", e)

    logger.info("PolicyPilot ready! Serving on %s:%d", settings.host, settings.port)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("PolicyPilot shutting down...")
    vector_store.save()
    await dispose_engine()
    logger.info("Shutdown complete")


# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="PolicyPilot",
    description="AI-powered policy document analysis & Q&A platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ──────────────────────────────────────────────────────

register_exception_handlers(app)

# ── Routers ──────────────────────────────────────────────────────────────────

from app.api.routes_upload import router as upload_router
from app.api.routes_query import router as query_router
from app.api.routes_summary import router as summary_router
from app.api.routes_documents import router as documents_router
from app.api.routes_health import router as health_router
from app.api.routes_analytics import router as analytics_router

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(summary_router)
app.include_router(documents_router)
app.include_router(health_router)
app.include_router(analytics_router)


# ── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — basic API information."""
    return {
        "name": "PolicyPilot",
        "version": "1.0.0",
        "description": "AI-powered policy document analysis & Q&A platform",
        "docs": "/docs",
    }
