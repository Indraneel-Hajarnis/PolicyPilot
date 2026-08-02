#!/usr/bin/env python3
"""
Pre-seed script — runs during Docker build to pre-compute the FAISS index
and SQLite database from bundled seed documents.

This ensures the Docker image ships with all data pre-loaded, so container
starts are instant (no embedding generation at runtime).

Usage:
    cd backend
    python scripts/preseed.py

Environment:
    DATA_DIR     — where to write DB + FAISS (default: ./data)
    SEED_DATA_DIR — where seed documents live (default: ./seed_data)
"""
import logging
import os
import sys

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("preseed")


def main():
    logger.info("=" * 60)
    logger.info("  PolicyPilot Pre-Seed Script")
    logger.info("=" * 60)

    # Import after sys.path setup
    from app.config import settings

    logger.info("DATA_DIR       = %s", settings.data_dir)
    logger.info("SEED_DATA_DIR  = %s", settings.seed_data_dir)
    logger.info("VECTOR_STORE   = %s", settings.resolved_vector_store_path)
    logger.info("DATABASE_URL   = %s", settings.resolved_database_url)

    # 1. Initialize the database (create tables)
    logger.info("Initializing database...")
    from app.db.database import init_db
    init_db()

    # 2. Create default users
    logger.info("Creating default users...")
    from app.services.auth import ensure_default_users
    ensure_default_users()

    # 3. Seed the central repository (3 built-in demo documents)
    logger.info("Seeding central repository...")
    from app.db.database import SessionLocal
    from app.services.seed_repository import seed_central_repository
    db = SessionLocal()
    try:
        result = seed_central_repository(db)
        logger.info("Central repository: %s", result.get("message", "done"))
    finally:
        db.close()

    # 4. Seed from bundled documents (144 files in seed_data/)
    logger.info("Processing bundled seed documents...")
    from app.services.startup import _seed_from_bundled_documents
    _seed_from_bundled_documents()

    # 5. Verify
    from pathlib import Path
    faiss_path = Path(settings.resolved_vector_store_path) / "index.faiss"
    db_path = settings.resolved_database_url.replace("sqlite:///", "")

    logger.info("=" * 60)
    logger.info("  Pre-Seed Complete")
    logger.info("=" * 60)
    logger.info("  FAISS index: %s (exists=%s)", faiss_path, faiss_path.exists())
    if faiss_path.exists():
        logger.info("  FAISS size:  %.2f MB", faiss_path.stat().st_size / 1024 / 1024)
    logger.info("  Database:    %s (exists=%s)", db_path, Path(db_path).exists())
    if Path(db_path).exists():
        logger.info("  DB size:     %.2f MB", Path(db_path).stat().st_size / 1024 / 1024)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
