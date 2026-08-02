"""
Document comparison endpoint (SRS Section 3.5, FR3).
Sends two documents' text to LLM for structured comparison.
"""
import json
import logging
from pathlib import Path
from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.models import DocumentRecord

logger = logging.getLogger("api.compare")
router = APIRouter(prefix="/compare", tags=["compare"])
UPLOAD_DIR = Path(settings.resolved_upload_dir)


class CompareRequest(BaseModel):
    doc_id_a: int
    doc_id_b: int
    language: Optional[str] = "en"


def _get_document_text(doc: DocumentRecord) -> str:
    """Get full text for a document — from disk if available, else text_preview."""
    file_path = UPLOAD_DIR / doc.filename
    if file_path.exists():
        ext = Path(doc.filename).suffix.lower()
        try:
            if ext == ".docx":
                from app.services.docx_extractor import extract_docx_info
                text, _ = extract_docx_info(file_path)
            else:
                from app.services.pdf_extractor import extract_pdf_info
                text, _ = extract_pdf_info(file_path)
            if text:
                return text
        except Exception:
            pass
    return doc.text_preview or ""


@router.post("")
def compare_documents(payload: CompareRequest, db: Session = Depends(get_db)):
    """Compare two documents and return structured differences."""
    doc_a = db.query(DocumentRecord).filter(DocumentRecord.id == payload.doc_id_a).first()
    doc_b = db.query(DocumentRecord).filter(DocumentRecord.id == payload.doc_id_b).first()

    if not doc_a:
        raise HTTPException(status_code=404, detail=f"Document A (id={payload.doc_id_a}) not found")
    if not doc_b:
        raise HTTPException(status_code=404, detail=f"Document B (id={payload.doc_id_b}) not found")

    text_a = _get_document_text(doc_a)
    text_b = _get_document_text(doc_b)

    if not text_a or not text_b:
        raise HTTPException(status_code=400, detail="One or both documents have no extractable text.")

    if not settings.api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured. Cannot perform AI comparison.")

    lang_map = {
        "hi": "Respond in Hindi (हिन्दी).",
        "mr": "Respond in Marathi (मराठी).",
    }
    lang_instr = lang_map.get(payload.language, "Respond in English.")

    # Truncate to fit within context window
    max_chars = 4000
    truncated_a = text_a[:max_chars]
    truncated_b = text_b[:max_chars]

    name_a = doc_a.original_name or doc_a.filename
    name_b = doc_b.original_name or doc_b.filename

    prompt = (
        f"You are PolicyPilot, an expert at comparing government policy documents.\n\n"
        f"DOCUMENT A: \"{name_a}\"\n"
        f"{'=' * 40}\n{truncated_a}\n{'=' * 40}\n\n"
        f"DOCUMENT B: \"{name_b}\"\n"
        f"{'=' * 40}\n{truncated_b}\n{'=' * 40}\n\n"
        f"{lang_instr}\n\n"
        "Compare these two documents thoroughly. Return ONLY valid JSON (no markdown fences) with this structure:\n"
        '{\n'
        '  "similarities": ["shared theme or provision 1", "shared theme 2"],\n'
        '  "differences": [\n'
        '    {"aspect": "aspect name", "doc_a": "what doc A says", "doc_b": "what doc B says"}\n'
        '  ],\n'
        '  "key_changes": ["critical change 1", "critical change 2"],\n'
        '  "recommendation": "Brief recommendation about which is more current or comprehensive",\n'
        '  "conflict_areas": ["area where documents directly contradict each other"]\n'
        '}'
    )

    try:
        from app.services.groq_client import GroqClient
        client = GroqClient(api_key=settings.api_key)
        raw = client.generate(prompt, model=settings.model_name).strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "similarities": [],
            "differences": [],
            "key_changes": [],
            "recommendation": raw if 'raw' in dir() else "Comparison failed — could not parse LLM output.",
            "conflict_areas": [],
        }
    except Exception as exc:
        logger.error("Document comparison failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(exc)}")

    return {
        "doc_a": {"id": doc_a.id, "name": name_a},
        "doc_b": {"id": doc_b.id, "name": name_b},
        **data,
    }
