import logging

# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, inspect as sa_inspect, text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
logger = logging.getLogger('db.migration')


def init_db() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_db()


def _add_missing_columns(table_name: str, columns: dict[str, str]) -> None:
    inspector = sa_inspect(engine)
    if table_name not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns(table_name)}
    with engine.connect() as conn:
        for col, col_type in columns.items():
            if col not in existing:
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {col} {col_type}'))
        conn.commit()


def _migrate_db() -> None:
    try:
        _add_missing_columns(
            'documents',
            {
                'content_type': 'VARCHAR(100)',
                'text_preview': 'TEXT',
                'original_name': 'VARCHAR(255)',
                'title': 'VARCHAR(500)',
                'file_size': 'INTEGER',
                'page_count': 'INTEGER',
                'language': 'VARCHAR(10)',
                'issue_date': 'VARCHAR(50)',
                'department': 'VARCHAR(255)',
                'document_number': 'VARCHAR(100)',
                'category': 'VARCHAR(100)',
                'status': 'VARCHAR(50)',
                'status_reason': 'TEXT',
                'source_id': 'INTEGER',
                'source_key': 'VARCHAR(100)',
                'source_url': 'VARCHAR(1000)',
                'source_document_id': 'VARCHAR(255)',
                'checksum': 'VARCHAR(128)',
                'is_repository_document': 'BOOLEAN DEFAULT 0',
                'ocr_used': 'BOOLEAN DEFAULT 0',
                'ocr_confidence': 'REAL',
            },
        )
        _add_missing_columns(
            'query_logs',
            {
                'document_id': 'INTEGER',
                'user_id': 'INTEGER',
                'language': 'VARCHAR(10)',
                'confidence': 'REAL',
            },
        )
        _add_missing_columns(
            'chat_sessions',
            {
                'user_id': 'INTEGER',
            },
        )
    except Exception as exc:
        logger.warning('Migration warning: %s', exc)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
