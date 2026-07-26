"""
Query endpoint — RAG-based question answering.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.schemas import QueryRequest, QueryResponse
from app.services.qa_pipeline import answer_question

logger = get_logger("api.query")
router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """
    Ask a question about uploaded policy documents.

    The RAG pipeline retrieves relevant chunks, builds context,
    and generates an answer via the Groq LLM.
    """
    logger.info(
        "Query received: '%s' (doc_id=%s, lang=%s)",
        request.question[:80],
        request.document_id,
        request.language,
    )

    response = await answer_question(
        question=request.question,
        db=db,
        document_id=request.document_id,
        language=request.language,
    )

    return response
