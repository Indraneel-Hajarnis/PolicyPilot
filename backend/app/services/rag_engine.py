"""
Central RAG orchestrator — embedder → FAISS retrieval → Groq LLM → structured output.
All external dependencies (FAISS, SentenceTransformers, Groq) load lazily and degrade
gracefully if not installed or not configured.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger("rag_engine")

# ── Lazy singletons ──────────────────────────────────────────────────────────

_embedder = None
_vector_store = None
_groq_client = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from app.services.embedder import Embedder
            _embedder = Embedder()
            logger.info("Embedder (all-MiniLM-L6-v2) ready")
        except Exception as exc:
            logger.warning("Embedder unavailable: %s", exc)
    return _embedder


def _get_vector_store():
    global _vector_store
    if _vector_store is None:
        try:
            from app.services.vector_store import VectorStore
            _vector_store = VectorStore(Path(settings.vector_store_path))
            logger.info("FAISS VectorStore ready (%d vectors)", _vector_store.index.ntotal if _vector_store.index else 0)
        except Exception as exc:
            logger.warning("VectorStore unavailable: %s", exc)
    return _vector_store


def _get_groq():
    global _groq_client
    key = settings.api_key
    if _groq_client is None or getattr(_groq_client, '_api_key', None) != key:
        from app.services.groq_client import GroqClient
        _groq_client = GroqClient(api_key=key)
    return _groq_client


# ── Indexing ─────────────────────────────────────────────────────────────────

def index_document(text: str, doc_id: int) -> int:
    """Chunk → embed → add to FAISS. Returns number of indexed chunks."""
    if not text or not text.strip():
        return 0
    try:
        from app.services.chunker import split_text
        chunks = split_text(text, chunk_size=800, chunk_overlap=150)
        if not chunks:
            return 0

        embedder = _get_embedder()
        vs = _get_vector_store()
        if embedder is None or vs is None:
            return 0

        embeddings = embedder.embed(chunks)
        # Store full chunk text + doc_id/chunk_index as real metadata instead of
        # packing a truncated "doc_id::i::chunk[:100]" string (which threw away
        # everything past the first 100 characters of every chunk).
        metadatas = [
            {"doc_id": doc_id, "chunk_index": i, "text": chunk}
            for i, chunk in enumerate(chunks)
        ]
        vs.add(embeddings, metadatas)
        logger.info("Indexed %d chunks for doc_id=%d", len(chunks), doc_id)
        return len(chunks)
    except Exception as exc:
        logger.warning("Indexing failed for doc_id=%d: %s", doc_id, exc)
        return 0


# ── Q&A ──────────────────────────────────────────────────────────────────────

def answer_question(
    question: str,
    document_id: Optional[int] = None,
    language: str = "en",
) -> dict:
    """Full RAG: embed question → FAISS search → Groq LLM → structured answer."""
    sources = []
    context = ""
    confidence = 0.0

    # 1. Retrieve relevant chunks
    embedder = _get_embedder()
    vs = _get_vector_store()

    if embedder and vs and vs.index and vs.index.ntotal > 0:
        try:
            q_emb = embedder.embed([question])[0]
            # document_id is passed straight into the vector store so filtering
            # happens against the FULL candidate pool, not just a fixed top-6
            # global search that could exclude this document entirely.
            hits = vs.search(q_emb, top_k=6, document_id=document_id)
            for hit in hits:
                sim = round(1.0 / (1.0 + hit["distance"]), 3)
                sources.append({
                    "text": hit["text"],
                    "document_id": hit["doc_id"],
                    "chunk_index": hit.get("chunk_index"),
                    "score": sim,
                    "page": None,  # page-level tracking not yet implemented
                })
            context = "\n\n---\n\n".join(s["text"] for s in sources[:4])
            if sources:
                confidence = sources[0]["score"]
        except Exception as exc:
            logger.warning("Retrieval error: %s", exc)

    # 2. Language instruction
    lang_map = {
        "hi": "Respond ONLY in Hindi (हिन्दी). Use formal register.",
        "mr": "Respond ONLY in Marathi (मराठी). Use formal register.",
    }
    lang_instr = lang_map.get(language, "Respond in clear, professional English.")

    # 3. LLM generation
    active_key = settings.api_key
    if not active_key:
        answer = (
            "ℹ️ **AI Service Configuration Notice**\n\n"
            "Please configure your `GROQ_API_KEY` in the server environment settings to enable automated AI responses.\n\n"
            + (f"**Relevant Policy Passages Found:**\n\n> {context[:600]}..." if context else
               "_No relevant policy documents uploaded yet. Please upload a policy PDF to begin._")
        )
    elif not context:
        answer = (
            "I couldn't find relevant content in the indexed policy documents to answer this question.\n\n"
            "**Try:**\n"
            "- Uploading a policy PDF first\n"
            "- Rephrasing your question with more specific terms\n"
            "- Changing the Search Scope in the sidebar"
        )
        confidence = 0.0
    else:
        prompt = (
            f"You are PolicyPilot, an expert AI assistant for analyzing policy and legal documents.\n\n"
            f"POLICY CONTEXT (retrieved via FAISS semantic search):\n{context}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"{lang_instr}\n\n"
            "Instructions:\n"
            "- Answer based STRICTLY on the policy context provided.\n"
            "- Be precise, structured, and cite relevant clauses/sections.\n"
            "- Use Markdown formatting (bullets, bold key terms).\n"
            "- If the context doesn't fully answer the question, say so clearly."
        )
        try:
            groq = _get_groq()
            answer = groq.generate(prompt, model=settings.model_name)
            confidence = max(confidence, 0.78)
        except Exception as exc:
            logger.error("Groq generation error: %s", exc)
            answer = (
                f"⚠️ LLM generation failed: `{exc}`\n\n"
                f"**Retrieved context preview:**\n\n> {context[:500]}..."
            )

    return {
        "answer": answer,
        "sources": sources,
        "confidence": round(confidence, 3),
        "related_documents": [],
    }


# ── Summarization ─────────────────────────────────────────────────────────────

def summarize_document(text: str, filename: str, language: str = "en") -> dict:
    """Generate a structured AI summary using Groq LLM."""
    if not settings.api_key or not text.strip():
        return _placeholder_summary(filename, text)

    lang_map = {
        "hi": "Respond ONLY in Hindi (हिन्दी).",
        "mr": "Respond ONLY in Marathi (मराठी).",
    }
    lang_instr = lang_map.get(language, "Respond in English.")
    truncated = text[:7000]

    prompt = (
        f"You are PolicyPilot. Analyze this policy document and return a structured JSON summary.\n\n"
        f"DOCUMENT: {filename}\n"
        f"CONTENT:\n{truncated}\n\n"
        f"{lang_instr}\n\n"
        "Return ONLY valid JSON (no markdown fences) with this exact structure:\n"
        '{\n'
        '  "executive_summary": "2-3 sentence overview of the document",\n'
        '  "key_points": ["key point 1", "key point 2", "key point 3", "key point 4", "key point 5"],\n'
        '  "sections": [{"title": "Section Name", "content": "Brief summary of this section"}],\n'
        '  "important_dates": ["specific date or deadline mentioned"],\n'
        '  "action_items": ["required action or compliance step"],\n'
        '  "full_summary": "Comprehensive 200-word narrative summary of the entire document"\n'
        '}'
    )

    try:
        groq = _get_groq()
        raw = groq.generate(prompt, model=settings.model_name).strip()
        # Strip markdown code fences if the model wraps the JSON
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
        data = json.loads(raw)
        return data
    except Exception as exc:
        logger.error("Summary generation failed for '%s': %s", filename, exc)
        return _placeholder_summary(filename, text)


def _placeholder_summary(filename: str, text: str) -> dict:
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 30]
    return {
        "executive_summary": (
            f"'{filename}' has been indexed successfully. "
            "Add a GROQ_API_KEY to backend/.env to enable AI-powered structured summaries."
        ),
        "key_points": sentences[:5] or [
            "Document indexed into PolicyPilot.",
            "FAISS vector embeddings ready for semantic search.",
            "Tri-lingual Q&A available (EN / HI / MR).",
        ],
        "sections": [{"title": "Document Preview", "content": text[:500] or "No preview available."}],
        "important_dates": [],
        "action_items": [
            "Configure GROQ_API_KEY in backend/.env",
            "Ask questions about this policy via the Chat page",
            "Export this summary as JSON",
        ],
        "full_summary": "",
    }