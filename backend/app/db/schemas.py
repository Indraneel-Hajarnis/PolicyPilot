from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    content_type: Optional[str] = None


class DocumentRead(BaseModel):
    id: int
    filename: str
    content_type: Optional[str] = None
    uploaded_at: datetime
    text_preview: Optional[str] = None

    class Config:
        from_attributes = True
