"""
Summary endpoint — structured document summarization.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.schemas import SummaryResponse
from app.services.summarizer import summarize_document

logger = get_logger("api.summary")
router = APIRouter(prefix="/api", tags=["Summary"])


@router.get("/summary/{document_id}", response_model=SummaryResponse)
async def get_summary(
    document_id: int,
    language: str = "en",
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    """
    Generate a structured summary of a specific document in the target language (en, hi, mr).
    """
    logger.info("Summary requested for document ID: %d in language: %s", document_id, language)

    summary = await summarize_document(
        document_id=document_id,
        db=db,
        language=language,
    )

    return summary
