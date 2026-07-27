"""
Analytics and Audit routes — query logs, system metrics, and language usage statistics.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends 
# pyrefly: ignore [missing-import]
from sqlalchemy import func 
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session 

from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.models import DocumentRecord, QueryLog

logger = get_logger("api.analytics")
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats")
def get_analytics_stats(db: Session = Depends(get_db)):
    """High-level platform statistics."""
    try:
        doc_count = db.query(func.count(DocumentRecord.id)).scalar() or 0
        page_total = db.query(func.sum(DocumentRecord.page_count)).scalar() or 0
        size_total = db.query(func.sum(DocumentRecord.file_size)).scalar() or 0
        query_count = db.query(func.count(QueryLog.id)).scalar() or 0
        avg_conf = db.query(func.avg(QueryLog.confidence)).scalar()

        en_count = db.query(func.count(DocumentRecord.id)).filter(
            (DocumentRecord.language == "en") | (DocumentRecord.language == None)  # noqa: E711
        ).scalar() or 0
        hi_count = db.query(func.count(DocumentRecord.id)).filter(
            DocumentRecord.language == "hi"
        ).scalar() or 0
        mr_count = db.query(func.count(DocumentRecord.id)).filter(
            DocumentRecord.language == "mr"
        ).scalar() or 0
    except Exception as exc:
        logger.warning("Error querying analytics stats: %s", exc)
        doc_count = page_total = size_total = query_count = en_count = hi_count = mr_count = 0
        avg_conf = None

    return {
        "document_count": doc_count,
        "chunk_count": doc_count * 8,
        "page_count": int(page_total),
        "total_size_bytes": int(size_total),
        "query_count": query_count,
        "avg_confidence": round(float(avg_conf), 3) if avg_conf else 0.0,
        "vector_store_size": doc_count,
        "languages": {"en": en_count, "hi": hi_count, "mr": mr_count},
    }


@router.get("/queries")
def get_recent_queries(limit: int = 20, db: Session = Depends(get_db)):
    """Return recent Q&A queries with metadata."""
    try:
        logs = (
            db.query(QueryLog)
            .order_by(QueryLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": log.id,
                "question": log.question,
                "language": log.language or "en",
                "document_id": log.document_id,
                "confidence": log.confidence,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    except Exception as exc:
        logger.warning("Error fetching query logs: %s", exc)
        return []
