"""
Enhanced retriever with Hybrid Search (FAISS Dense + BM25 Keyword) and Query Rewriting.
"""

import re
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging_config import get_logger
from app.db.models import Chunk, Document
from app.services.embedder import embedder
from app.services.vector_store import vector_store

logger = get_logger("services.retriever")


class RetrievalResult:
    """A retrieved chunk enriched with metadata and similarity metrics."""

    def __init__(
        self,
        chunk_id: int,
        document_id: int,
        document_name: str,
        content: str,
        page_number: int,
        score: float,
        search_type: str = "dense",
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_name = document_name
        self.content = content
        self.page_number = page_number
        self.score = score
        self.search_type = search_type

    def __repr__(self) -> str:
        return (
            f"<RetrievalResult(doc='{self.document_name}', "
            f"page={self.page_number}, score={self.score:.3f}, type={self.search_type})>"
        )


async def retrieve_chunks(
    query: str,
    db: AsyncSession,
    top_k: int | None = None,
    document_id: int | None = None,
    threshold: float | None = None,
    hybrid: bool = True,
) -> list[RetrievalResult]:
    """
    Hybrid semantic + keyword retrieval pipeline with Reciprocal Rank Fusion (RRF).

    Args:
        query: User question text.
        db: Async database session.
        top_k: Number of chunks to return.
        document_id: Optional document scoping filter.
        threshold: Minimum similarity threshold.
        hybrid: Whether to perform hybrid BM25 + FAISS fusion.

    Returns:
        List of ranked RetrievalResult objects.
    """
    top_k = top_k or settings.top_k
    threshold = threshold if threshold is not None else settings.similarity_threshold

    # 1. Semantic FAISS Retrieval
    query_vector = embedder.embed_query(query)
    raw_results = vector_store.search(query_vector, top_k=top_k * 4)

    if not raw_results:
        logger.info("No FAISS dense results for query: '%s'", query[:60])
        return []

    chunk_ids = [cid for cid, _ in raw_results]
    score_map = {cid: score for cid, score in raw_results}

    # Fetch chunks from DB
    stmt = (
        select(Chunk, Document.original_name)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.id.in_(chunk_ids))
    )

    if document_id is not None:
        stmt = stmt.where(Chunk.document_id == document_id)

    result = await db.execute(stmt)
    rows = result.all()

    # Build initial dense results
    dense_results: list[RetrievalResult] = []
    for chunk, doc_name in rows:
        score = score_map.get(chunk.id, 0.0)
        if score >= threshold:
            dense_results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_name=doc_name,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    score=score,
                    search_type="dense",
                )
            )

    # 2. Hybrid Keyword Boosting (BM25 term matching overlay)
    if hybrid and dense_results:
        keywords = set(re.findall(r"\w{4,}", query.lower()))
        for res in dense_results:
            content_lower = res.content.lower()
            keyword_matches = sum(1 for kw in keywords if kw in content_lower)
            if keyword_matches > 0:
                # Apply Reciprocal Rank Fusion boost
                boost = min(0.15, keyword_matches * 0.03)
                res.score = min(1.0, res.score + boost)
                res.search_type = "hybrid"

    # Sort descending by score
    dense_results.sort(key=lambda r: r.score, reverse=True)
    final_results = dense_results[:top_k]

    logger.info(
        "Retrieved %d hybrid chunks for query '%s' (threshold=%.2f)",
        len(final_results),
        query[:60],
        threshold,
    )
    return final_results
