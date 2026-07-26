"""
Related documents recommendation via embedding similarity.
"""

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.db.models import Chunk, Document
from app.db.schemas import DocumentOut
from app.services.embedder import embedder
from app.services.vector_store import vector_store

logger = get_logger("services.related_docs")


async def find_related_documents(
    document_ids: list[int],
    db: AsyncSession,
    limit: int = 3,
) -> list[DocumentOut]:
    """
    Find documents similar to the given document(s) based on
    average embedding similarity.

    Args:
        document_ids: IDs of the source document(s).
        db: Async database session.
        limit: Max number of related docs to return.

    Returns:
        List of DocumentOut for the most similar other documents.
    """
    if not document_ids:
        return []

    # 1. Get chunks for the source documents
    stmt = (
        select(Chunk.embedding_id)
        .where(Chunk.document_id.in_(document_ids))
        .where(Chunk.embedding_id.isnot(None))
    )
    result = await db.execute(stmt)
    embedding_ids = [row[0] for row in result.all()]

    if not embedding_ids or vector_store.index is None or vector_store.size == 0:
        return []

    # 2. Compute average embedding for the source documents
    vectors = []
    for eid in embedding_ids:
        if eid < vector_store.size:
            try:
                vec = vector_store.index.reconstruct(int(eid))
                vectors.append(vec)
            except Exception:
                continue

    if not vectors:
        return []

    avg_vector = np.mean(vectors, axis=0).astype(np.float32)
    # Re-normalize
    norm = np.linalg.norm(avg_vector)
    if norm > 0:
        avg_vector = avg_vector / norm

    # 3. Search FAISS for similar chunks (fetch extra to find different documents)
    results = vector_store.search(avg_vector, top_k=limit * 10)

    # 4. Map chunk IDs back to document IDs and filter out source docs
    chunk_ids = [cid for cid, _ in results]
    if not chunk_ids:
        return []

    stmt = (
        select(Chunk.document_id)
        .where(Chunk.id.in_(chunk_ids))
        .where(Chunk.document_id.notin_(document_ids))
        .distinct()
    )
    result = await db.execute(stmt)
    related_doc_ids = [row[0] for row in result.all()][:limit]

    if not related_doc_ids:
        return []

    # 5. Fetch full document records
    stmt = select(Document).where(Document.id.in_(related_doc_ids))
    result = await db.execute(stmt)
    docs = result.scalars().all()

    related = [DocumentOut.model_validate(doc) for doc in docs]
    logger.info("Found %d related documents for doc IDs %s", len(related), document_ids)
    return related
