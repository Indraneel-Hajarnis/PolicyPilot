import logging
from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
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


def _background_index(text: str, doc_id: int, filename: str):
    """Run FAISS indexing asynchronously in the background."""
    try:
        from app.services.rag_engine import index_document
        chunk_count = index_document(text, doc_id)
        logger.info("Background indexing completed: %d chunks for '%s' (doc_id=%d)", chunk_count, filename, doc_id)
    except Exception as exc:
        logger.warning("Background indexing failed for '%s': %s", filename, exc)


@router.post("", response_model=DocumentRead)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Sanitize filename (removes directory paths if passed on Windows)
    clean_filename = Path(file.filename).name
    if not clean_filename or not clean_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid PDF file name.")

    try:
        # ── Save file to disk ──────────────────────────────────────────────────
        save_path = UPLOAD_DIR / clean_filename
        contents = file.file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

        save_path.write_bytes(contents)
        file_size = len(contents)

        # ── Extract text + page count ─────────────────────────────────────────
        extracted_text, page_count = extract_pdf_info(save_path)

        # ── Detect language ───────────────────────────────────────────────────
        detected_lang = "en"
        if extracted_text:
            try:
                detected_lang = detect_language(extracted_text[:2000])
            except Exception as lang_err:
                logger.warning("Language detection failed: %s", lang_err)

        # ── Persist metadata to database ──────────────────────────────────────
        record = DocumentRecord(
            filename=clean_filename,
            original_name=clean_filename,
            content_type=file.content_type or "application/pdf",
            file_size=file_size,
            page_count=page_count,
            language=detected_lang,
            text_preview=extracted_text[:10000] if extracted_text else None,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # ── Schedule background indexing to prevent HTTP timeouts ─────────────
        if extracted_text:
            background_tasks.add_task(_background_index, extracted_text, record.id, clean_filename)

        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error during PDF upload '%s': %s", file.filename, e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF document: {str(e)}")
