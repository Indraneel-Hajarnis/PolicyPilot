from datetime import datetime
from typing import Optional, List

# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    original_name: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    language: Optional[str] = "en"
    department: Optional[str] = None
    document_number: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = "active"


class DocumentRead(BaseModel):
    id: int
    filename: str
    original_name: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    uploaded_at: datetime
    text_preview: Optional[str] = None
    department: Optional[str] = None
    document_number: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = "active"

    class Config:
        from_attributes = True


# ── Chat History Schemas ──────────────────────────────────────────────────────

class ChatMessageRead(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    confidence: Optional[float] = None
    sources_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionRead(BaseModel):
    id: int
    title: Optional[str] = "New Chat"
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Chat"
    document_id: Optional[int] = None


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    confidence: Optional[float] = None
    sources_json: Optional[str] = None
