from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.database import get_db
from app.db.models import DocumentRecord
from app.db.schemas import DocumentCreate, DocumentRead
from app.services.pdf_extractor import extract_text_from_pdf

router = APIRouter(prefix="/upload", tags=["upload"])
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("", response_model=DocumentRead)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    save_path = UPLOAD_DIR / file.filename
    contents = file.file.read()
    save_path.write_bytes(contents)

    extracted_text = extract_text_from_pdf(save_path)

    record = DocumentRecord(
        filename=file.filename,
        content_type=file.content_type,
        text_preview=extracted_text[:2000] if extracted_text else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record
