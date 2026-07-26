from datetime import datetime
from typing import Optional

# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    original_name: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    language: Optional[str] = "en"


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

    class Config:
        from_attributes = True
