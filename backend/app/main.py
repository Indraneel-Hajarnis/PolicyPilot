# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_analytics import router as analytics_router
from app.api.routes_chat import router as chat_router
from app.api.routes_compare import router as compare_router
from app.api.routes_documents import router as documents_router
from app.api.routes_health import router as health_router
from app.api.routes_query import router as query_router
from app.api.routes_repository import router as repository_router
from app.api.routes_summary import router as summary_router
from app.api.routes_upload import router as upload_router
from app.config import settings
import threading
from app.db.database import init_db

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
app.include_router(repository_router, prefix="/api")

init_db()


@app.on_event("startup")
def prewarm_models():
    """Background pre-warm for SentenceTransformer embedder & FAISS store."""
    def _warm():
        try:
            from app.services.rag_engine import _get_embedder, _get_vector_store
            _get_embedder()
            _get_vector_store()
        except Exception:
            pass
    threading.Thread(target=_warm, daemon=True).start()


@app.get("/")
def read_root():
    return {"message": "PolicyPilot API is running"}