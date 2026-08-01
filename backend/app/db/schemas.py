from datetime import datetime
from typing import Optional

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    filename: str
    original_name: Optional[str] = None
    title: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    language: Optional[str] = 'en'
    issue_date: Optional[str] = None
    department: Optional[str] = None
    document_number: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = 'active'
    status_reason: Optional[str] = None
    source_key: Optional[str] = None
    source_url: Optional[str] = None
    is_repository_document: Optional[bool] = False
    ocr_used: Optional[bool] = False
    ocr_confidence: Optional[float] = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_name: Optional[str] = None
    title: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    uploaded_at: datetime
    text_preview: Optional[str] = None
    issue_date: Optional[str] = None
    department: Optional[str] = None
    document_number: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = 'active'
    status_reason: Optional[str] = None
    source_key: Optional[str] = None
    source_url: Optional[str] = None
    is_repository_document: Optional[bool] = False
    ocr_used: Optional[bool] = False
    ocr_confidence: Optional[float] = None


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    confidence: Optional[float] = None
    sources_json: Optional[str] = None
    created_at: datetime


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    title: Optional[str] = 'New Chat'
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0


class ChatSessionCreate(BaseModel):
    title: Optional[str] = 'New Chat'
    document_id: Optional[int] = None


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    confidence: Optional[float] = None
    sources_json: Optional[str] = None
