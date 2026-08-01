"""
Central RAG orchestrator — embedder → FAISS retrieval → Groq LLM → structured output.
All external dependencies (FAISS, SentenceTransformers, Groq) load lazily and degrade
gracefully if not installed or not configured.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict

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

def index_document(
    text: str,
    doc_id: int,
    page_tuples: Optional[List[Tuple[int, str]]] = None,
    doc_meta: Optional[Dict] = None,
) -> int:
    """Chunk → embed → add to FAISS. Returns number of indexed chunks."""
    if not text or not text.strip():
        return 0
    try:
        from app.services.chunker import split_text, split_page_tuples
        if page_tuples:
            raw_chunks = split_page_tuples(page_tuples, chunk_size=1000, chunk_overlap=200)
        else:
            simple_chunks = split_text(text, chunk_size=1000, chunk_overlap=200)
            raw_chunks = [
                {"text": chunk, "page_number": 1, "chunk_index": i}
                for i, chunk in enumerate(simple_chunks)
            ]

        if not raw_chunks:
            return 0

        embedder = _get_embedder()
        vs = _get_vector_store()
        if embedder is None or vs is None:
            return 0

        texts_to_embed = [c["text"] for c in raw_chunks]
        embeddings = embedder.embed(texts_to_embed)

        meta_base = doc_meta or {}
        metadatas = [
            {
                "doc_id": doc_id,
                "chunk_index": c["chunk_index"],
                "page_number": c.get("page_number", 1),
                "text": c["text"],
                "filename": meta_base.get("filename"),
                "document_number": meta_base.get("document_number"),
                "department": meta_base.get("department"),
                "category": meta_base.get("category"),
                "issue_date": meta_base.get("issue_date"),
            }
            for c in raw_chunks
        ]
        vs.add(embeddings, metadatas)
        logger.info("Indexed %d chunks for doc_id=%d", len(raw_chunks), doc_id)
        return len(raw_chunks)
    except Exception as exc:
        logger.warning("Indexing failed for doc_id=%d: %s", doc_id, exc)
        return 0


# ── Q&A ──────────────────────────────────────────────────────────────────────

def answer_question(
    question: str,
    document_id: Optional[int] = None,
    language: str = "en",
    conversation_history: Optional[List[Dict]] = None,
) -> dict:
    """Full RAG: embed question → FAISS search → Groq LLM → structured answer."""
    sources = []
    context = ""
    confidence = 0.0
    conflicts = []

    # 1. Retrieve relevant chunks with cross-lingual query expansion
    embedder = _get_embedder()
    vs = _get_vector_store()

    if embedder and vs and vs.index and vs.index.ntotal > 0:
        try:
            from app.services.language_utils import translate_and_expand_query
            search_query = translate_and_expand_query(question, target_lang=language)
            q_emb = embedder.embed([search_query])[0]
            hits = vs.search(q_emb, top_k=8, document_id=document_id)

            min_thresh = float(getattr(settings, "similarity_threshold", 0.28))
            for hit in hits:
                # FAISS L2 distance on normalized vectors -> exact cosine similarity
                dist = hit.get("distance", 2.0)
                sim = round(max(0.0, 1.0 - (dist / 2.0)), 3)
                if sim >= min_thresh:
                    sources.append({
                        "text": hit["text"],
                        "document_id": hit["doc_id"],
                        "chunk_index": hit.get("chunk_index"),
                        "score": sim,
                        "page": hit.get("page_number", 1),
                        "page_number": hit.get("page_number", 1),
                        "filename": hit.get("filename"),
                        "document_number": hit.get("document_number"),
                        "department": hit.get("department"),
                        "issue_date": hit.get("issue_date"),
                    })

            if sources:
                sources.sort(key=lambda x: x["score"], reverse=True)
                confidence = sources[0]["score"]
                context_passages = []
                for s in sources[:5]:
                    prefix = f"[Doc #{s['document_id']} | Page {s['page_number']}]"
                    if s.get("document_number"):
                        prefix += f" [GR: {s['document_number']}]"
                    context_passages.append(f"{prefix}\n{s['text']}")
                context = "\n\n---\n\n".join(context_passages)
        except Exception as exc:
            logger.warning("Retrieval error: %s", exc)

    # 2. Language instruction
    lang_map = {
        "hi": "Respond ONLY in Hindi (हिन्दी). Use formal register.",
        "mr": "Respond ONLY in Marathi (मराठी). Use formal register.",
    }
    lang_instr = lang_map.get(language, "Respond in clear, professional English.")

    # 3. LLM generation or grounded refusal
    active_key = settings.api_key

    if not sources or not context.strip():
        # SRS Grounded Refusal — NO ungrounded parametric general knowledge
        if language == "mr":
            answer = (
                "⚠️ **शासकीय दस्तऐवज उपलब्ध नाहीत (Insufficient Authenticated Evidence)**\n\n"
                "तुमच्या प्रश्नासाठी केंद्रीय भांडारामध्ये संबंधित अधिकृत शासन निर्णय किंवा परिपत्रकाचा संदर्भ आढळला नाही. "
                "अचूक माहितीसाठी कृपया संबंधित शासन निर्णय अपलोड करा."
            )
        elif language == "hi":
            answer = (
                "⚠️ **प्रमाणित दस्तावेज़ उपलब्ध नहीं हैं (Insufficient Authenticated Evidence)**\n\n"
                "आपके प्रश्न के लिए केंद्रीय रिपोजिटरी में कोई प्रासंगिक सरकारी संकल्प या परिपत्रक नहीं मिला। "
                "कृपया प्रासंगिक दस्तावेज़ अपलोड करें।"
            )
        else:
            answer = (
                "⚠️ **Insufficient Authenticated Evidence**\n\n"
                "No matching policy passages or authenticated evidence were found in the repository for your query. "
                "To maintain strict regulatory grounding, answers cannot be generated without indexed source context.\n\n"
                "**Recommended Actions:**\n"
                "- Try rephrasing your question with specific terms or GR reference numbers.\n"
                "- Import or upload the relevant Government Resolution (GR) via the Repository page."
            )
        return {
            "answer": answer,
            "sources": [],
            "confidence": 0.0,
            "related_documents": [],
            "conflicts": [],
        }

    if not active_key:
        answer = (
            "ℹ️ **AI Service Configuration Notice**\n\n"
            "Please configure your `GROQ_API_KEY` in the server environment settings to enable automated AI responses.\n\n"
            f"**Relevant Policy Passages Found:**\n\n> {context[:600]}..."
        )
    else:
        # Context IS available — perform RAG synthesis
        system_prompt = (
            f"You are PolicyPilot, an expert AI assistant for analyzing government policy, insurance, legal, and compliance documents.\n\n"
            f"RETRIEVED POLICY CONTEXT (from semantic search over authenticated repository documents):\n"
            f"{'=' * 60}\n"
            f"{context}\n"
            f"{'=' * 60}\n\n"
            f"{lang_instr}\n\n"
            "INSTRUCTIONS:\n"
            "- Use the retrieved context as your ONLY source of truth. Rely strictly on facts mentioned in the context.\n"
            "- Provide clear, structured, professional answers using Markdown.\n"
            "- Always cite specific Page Numbers and GR Document Numbers when referencing facts.\n"
            "- If the context contains conflicting provisions between different documents or dates, highlight the conflict clearly under a '⚠️ **Conflicting Policy Provisions**' section.\n"
            "- Never fabricate policies or speculate beyond the provided text."
        )
        try:
            groq = _get_groq()
            messages = _build_messages(conversation_history, system_prompt, question)
            answer = groq.generate_chat(messages, model=settings.model_name)

            # Check for conflict objects if multiple document sources exist
            doc_ids = {s["document_id"] for s in sources if s.get("document_id")}
            if len(doc_ids) > 1 and ("conflict" in answer.lower() or "supersed" in answer.lower() or "amend" in answer.lower()):
                conflicts.append({
                    "description": "Cross-document policy differences detected between retrieved sections.",
                    "document_ids": list(doc_ids),
                })

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
        "conflicts": conflicts,
    }



def _build_messages(
    conversation_history: Optional[List[Dict]],
    system_prompt: str,
    current_question: Optional[str] = None,
) -> List[Dict]:
    """
    Build the messages list for the Groq chat API.
    Includes conversation history for multi-turn context.
    """
    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        for turn in conversation_history[-10:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": str(content)})

    if current_question:
        messages.append({"role": "user", "content": current_question})

    return messages


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