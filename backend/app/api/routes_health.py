"""
Health check endpoint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.db.models import Document
from app.db.schemas import HealthResponse
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """
    Check API health, FAISS index stats, and document count.
    """
    # Count documents
    stmt = select(func.count()).select_from(Document)
    result = await db.execute(stmt)
    doc_count = result.scalar() or 0

    return HealthResponse(
        status="healthy",
        document_count=doc_count,
        faiss_index_size=vector_store.size,
        embedding_model=settings.embedding_model,
        llm_model=settings.groq_model,
    )
