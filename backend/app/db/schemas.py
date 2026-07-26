"""
Pydantic request/response schemas for PolicyPilot API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Upload ───────────────────────────────────────────────────────────────────


class UploadResponse(BaseModel):
    """Response after a successful document upload."""

    id: int
    filename: str
    original_name: str
    page_count: int
    file_size: int
    language: str
    status: str
    message: str = "Document uploaded and processing started"


# ── Documents ────────────────────────────────────────────────────────────────


class DocumentOut(BaseModel):
    """Public representation of a document."""

    id: int
    filename: str
    original_name: str
    upload_date: datetime
    page_count: int
    status: str
    language: str
    file_size: int

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentOut):
    """Extended document info including chunk count."""

    chunk_count: int = 0


# ── Query ────────────────────────────────────────────────────────────────────


class QueryRequest(BaseModel):
    """Incoming Q&A question."""

    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    document_id: Optional[int] = Field(
        None, description="Optional: scope the search to a specific document"
    )
    language: Optional[str] = Field(
        None, description="Optional: desired response language (ISO 639-1)"
    )


class SourceCitation(BaseModel):
    """A single source chunk backing an answer."""

    document_id: int
    document_name: str
    page_number: int
    chunk_text: str = Field(..., description="Relevant excerpt from the document")
    similarity_score: float = Field(..., ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    """Response to a Q&A question."""

    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: list[SourceCitation] = []
    related_documents: list[DocumentOut] = []
    query_id: int = Field(..., description="Logged query ID for reference")


# ── Summary ──────────────────────────────────────────────────────────────────


class SummarySection(BaseModel):
    """A titled section of the document summary."""

    title: str
    content: str


class SummaryResponse(BaseModel):
    """Structured summary of a policy document."""

    document_id: int
    document_name: str
    title: str = ""
    key_points: list[str] = []
    sections: list[SummarySection] = []
    important_dates: list[str] = []
    action_items: list[str] = []
    full_summary: str = ""


# ── Health ───────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    document_count: int = 0
    faiss_index_size: int = 0
    embedding_model: str = ""
    llm_model: str = ""
