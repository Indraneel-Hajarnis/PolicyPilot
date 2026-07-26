from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/summary", tags=["summary"])


class SummaryRequest(BaseModel):
    document_id: int


@router.post("")
def create_summary(payload: SummaryRequest):
    if payload.document_id <= 0:
        raise HTTPException(status_code=400, detail="document_id must be positive")

    return {
        "document_id": payload.document_id,
        "summary": "This is a placeholder summary. Wire up the summarizer service to generate structured output.",
        "highlights": [],
    }
