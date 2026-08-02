from contextlib import asynccontextmanager

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_analytics import router as analytics_router
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.api.routes_compare import router as compare_router
from app.api.routes_documents import router as documents_router
from app.api.routes_health import router as health_router
from app.api.routes_query import router as query_router
from app.api.routes_repository import router as repository_router
from app.api.routes_summary import router as summary_router
from app.api.routes_upload import router as upload_router
from app.config import settings
from app.db.database import SessionLocal, init_db
from app.services.auth import ensure_default_users
from app.services.seed_repository import seed_central_repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Check-or-seed: load pre-computed FAISS or seed from bundled docs
        from app.services.startup import initialize_data
        initialize_data()

        ensure_default_users()
        db = SessionLocal()
        try:
            seed_central_repository(db)
        finally:
            db.close()
    except Exception as exc:
        print(f"Startup initialization warning: {exc}")
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
app.include_router(repository_router, prefix="/api")

init_db()


@app.get("/")
def read_root():
    return {"message": "PolicyPilot API is running"}
