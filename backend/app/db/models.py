"""
SQLAlchemy ORM models for PolicyPilot.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    """Represents an uploaded policy document."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False, comment="Stored filename (UUID-based)")
    original_name = Column(String(500), nullable=False, comment="User-facing original filename")
    upload_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    page_count = Column(Integer, default=0, comment="Number of pages in the PDF")
    status = Column(
        String(50),
        default="processing",
        nullable=False,
        comment="processing | ready | failed",
    )
    language = Column(String(20), default="en", comment="Detected document language (ISO 639-1)")
    file_size = Column(Integer, default=0, comment="File size in bytes")

    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, name='{self.original_name}', status='{self.status}')>"


class Chunk(Base):
    """Represents a text chunk extracted from a document."""

    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False, comment="The chunk text content")
    page_number = Column(Integer, nullable=False, comment="Source page (1-indexed)")
    chunk_index = Column(Integer, nullable=False, comment="Sequential chunk index within document")
    embedding_id = Column(
        Integer,
        nullable=True,
        comment="Corresponding ID in the FAISS index",
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, doc_id={self.document_id}, page={self.page_number})>"


class QueryLog(Base):
    """Logs every Q&A query for analytics and debugging."""

    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0, comment="Model confidence 0.0–1.0")
    document_ids = Column(String(500), default="", comment="Comma-separated document IDs used")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<QueryLog(id={self.id}, q='{self.question[:40]}...')>"
