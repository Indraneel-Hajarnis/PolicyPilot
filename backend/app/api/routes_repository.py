"""
Centralized Repository & Open Dataset integration (SRS Section 3.7).
Provides endpoints to browse and import documents from external sources:
- GitHub: orgpedia/mahGRs
- Maharashtra GR Portal: gr.maharashtra.gov.in
- DTE Maharashtra: dte.maharashtra.gov.in
"""
import logging
from pathlib import Path
from typing import Optional

# pyrefly: ignore [missing-import]
import requests
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.models import DocumentRecord

logger = logging.getLogger("api.repository")
router = APIRouter(prefix="/repository", tags=["repository"])
UPLOAD_DIR = Path(settings.resolved_upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Source definitions ────────────────────────────────────────────────────────

SOURCES = [
    {
        "id": "github_mahgrs",
        "name": "Maharashtra GRs (GitHub)",
        "description": "Historical Maharashtra Government Resolutions from orgpedia/mahGRs repository",
        "url": "https://github.com/orgpedia/mahGRs",
        "type": "github",
    },
    {
        "id": "gr_maharashtra",
        "name": "Maharashtra GR Portal",
        "description": "Official Maharashtra Government Resolutions portal",
        "url": "https://gr.maharashtra.gov.in",
        "type": "portal",
    },
    {
        "id": "dte_maharashtra",
        "name": "DTE Maharashtra",
        "description": "Directorate of Technical Education — circulars and orders",
        "url": "https://dte.maharashtra.gov.in",
        "type": "portal",
    },
]


class ImportRequest(BaseModel):
    url: str
    source: str
    filename: Optional[str] = None


class BulkImportRequest(BaseModel):
    limit: int = 50
    per_department_limit: int = 0
    departments: Optional[list[str]] = None
    language: str = "en"


@router.get("/sources")
def get_sources():
    """Return available external document sources."""
    return SOURCES


@router.get("/github")
def browse_github_repo(path: str = "", limit: int = 50):
    """
    Browse the orgpedia/mahGRs GitHub repository.
    Returns list of files/directories at the given path.
    """
    api_url = f"https://api.github.com/repos/orgpedia/mahGRs/contents/{path}"
    try:
        resp = requests.get(api_url, timeout=15, headers={"Accept": "application/vnd.github.v3+json"})
        if resp.status_code == 404:
            return {"items": [], "error": "Path not found in repository"}
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list):
            items = []
            for item in data[:limit]:
                items.append({
                    "name": item.get("name", ""),
                    "path": item.get("path", ""),
                    "type": item.get("type", ""),  # "file" or "dir"
                    "size": item.get("size", 0),
                    "download_url": item.get("download_url"),
                    "html_url": item.get("html_url"),
                })
            return {"items": items, "current_path": path}
        else:
            # Single file
            return {
                "items": [{
                    "name": data.get("name", ""),
                    "path": data.get("path", ""),
                    "type": "file",
                    "size": data.get("size", 0),
                    "download_url": data.get("download_url"),
                    "html_url": data.get("html_url"),
                }],
                "current_path": path,
            }
    except requests.RequestException as exc:
        logger.warning("GitHub API error: %s", exc)
        return {"items": [], "error": f"Failed to fetch from GitHub: {str(exc)}"}


@router.post("/seed")
def trigger_seed_repository(db: Session = Depends(get_db)):
    """Seed the central policy document corpus if empty."""
    from app.services.seed_repository import seed_central_repository
    res = seed_central_repository(db)
    return res


@router.get("/documents")
def list_repository_documents(db: Session = Depends(get_db)):
    """List all centrally ingested repository documents."""
    docs = db.query(DocumentRecord).filter(DocumentRecord.is_repository_document == True).order_by(DocumentRecord.uploaded_at.desc()).all()
    return docs


@router.post("/import")
def import_from_repository(
    payload: ImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Download a document from an external URL and ingest it into PolicyPilot central repository.
    """
    if not payload.url:
        raise HTTPException(status_code=400, detail="URL is required")

    filename = payload.filename or payload.url.split("/")[-1] or "imported_document.pdf"
    extension = Path(filename).suffix.lower()
    if extension not in {".pdf", ".docx"}:
        filename = filename + ".pdf"
        extension = ".pdf"

    try:
        resp = requests.get(payload.url, timeout=30, stream=True)
        resp.raise_for_status()
        contents = resp.content

        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Downloaded file is empty")

        save_path = UPLOAD_DIR / filename
        save_path.write_bytes(contents)
        file_size = len(contents)

        if extension == ".docx":
            from app.services.docx_extractor import extract_docx_detailed
            extracted_text, page_count, page_tuples, ocr_used, ocr_conf = extract_docx_detailed(save_path)
        else:
            from app.services.pdf_extractor import extract_pdf_detailed
            extracted_text, page_count, page_tuples, ocr_used, ocr_conf = extract_pdf_detailed(save_path)

        detected_lang = "en"
        if extracted_text:
            try:
                from app.services.language_utils import detect_language
                detected_lang = detect_language(extracted_text[:2000])
            except Exception:
                pass

        dept = None
        doc_num = None
        if extracted_text:
            from app.services.status_inference import extract_gr_metadata
            h_meta = extract_gr_metadata(extracted_text)
            doc_num = h_meta.get("document_number")
            dept = h_meta.get("department")

        record = DocumentRecord(
            filename=filename,
            original_name=filename,
            content_type="application/pdf" if extension == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=file_size,
            page_count=page_count,
            language=detected_lang,
            text_preview=extracted_text[:10000] if extracted_text else None,
            department=dept,
            document_number=doc_num,
            category="Resolution" if "gr" in payload.source.lower() else "Circular",
            status="active",
            is_repository_document=True,
            source_key=payload.source,
            source_url=payload.url,
            ocr_used=ocr_used,
            ocr_confidence=ocr_conf,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        if extracted_text:
            try:
                from app.services.status_inference import infer_document_relationships
                infer_document_relationships(record, extracted_text, db)
            except Exception:
                pass

        if extracted_text:
            from app.api.routes_upload import _background_index
            doc_meta = {
                "filename": record.filename,
                "document_number": record.document_number,
                "department": record.department,
                "category": record.category,
                "issue_date": record.issue_date,
            }
            background_tasks.add_task(_background_index, extracted_text, getattr(record, "id"), filename, page_tuples, doc_meta)

        return {
            "message": f"Document '{filename}' imported successfully into central repository",
            "document": {
                "id": record.id,
                "filename": record.filename,
                "original_name": record.original_name,
                "page_count": record.page_count,
                "file_size": record.file_size,
                "source": payload.source,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Import failed from %s: %s", payload.url, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Import failed: {str(exc)}")


# ── Bulk Import from GitHub (orgpedia/mahGRs) ────────────────────────────────

@router.get("/bulk-import/departments")
def list_bulk_import_departments():
    """List available department folders from the orgpedia/mahGRs repository."""
    from app.services.bulk_importer import list_available_departments
    depts = list_available_departments()
    return {"departments": depts, "total": len(depts)}


@router.post("/bulk-import")
def bulk_import_from_github(payload: BulkImportRequest):
    """
    Bulk download and index GR documents from orgpedia/mahGRs GitHub repository.
    Downloads pre-extracted text files (.en.txt or .mr.txt) and ingests them
    into the PolicyPilot database and FAISS vector store.
    """
    # Safety cap to prevent accidental huge imports
    safe_limit = min(payload.limit, 200) if payload.limit > 0 else 200

    from app.services.bulk_importer import bulk_import
    result = bulk_import(
        limit=safe_limit,
        per_department_limit=payload.per_department_limit,
        departments=payload.departments,
        language=payload.language,
    )

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "message": f"Bulk import complete: {result['total_imported']} imported, {result['total_skipped']} skipped, {result['total_failed']} failed",
        "summary": {
            "departments_processed": result["departments_processed"],
            "total_imported": result["total_imported"],
            "total_skipped": result["total_skipped"],
            "total_failed": result["total_failed"],
        },
        "imported": result["imported"],
        "skipped": result["skipped"][:20],  # Limit response size
        "failed": result["failed"],
    }

