from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DocumentRecord
from app.db.schemas import DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_DIR = Path("./data/uploads")


class StatusUpdate(BaseModel):
    status: str  # active, amended, superseded, draft


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    return db.query(DocumentRecord).order_by(DocumentRecord.uploaded_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully", "id": document_id}


# ── Document Download (SRS Section 3.7, FR4) ─────────────────────────────────

@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """Serve the original uploaded file for download."""
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = UPLOAD_DIR / document.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk. It may have been removed.")

    return FileResponse(
        path=str(file_path),
        filename=document.original_name or document.filename,
        media_type=document.content_type or "application/octet-stream",
    )


# ── Document Status (SRS Section 3.5, FR5) ───────────────────────────────────

@router.patch("/{document_id}/status")
def update_document_status(document_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    """Update the legal status of a document."""
    valid_statuses = {"active", "amended", "superseded", "draft"}
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Must be one of: {', '.join(valid_statuses)}"
        )

    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = payload.status
    db.commit()
    db.refresh(document)
    return {"message": f"Status updated to '{payload.status}'", "id": document_id, "status": payload.status}
