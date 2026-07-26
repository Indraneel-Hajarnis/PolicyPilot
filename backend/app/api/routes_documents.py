"""
Documents endpoints — list, detail, and delete documents.
"""

from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import DocumentNotFoundError
from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.models import Chunk, Document
from app.db.schemas import DocumentDetail, DocumentOut
from app.services.vector_store import vector_store

logger = get_logger("api.documents")
router = APIRouter(prefix="/api", tags=["Documents"])


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    """List all uploaded documents, ordered by upload date descending."""
    stmt = select(Document).order_by(Document.upload_date.desc())
    result = await db.execute(stmt)
    docs = result.scalars().all()
    return [DocumentOut.model_validate(doc) for doc in docs]


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> DocumentDetail:
    """Get detailed information about a specific document."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)

    # Count chunks
    stmt = select(func.count()).select_from(Chunk).where(Chunk.document_id == document_id)
    result = await db.execute(stmt)
    chunk_count = result.scalar() or 0

    detail = DocumentDetail(
        **DocumentOut.model_validate(doc).model_dump(),
        chunk_count=chunk_count,
    )
    return detail


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a document and all associated data:
    - Database records (document + chunks via cascade)
    - FAISS embeddings
    - Stored PDF file
    """
    doc = await db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)

    # 1. Get chunk IDs for FAISS removal
    stmt = select(Chunk.id).where(Chunk.document_id == document_id)
    result = await db.execute(stmt)
    chunk_ids = {row[0] for row in result.all()}

    # 2. Remove from FAISS
    if chunk_ids:
        vector_store.remove_by_chunk_ids(chunk_ids)
        vector_store.save()

    # 3. Delete the PDF file
    pdf_path = Path(settings.upload_dir) / doc.filename
    pdf_path.unlink(missing_ok=True)

    # 4. Delete from database (chunks cascade)
    await db.delete(doc)

    logger.info(
        "Deleted document '%s' (id=%d, chunks=%d)",
        doc.original_name,
        document_id,
        len(chunk_ids),
    )

    return {
        "message": f"Document '{doc.original_name}' deleted successfully",
        "deleted_chunks": len(chunk_ids),
    }
