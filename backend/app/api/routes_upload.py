import logging
from pathlib import Path
from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DocumentRecord
from app.db.schemas import DocumentRead
from app.services.language_utils import detect_language
from app.services.pdf_extractor import extract_pdf_info

logger = logging.getLogger("api.upload")
router = APIRouter(prefix="/upload", tags=["upload"])
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _background_index(text: str, doc_id: int, filename: str, page_tuples=None, doc_meta=None):
    """Run FAISS indexing asynchronously in the background."""
    try:
        from app.services.rag_engine import index_document
        chunk_count = index_document(text, doc_id, page_tuples=page_tuples, doc_meta=doc_meta)
        logger.info(
            "Background indexing completed: %d chunks for '%s' (doc_id=%d)",
            chunk_count, filename, doc_id,
        )
    except Exception as exc:
        logger.error(
            "Background indexing FAILED for '%s' (doc_id=%d): %s",
            filename, doc_id, exc, exc_info=True,
        )


def _extract_file_info(save_path: Path, extension: str):
    """Route to the correct extractor based on file extension."""
    if extension == ".txt":
        text = save_path.read_text(encoding="utf-8", errors="ignore")
        return text, 1, None, False, 0.0
    elif extension == ".docx":
        from app.services.docx_extractor import extract_docx_detailed
        return extract_docx_detailed(save_path)
    else:
        try:
            from app.services.pdf_extractor import extract_pdf_detailed
            return extract_pdf_detailed(save_path)
        except Exception:
            text = save_path.read_text(encoding="utf-8", errors="ignore")
            return text, 1, None, False, 0.0


def _content_type_for_ext(extension: str) -> str:
    """Return MIME type for known extensions."""
    if extension == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "application/pdf"


@router.post("", response_model=DocumentRead)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    department: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    clean_filename = Path(file.filename).name
    extension = Path(clean_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{extension}'. Only PDF and DOCX files are supported."
        )

    try:
        save_path = UPLOAD_DIR / clean_filename
        contents = file.file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

        save_path.write_bytes(contents)
        file_size = len(contents)

        # ── Extract text + page count + OCR details ────────────────────────────
        extracted_text, page_count, page_tuples, ocr_used, ocr_conf = _extract_file_info(save_path, extension)

        # ── Detect language ───────────────────────────────────────────────────
        detected_lang = "en"
        if extracted_text:
            try:
                detected_lang = detect_language(extracted_text[:2000])
            except Exception as lang_err:
                logger.warning("Language detection failed: %s", lang_err)

        # ── Auto-extract metadata via LLM or heuristics if not provided ─────
        if extracted_text:
            from app.services.status_inference import extract_gr_metadata
            h_meta = extract_gr_metadata(extracted_text)
            if not document_number and h_meta.get("document_number"):
                document_number = h_meta["document_number"]
            if not department and h_meta.get("department"):
                department = h_meta["department"]

            if not department or not category:
                try:
                    auto_meta = _auto_extract_metadata(extracted_text[:3000])
                    if not department and auto_meta.get("department"):
                        department = auto_meta["department"]
                    if not category and auto_meta.get("category"):
                        category = auto_meta["category"]
                    if not document_number and auto_meta.get("document_number"):
                        document_number = auto_meta["document_number"]
                except Exception as meta_err:
                    logger.warning("Auto metadata extraction failed: %s", meta_err)

        # ── Persist record ────────────────────────────────────────────────────
        record = DocumentRecord(
            filename=clean_filename,
            original_name=clean_filename,
            content_type=file.content_type or _content_type_for_ext(extension),
            file_size=file_size,
            page_count=page_count,
            language=detected_lang,
            text_preview=extracted_text[:10000] if extracted_text else None,
            department=department,
            document_number=document_number,
            category=category or "Resolution",
            status="active",
            ocr_used=ocr_used,
            ocr_confidence=ocr_conf,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # ── Infer relationships ────────────────────────────────────────────────
        if extracted_text:
            try:
                from app.services.status_inference import infer_document_relationships
                infer_document_relationships(record, extracted_text, db)
            except Exception as rel_err:
                logger.warning("Relationship inference warning: %s", rel_err)

        # ── Schedule background indexing with page provenance ──────────────────
        if extracted_text:
            doc_meta = {
                "filename": record.filename,
                "document_number": record.document_number,
                "department": record.department,
                "category": record.category,
                "issue_date": record.issue_date,
            }
            background_tasks.add_task(_background_index, extracted_text, record.id, clean_filename, page_tuples, doc_meta)

        return record


    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error during file upload '%s': %s", file.filename, e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


def _auto_extract_metadata(text_preview: str) -> dict:
    """Use a simple heuristic + LLM to extract department, category, document_number from text."""
    import json
    from app.config import settings

    if not settings.api_key:
        return {}

    try:
        from app.services.groq_client import GroqClient
        client = GroqClient(api_key=settings.api_key)
        prompt = (
            "Extract metadata from this government/policy document text. "
            "Return ONLY valid JSON (no markdown) with these fields:\n"
            '{"department": "department name or null", "document_number": "GR/circular number or null", "category": "one of: Policy, Circular, Resolution, Notification, Amendment, Report, Guidelines, Other"}\n\n'
            f"DOCUMENT TEXT:\n{text_preview}"
        )
        raw = client.generate(prompt, model="llama-3.1-8b-instant").strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
        return json.loads(raw)
    except Exception:
        return {}


@router.post("/reindex", tags=["upload"])
def reindex_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Re-index every document already in the DB from its saved file on disk.
    Useful after wiping the FAISS index without losing uploaded files.
    """
    records = db.query(DocumentRecord).all()
    queued = []
    skipped = []

    for record in records:
        file_path = UPLOAD_DIR / record.filename
        if not file_path.exists():
            skipped.append({"id": record.id, "filename": record.filename, "reason": "file not found on disk"})
            continue

        extension = Path(record.filename).suffix.lower()
        extracted_text, page_count, page_tuples, ocr_used, ocr_conf = _extract_file_info(file_path, extension)
        if not extracted_text or not extracted_text.strip():
            skipped.append({"id": record.id, "filename": record.filename, "reason": "no text extracted"})
            continue

        doc_meta = {
            "filename": record.filename,
            "document_number": record.document_number,
            "department": record.department,
            "category": record.category,
            "issue_date": record.issue_date,
        }
        background_tasks.add_task(_background_index, extracted_text, record.id, record.filename, page_tuples, doc_meta)
        queued.append({"id": record.id, "filename": record.filename})

    logger.info("Reindex triggered: %d queued, %d skipped", len(queued), len(skipped))
    return {
        "message": f"Re-indexing {len(queued)} document(s) in the background.",
        "queued": queued,
        "skipped": skipped,
    }
