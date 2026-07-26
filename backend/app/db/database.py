# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text, inspect as sa_inspect
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import declarative_base, sessionmaker 

from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_db()


def _migrate_db() -> None:
    """Safely add any missing columns to existing SQLite tables."""
    # ALL columns that may be missing from older DB versions
    documents_cols = {
        "content_type": "VARCHAR(100)",
        "text_preview": "TEXT",
        "original_name": "VARCHAR(255)",
        "file_size": "INTEGER",
        "page_count": "INTEGER",
        "language": "VARCHAR(10)",
    }
    try:
        inspector = sa_inspect(engine)
        tables = inspector.get_table_names()

        # Migrate documents table
        if "documents" in tables:
            existing = {c["name"] for c in inspector.get_columns("documents")}
            with engine.connect() as conn:
                for col, col_type in documents_cols.items():
                    if col not in existing:
                        conn.execute(text(f"ALTER TABLE documents ADD COLUMN {col} {col_type}"))
                conn.commit()

        # Migrate query_logs table (add columns if needed after first run)
        if "query_logs" in tables:
            existing_ql = {c["name"] for c in inspector.get_columns("query_logs")}
            query_log_cols = {
                "document_id": "INTEGER",
                "language": "VARCHAR(10)",
                "confidence": "REAL",
            }
            with engine.connect() as conn:
                for col, col_type in query_log_cols.items():
                    if col not in existing_ql:
                        conn.execute(text(f"ALTER TABLE query_logs ADD COLUMN {col} {col_type}"))
                conn.commit()
    except Exception as e:
        import logging
        logging.getLogger("db.migration").warning("Migration warning: %s", e)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
