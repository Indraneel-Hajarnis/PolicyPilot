from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str


@router.post("")
def answer_query(payload: QueryRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    return {
        "answer": "This is a placeholder response. Connect the retrieval pipeline to provide grounded answers.",
        "sources": [],
    }
