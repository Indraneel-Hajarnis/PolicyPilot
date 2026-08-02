"""
Bulk importer for Maharashtra Government Resolutions from orgpedia/mahGRs.

Downloads pre-extracted text files (.en.txt = English, .mr.txt = Marathi)
from the GitHub repository and ingests them into the PolicyPilot database
and FAISS vector store.

Usage (standalone):
    cd backend
    python -m app.services.bulk_importer --limit 10 --departments Finance_Department

Usage (via API):
    POST /api/repository/bulk-import
    {"limit": 10, "departments": ["Finance_Department"], "language": "en"}
"""

import logging
import time
from pathlib import Path
from typing import Optional

# pyrefly: ignore [missing-import]
import requests
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal
from app.db.models import DocumentRecord
from app.services.language_utils import detect_language

logger = logging.getLogger("bulk_importer")

GITHUB_API_BASE = "https://api.github.com/repos/orgpedia/mahGRs/contents"
RAW_BASE = "https://raw.githubusercontent.com/orgpedia/mahGRs/main"
UPLOAD_DIR = Path(settings.resolved_upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Rate-limit: GitHub API allows 60 requests/hour unauthenticated
GITHUB_HEADERS = {"Accept": "application/vnd.github.v3+json"}


def _list_departments() -> list[dict]:
    """Fetch all department directories from GRs/."""
    url = f"{GITHUB_API_BASE}/GRs"
    try:
        resp = requests.get(url, timeout=15, headers=GITHUB_HEADERS)
        resp.raise_for_status()
        return [
            {"name": item["name"], "path": item["path"]}
            for item in resp.json()
            if item.get("type") == "dir"
        ]
    except Exception as exc:
        logger.error("Failed to list departments: %s", exc)
        return []


def _list_department_files(dept_path: str, language: str = "en") -> list[dict]:
    """
    List all text files in a department folder.
    Filters by language suffix (e.g. '.en.txt' or '.mr.txt').
    """
    url = f"{GITHUB_API_BASE}/{dept_path}"
    try:
        resp = requests.get(url, timeout=30, headers=GITHUB_HEADERS)
        resp.raise_for_status()
        suffix = f".{language}.txt"
        files = []
        for item in resp.json():
            name = item.get("name", "")
            if item.get("type") == "file" and name.endswith(suffix):
                files.append({
                    "name": name,
                    "path": item["path"],
                    "download_url": item.get("download_url"),
                    "size": item.get("size", 0),
                })
        return files
    except Exception as exc:
        logger.error("Failed to list files in %s: %s", dept_path, exc)
        return []


def _download_text(download_url: str) -> Optional[str]:
    """Download text content from a raw GitHub URL."""
    try:
        resp = requests.get(download_url, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        logger.warning("Download failed for %s: %s", download_url, exc)
        return None


def _extract_gr_id(filename: str) -> str:
    """Extract the GR identifier from filename like '202101141237329905.pdf.en.txt'."""
    # Strip language suffix and .pdf extension
    return filename.split(".pdf")[0] if ".pdf" in filename else filename.split(".")[0]


def bulk_import(
    limit: int = 50,
    per_department_limit: int = 0,
    departments: Optional[list[str]] = None,
    language: str = "en",
    skip_existing: bool = True,
) -> dict:
    """
    Bulk import GR documents from orgpedia/mahGRs into PolicyPilot.

    Args:
        limit: Maximum total documents to import (0 = unlimited).
        per_department_limit: Max documents per department (0 = unlimited).
        departments: List of specific department names to import from.
                     If None/empty, imports from all departments.
        language: Language version to import ('en' or 'mr').
        skip_existing: If True, skip files already in the database.

    Returns:
        Summary dict with imported/skipped/failed counts and details.
    """
    db: Session = SessionLocal()
    results = {
        "imported": [],
        "skipped": [],
        "failed": [],
        "total_imported": 0,
        "total_skipped": 0,
        "total_failed": 0,
        "departments_processed": 0,
    }

    try:
        # ── List available departments ────────────────────────────────────
        all_departments = _list_departments()
        if not all_departments:
            results["error"] = "Could not fetch department list from GitHub"
            return results

        # Filter departments if specified
        if departments:
            dept_set = set(departments)
            target_depts = [d for d in all_departments if d["name"] in dept_set]
            if not target_depts:
                results["error"] = (
                    f"None of the specified departments found. "
                    f"Available: {[d['name'] for d in all_departments]}"
                )
                return results
        else:
            target_depts = all_departments

        logger.info(
            "Bulk import starting: %d departments, limit=%d, lang=%s",
            len(target_depts), limit, language,
        )

        total_imported = 0

        for dept in target_depts:
            if limit > 0 and total_imported >= limit:
                break

            dept_name = dept["name"].replace("_", " ")
            dept_imported = 0

            logger.info("Processing department: %s", dept_name)

            # ── List files in department ──────────────────────────────────
            files = _list_department_files(dept["path"], language)
            if not files:
                logger.info("No %s files found in %s, skipping", language, dept_name)
                continue

            results["departments_processed"] += 1

            for file_info in files:
                # Check limits
                if limit > 0 and total_imported >= limit:
                    break
                if per_department_limit > 0 and dept_imported >= per_department_limit:
                    break

                gr_id = _extract_gr_id(file_info["name"])
                # Use a clean filename for DB
                clean_filename = f"{gr_id}_{dept['name']}.txt"

                # ── Skip if already imported ──────────────────────────────
                if skip_existing:
                    existing = db.query(DocumentRecord).filter(
                        DocumentRecord.filename == clean_filename
                    ).first()
                    if existing:
                        results["skipped"].append({
                            "filename": clean_filename,
                            "department": dept_name,
                            "reason": "already exists",
                        })
                        continue

                # ── Download text ─────────────────────────────────────────
                download_url = file_info.get("download_url")
                if not download_url:
                    download_url = f"{RAW_BASE}/{file_info['path']}"

                text = _download_text(download_url)
                if not text or not text.strip():
                    results["failed"].append({
                        "filename": clean_filename,
                        "department": dept_name,
                        "reason": "empty or download failed",
                    })
                    continue

                # ── Detect language ───────────────────────────────────────
                detected_lang = language
                try:
                    detected_lang = detect_language(text[:2000])
                except Exception:
                    pass

                # ── Save text to disk ─────────────────────────────────────
                save_path = UPLOAD_DIR / clean_filename
                save_path.write_text(text, encoding="utf-8")

                # ── Extract metadata via heuristics ───────────────────────
                doc_num = None
                try:
                    from app.services.status_inference import extract_gr_metadata
                    h_meta = extract_gr_metadata(text)
                    doc_num = h_meta.get("document_number")
                except Exception:
                    pass

                # ── Create DB record ──────────────────────────────────────
                record = DocumentRecord(
                    filename=clean_filename,
                    original_name=file_info["name"],
                    content_type="text/plain",
                    file_size=len(text.encode("utf-8")),
                    page_count=1,
                    language=detected_lang,
                    text_preview=text[:10000],
                    department=dept_name,
                    document_number=doc_num or gr_id,
                    category="Resolution",
                    status="active",
                    is_repository_document=True,
                    source_key="github_mahgrs",
                    source_url=f"https://github.com/orgpedia/mahGRs/blob/main/{file_info['path']}",
                )
                db.add(record)
                db.commit()
                db.refresh(record)

                # ── Index into FAISS ──────────────────────────────────────
                try:
                    from app.services.rag_engine import index_document
                    doc_meta = {
                        "filename": record.filename,
                        "document_number": record.document_number,
                        "department": record.department,
                        "category": record.category,
                        "issue_date": record.issue_date,
                    }
                    chunk_count = index_document(text, record.id, doc_meta=doc_meta)
                    logger.info(
                        "Indexed '%s': %d chunks (doc_id=%d)",
                        clean_filename, chunk_count, record.id,
                    )
                except Exception as idx_err:
                    logger.warning("Indexing failed for %s: %s", clean_filename, idx_err)

                results["imported"].append({
                    "id": record.id,
                    "filename": clean_filename,
                    "department": dept_name,
                    "document_number": record.document_number,
                    "size": len(text),
                })

                total_imported += 1
                dept_imported += 1

                # Be nice to GitHub API rate limits
                time.sleep(0.5)

            logger.info(
                "Department '%s': imported %d documents", dept_name, dept_imported,
            )

        # ── Final summary ─────────────────────────────────────────────────
        results["total_imported"] = len(results["imported"])
        results["total_skipped"] = len(results["skipped"])
        results["total_failed"] = len(results["failed"])

        logger.info(
            "Bulk import complete: %d imported, %d skipped, %d failed across %d departments",
            results["total_imported"],
            results["total_skipped"],
            results["total_failed"],
            results["departments_processed"],
        )

        return results

    except Exception as exc:
        logger.error("Bulk import error: %s", exc, exc_info=True)
        results["error"] = str(exc)
        return results
    finally:
        db.close()


def list_available_departments() -> list[dict]:
    """Return the list of department names available in the GitHub repo."""
    depts = _list_departments()
    return [
        {"name": d["name"], "display_name": d["name"].replace("_", " ")}
        for d in depts
    ]


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    parser = argparse.ArgumentParser(description="Bulk import Maharashtra GRs from GitHub")
    parser.add_argument("--limit", type=int, default=10, help="Max documents to import (default: 10)")
    parser.add_argument("--per-dept", type=int, default=0, help="Max per department (0=unlimited)")
    parser.add_argument("--departments", nargs="*", help="Specific department names")
    parser.add_argument("--language", choices=["en", "mr"], default="en", help="Language version")
    parser.add_argument("--no-skip", action="store_true", help="Don't skip existing documents")
    parser.add_argument("--list-departments", action="store_true", help="List available departments and exit")
    args = parser.parse_args()

    if args.list_departments:
        depts = list_available_departments()
        print(f"\n{'='*60}")
        print(f"  Available Departments ({len(depts)} total)")
        print(f"{'='*60}")
        for i, d in enumerate(depts, 1):
            print(f"  {i:2d}. {d['display_name']}")
        print()
        sys.exit(0)

    result = bulk_import(
        limit=args.limit,
        per_department_limit=args.per_dept,
        departments=args.departments,
        language=args.language,
        skip_existing=not args.no_skip,
    )

    print(f"\n{'='*60}")
    print(f"  Bulk Import Summary")
    print(f"{'='*60}")
    print(f"  Departments processed : {result['departments_processed']}")
    print(f"  Documents imported    : {result['total_imported']}")
    print(f"  Documents skipped     : {result['total_skipped']}")
    print(f"  Documents failed      : {result['total_failed']}")
    if result.get("error"):
        print(f"  Error                 : {result['error']}")
    print(f"{'='*60}\n")

    if result["imported"]:
        print("  Imported documents:")
        for doc in result["imported"]:
            print(f"    - [{doc['id']}] {doc['filename']} ({doc['department']})")
