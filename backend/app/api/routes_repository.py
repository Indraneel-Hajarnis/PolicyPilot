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

from app.db.database import get_db
from app.db.models import DocumentRecord

logger = logging.getLogger("api.repository")
router = APIRouter(prefix="/repository", tags=["repository"])
UPLOAD_DIR = Path("./data/uploads")
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


@router.post("/import")
def import_from_repository(
    payload: ImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Download a document from an external URL and ingest it into PolicyPilot.
    Follows the same pipeline as manual upload.
    """
    if not payload.url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Determine filename
    filename = payload.filename or payload.url.split("/")[-1] or "imported_document.pdf"
    extension = Path(filename).suffix.lower()
    if extension not in {".pdf", ".docx"}:
        # Default to PDF for unknown extensions
        filename = filename + ".pdf"
        extension = ".pdf"

    try:
        # Download the file
        resp = requests.get(payload.url, timeout=30, stream=True)
        resp.raise_for_status()
        contents = resp.content

        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Downloaded file is empty")

        # Save to disk
        save_path = UPLOAD_DIR / filename
        save_path.write_bytes(contents)
        file_size = len(contents)

        # Extract text
        if extension == ".docx":
            from app.services.docx_extractor import extract_docx_info
            extracted_text, page_count = extract_docx_info(save_path)
        else:
            from app.services.pdf_extractor import extract_pdf_info
            extracted_text, page_count = extract_pdf_info(save_path)

        # Detect language
        detected_lang = "en"
        if extracted_text:
            try:
                from app.services.language_utils import detect_language
                detected_lang = detect_language(extracted_text[:2000])
            except Exception:
                pass

        # Save to database
        record = DocumentRecord(
            filename=filename,
            original_name=filename,
            content_type="application/pdf" if extension == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=file_size,
            page_count=page_count,
            language=detected_lang,
            text_preview=extracted_text[:10000] if extracted_text else None,
            department=None,
            document_number=None,
            category="Resolution" if "gr" in payload.source.lower() else "Circular",
            status="active",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Background index
        if extracted_text:
            from app.api.routes_upload import _background_index
            background_tasks.add_task(_background_index, extracted_text, record.id, filename)

        return {
            "message": f"Document '{filename}' imported successfully",
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
