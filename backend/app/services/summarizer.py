"""
Structured document summarization using the Groq LLM.
"""

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DocumentNotFoundError, LLMError
from app.core.logging_config import get_logger
from app.db.models import Chunk, Document
from app.db.schemas import SummaryResponse, SummarySection
from app.prompts.summary_prompt import build_summary_messages
from app.services.groq_client import groq_client
from app.services.language_utils import get_language_name, translate_text

logger = get_logger("services.summarizer")

async def summarize_document(
    document_id: int,
    db: AsyncSession,
    language: str | None = "en",
) -> SummaryResponse:
    """
    Generate a structured summary of a policy document in the requested language.
    """
    # 1. Load the document
    doc = await db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)

    # 2. Load all chunks for the document (ordered by chunk_index)
    stmt = (
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()

    if not chunks:
        raise DocumentNotFoundError(
            f"No text chunks found for document {document_id}"
        )

    # 3. Combine chunk texts
    full_text = "\n\n".join(c.content for c in chunks)
    if len(full_text) > 12000:
        full_text = full_text[:12000] + "\n\n[... content truncated for summarization ...]"

    # 4. Build prompt and call LLM
    messages = build_summary_messages(
        document_name=doc.original_name,
        document_text=full_text,
    )

    if language and language != "en":
        target_name = get_language_name(language)
        messages[0]["content"] += f"\n\nIMPORTANT: Produce all text in {target_name}. Ensure JSON key names stay in English, but string values are in {target_name}."

    raw_response = await groq_client.chat_completion(
        messages=messages,
        temperature=0.3,
        max_tokens=3000,
    )

    # 5. Parse the structured JSON response
    summary = _parse_summary_response(raw_response, document_id, doc.original_name)

    logger.info("Generated summary for document '%s' in language '%s'", doc.original_name, language)
    return summary


def _parse_summary_response(
    raw: str, document_id: int, document_name: str
) -> SummaryResponse:
    """Parse the LLM's JSON response into a SummaryResponse."""
    # Try to extract JSON from the response
    try:
        # Handle responses wrapped in markdown code blocks
        json_str = raw
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        sections = [
            SummarySection(title=s.get("title", ""), content=s.get("content", ""))
            for s in data.get("sections", [])
        ]

        return SummaryResponse(
            document_id=document_id,
            document_name=document_name,
            title=data.get("title", document_name),
            key_points=data.get("key_points", []),
            sections=sections,
            important_dates=data.get("important_dates", []),
            action_items=data.get("action_items", []),
            full_summary=data.get("full_summary", ""),
        )
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        logger.warning("Failed to parse structured summary, using raw text: %s", e)
        # Fallback — return the raw text as the full summary
        return SummaryResponse(
            document_id=document_id,
            document_name=document_name,
            title=document_name,
            full_summary=raw,
        )
