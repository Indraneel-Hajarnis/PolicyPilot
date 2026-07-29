# pyrefly: ignore [missing-import]
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship

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

    # ── SRS metadata fields (FR3) ─────────────────────────────────────────────
    department = Column(String(255), nullable=True)
    document_number = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)

    # ── Document status (FR5) ─────────────────────────────────────────────────
    # Values: active, amended, superseded, draft
    status = Column(String(50), nullable=True, default="active")


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


# ── Chat History (FR3 — Conversation History) ─────────────────────────────────

class ChatSession(Base):
    """A conversation session grouping multiple messages."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=True, default="New Chat")
    document_id = Column(Integer, nullable=True)  # optional scope
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """A single message within a chat session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    sources_json = Column(Text, nullable=True)  # JSON-serialized sources array
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("ChatSession", back_populates="messages")
