from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException 
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DocumentRecord

router = APIRouter(prefix="/summary", tags=["summary"])
UPLOAD_DIR = Path("./data/uploads")


@router.get("/{document_id}")
def get_summary(document_id: int, language: str = "en", db: Session = Depends(get_db)):
    """Return an AI-generated structured summary for a document."""
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    fname = document.original_name or document.filename

    # Prefer reading full text from disk if available
    full_text = ""
    file_path = UPLOAD_DIR / document.filename
    if file_path.exists():
        try:
            from app.services.pdf_extractor import extract_pdf_info
            full_text, _ = extract_pdf_info(file_path)
        except Exception:
            full_text = document.text_preview or ""
    else:
        full_text = document.text_preview or ""

    from app.services.rag_engine import summarize_document
    data = summarize_document(text=full_text, filename=fname, language=language)

    # Merge metadata into the response
    data.setdefault("document_id", document_id)
    data.setdefault("document_name", fname)
    data["filename"] = fname
    data["language"] = language
    data["page_count"] = document.page_count or 0

    return data
