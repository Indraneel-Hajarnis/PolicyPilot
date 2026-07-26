# pyrefly: ignore [missing-import]
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func

from app.db.database import Base


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)          # bytes
    page_count = Column(Integer, nullable=True, default=0)
    language = Column(String(10), nullable=True, default="en")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    text_preview = Column(Text, nullable=True)


class QueryLog(Base):
    """Audit log for every Q&A query — feeds the Analytics dashboard."""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    document_id = Column(Integer, nullable=True)
    language = Column(String(10), nullable=True, default="en")
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
