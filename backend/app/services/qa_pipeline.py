"""
RAG Q&A pipeline — orchestrates retrieval and generation for question answering.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.db.models import QueryLog
from app.db.schemas import QueryResponse, SourceCitation
from app.prompts.qa_prompt import build_qa_messages
from app.services.groq_client import groq_client
from app.services.related_docs import find_related_documents
from app.services.retriever import retrieve_chunks

logger = get_logger("services.qa_pipeline")


async def answer_question(
    question: str,
    db: AsyncSession,
    document_id: int | None = None,
    language: str | None = None,
) -> QueryResponse:
    """
    Full RAG pipeline: retrieve → build prompt → generate → return response.

    Args:
        question: User's question.
        db: Async database session.
        document_id: Optional — scope to a single document.
        language: Optional — desired response language.

    Returns:
        QueryResponse with answer, sources, confidence, and related docs.
    """
    # 1. Retrieve relevant chunks
    chunks = await retrieve_chunks(
        query=question,
        db=db,
        document_id=document_id,
    )

    # 2. Build prompt messages
    messages = build_qa_messages(
        question=question,
        context_chunks=chunks,
        language=language,
    )

    # 3. Generate answer via Groq
    raw_answer = await groq_client.chat_completion(
        messages=messages,
        temperature=0.2,
        max_tokens=2048,
    )

    # 4. Parse confidence from the answer
    confidence, clean_answer = _extract_confidence(raw_answer)

    # 5. Build source citations
    sources = [
        SourceCitation(
            document_id=chunk.document_id,
            document_name=chunk.document_name,
            page_number=chunk.page_number,
            chunk_text=chunk.content[:300],
            similarity_score=round(chunk.score, 3),
        )
        for chunk in chunks
    ]

    # 6. Find related documents
    doc_ids_used = list({c.document_id for c in chunks})
    related_docs = await find_related_documents(
        document_ids=doc_ids_used, db=db, limit=3
    )

    # 7. Log the query
    query_log = QueryLog(
        question=question,
        answer=clean_answer,
        confidence=confidence,
        document_ids=",".join(str(d) for d in doc_ids_used),
    )
    db.add(query_log)
    await db.flush()

    logger.info(
        "Q&A complete: confidence=%.2f, sources=%d, related=%d",
        confidence,
        len(sources),
        len(related_docs),
    )

    return QueryResponse(
        answer=clean_answer,
        confidence=confidence,
        sources=sources,
        related_documents=related_docs,
        query_id=query_log.id,
    )


def _extract_confidence(answer: str) -> tuple[float, str]:
    """
    Extract confidence score from the LLM's response.

    The QA prompt instructs the model to include a confidence line like:
    [CONFIDENCE: 0.85]

    Returns:
        (confidence_float, cleaned_answer_text)
    """
    import re

    confidence = 0.5  # default
    clean = answer

    pattern = r"\[CONFIDENCE:\s*([\d.]+)\]"
    match = re.search(pattern, answer, re.IGNORECASE)

    if match:
        try:
            confidence = float(match.group(1))
            confidence = max(0.0, min(1.0, confidence))
        except ValueError:
            pass
        clean = re.sub(pattern, "", answer, flags=re.IGNORECASE).strip()

    return confidence, clean
