"""
Runtime startup initialization for PolicyPilot.

Checks whether the FAISS vector index already exists (pre-computed during
Docker build via scripts/preseed.py). If not, seeds the database and FAISS
index from the bundled documents in seed_data/.

This module is called from the FastAPI lifespan handler in app/main.py.
"""
import logging
import shutil
from pathlib import Path

from app.config import settings

logger = logging.getLogger("startup")


def initialize_data() -> None:
    """
    Check-or-seed startup flow:
    1. If FAISS index exists → data was pre-seeded (Docker build) → done.
    2. If not → process all files in seed_data/, create DB records,
       generate embeddings, build FAISS index.
    """
    faiss_index_file = Path(settings.resolved_vector_store_path) / "index.faiss"
    id_map_file = Path(settings.resolved_vector_store_path) / "id_map.pkl"

    if faiss_index_file.exists() and id_map_file.exists():
        logger.info(
            "FAISS index found at %s — loading pre-computed data",
            faiss_index_file,
        )
        
        # Eager load heavy ML models during startup so the first API request doesn't timeout
        try:
            logger.info("Eagerly loading Embedder and VectorStore...")
            from app.services.rag_engine import _get_embedder, _get_vector_store
            _get_embedder()
            _get_vector_store()
        except Exception as exc:
            logger.warning("Failed to eager load models: %s", exc)
            
        return

    logger.info("No FAISS index found — seeding from bundled documents...")
    _seed_from_bundled_documents()


def _seed_from_bundled_documents() -> None:
    """
    Process all files in seed_data/ directory:
    1. Create DocumentRecord in SQLite for each file
    2. Copy file to uploads/ directory
    3. Chunk → Embed → Add to FAISS
    """
    from app.db.database import SessionLocal
    from app.db.models import DocumentRecord
    from app.services.language_utils import detect_language
    from app.services.rag_engine import index_document

    seed_dir = Path(settings.seed_data_dir)
    upload_dir = Path(settings.resolved_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    if not seed_dir.exists():
        logger.warning("Seed data directory %s does not exist — skipping", seed_dir)
        return

    # Collect all seed files (.txt and .pdf)
    seed_files = sorted(
        f for f in seed_dir.iterdir()
        if f.is_file() and f.suffix.lower() in {".txt", ".pdf"}
    )

    if not seed_files:
        logger.warning("No seed files found in %s", seed_dir)
        return

    logger.info("Found %d seed files to process", len(seed_files))

    db = SessionLocal()
    total_indexed = 0

    try:
        for i, seed_file in enumerate(seed_files, 1):
            filename = seed_file.name

            # Skip if already in database
            existing = db.query(DocumentRecord).filter(
                DocumentRecord.filename == filename
            ).first()
            if existing:
                logger.debug("Skipping '%s' — already in database", filename)
                continue

            # Copy to uploads directory
            dest_path = upload_dir / filename
            if not dest_path.exists():
                shutil.copy2(seed_file, dest_path)

            # Read text content
            if seed_file.suffix.lower() == ".txt":
                text = seed_file.read_text(encoding="utf-8", errors="ignore")
                page_count = 1
                page_tuples = None
            elif seed_file.suffix.lower() == ".pdf":
                try:
                    from app.services.pdf_extractor import extract_pdf_detailed
                    text, page_count, page_tuples, _, _ = extract_pdf_detailed(dest_path)
                except Exception as exc:
                    logger.warning("PDF extraction failed for '%s': %s", filename, exc)
                    text = dest_path.read_text(encoding="utf-8", errors="ignore")
                    page_count = 1
                    page_tuples = None
            else:
                continue

            if not text or not text.strip():
                logger.warning("Skipping '%s' — no text content", filename)
                continue

            # Detect language
            detected_lang = "en"
            try:
                detected_lang = detect_language(text[:2000])
            except Exception:
                pass

            # Extract department from filename (e.g. "202101141237329905_Finance_Department.txt")
            department = None
            parts = filename.rsplit("_", 1)
            if len(parts) > 1:
                dept_part = filename.split("_", 1)
                if len(dept_part) > 1:
                    department = dept_part[1].replace("_", " ").rsplit(".", 1)[0]

            # Extract document number
            doc_num = filename.split("_")[0] if "_" in filename else filename.split(".")[0]
            try:
                from app.services.status_inference import extract_gr_metadata
                h_meta = extract_gr_metadata(text[:3000])
                if h_meta.get("document_number"):
                    doc_num = h_meta["document_number"]
                if h_meta.get("department"):
                    department = h_meta["department"]
            except Exception:
                pass

            # Create database record
            record = DocumentRecord(
                filename=filename,
                original_name=filename,
                content_type="text/plain" if seed_file.suffix == ".txt" else "application/pdf",
                file_size=seed_file.stat().st_size,
                page_count=page_count,
                language=detected_lang,
                text_preview=text[:10000],
                department=department,
                document_number=doc_num,
                category="Resolution",
                status="active",
                is_repository_document=True,
                source_key="seed_data",
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            # Index into FAISS
            try:
                doc_meta = {
                    "filename": record.filename,
                    "document_number": record.document_number,
                    "department": record.department,
                    "category": record.category,
                    "issue_date": record.issue_date,
                }
                chunk_count = index_document(
                    text, record.id,
                    page_tuples=page_tuples,
                    doc_meta=doc_meta,
                )
                total_indexed += 1
                if i % 20 == 0 or i == len(seed_files):
                    logger.info(
                        "Progress: %d/%d files processed (%d indexed)",
                        i, len(seed_files), total_indexed,
                    )
            except Exception as exc:
                logger.warning("Indexing failed for '%s': %s", filename, exc)

        logger.info(
            "Seed complete: %d documents indexed from %s",
            total_indexed, seed_dir,
        )

    except Exception as exc:
        logger.error("Seed initialization error: %s", exc, exc_info=True)
    finally:
        db.close()
