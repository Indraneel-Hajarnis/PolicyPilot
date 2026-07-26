"""
Analytics and Audit routes — query logs, system metrics, and usage statistics.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy import func, select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession 

from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.models import Chunk, Document, QueryLog
from app.services.vector_store import vector_store

logger = get_logger("api.analytics")
router = APIRouter(prefix="/api", tags=["Analytics"])


@router.get("/analytics/stats")
async def get_analytics_stats(db: AsyncSession = Depends(get_db)):
    """
    Get high-level platform statistics: total documents, total chunks,
    query count, average confidence, vector store size, language breakdown.
    """
    doc_count = (await db.execute(select(func.count()).select_from(Document))).scalar() or 0
    chunk_count = (await db.execute(select(func.count()).select_from(Chunk))).scalar() or 0
    query_count = (await db.execute(select(func.count()).select_from(QueryLog))).scalar() or 0
    avg_conf = (await db.execute(select(func.avg(QueryLog.confidence)))).scalar() or 0.0

    # Language breakdown query
    lang_stmt = select(Document.language, func.count()).group_by(Document.language)
    lang_result = await db.execute(lang_stmt)
    languages = {row[0] or "en": row[1] for row in lang_result.all()}

    return {
        "document_count": doc_count,
        "chunk_count": chunk_count,
        "query_count": query_count,
        "avg_confidence": round(float(avg_conf), 2),
        "vector_store_size": vector_store.size,
        "languages": languages,
    }


@router.get("/analytics/queries")
async def get_recent_queries(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch recent Q&A query logs with confidence ratings.
    """
    stmt = select(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "question": log.question,
            "answer": log.answer,
            "confidence": round(log.confidence, 2),
            "document_ids": log.document_ids,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
