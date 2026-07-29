from typing import Optional, List, Dict

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel 
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session 

from app.db.database import get_db
from app.db.models import QueryLog

router = APIRouter(prefix="/query", tags=["query"])


class ConversationTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class QueryRequest(BaseModel):
    question: str
    document_id: Optional[int] = None
    language: Optional[str] = "en"
    conversation_history: Optional[List[ConversationTurn]] = None


@router.post("")
def answer_query(payload: QueryRequest, db: Session = Depends(get_db)):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    from app.services.rag_engine import answer_question

    # Convert conversation history to plain dicts for the engine
    history = None
    if payload.conversation_history:
        history = [{"role": t.role, "content": t.content} for t in payload.conversation_history]

    result = answer_question(
        question=payload.question,
        document_id=payload.document_id,
        language=payload.language or "en",
        conversation_history=history,
    )

    # ── Persist query log ─────────────────────────────────────────────────────
    try:
        log = QueryLog(
            question=payload.question,
            answer=result["answer"][:2000],
            document_id=payload.document_id,
            language=payload.language or "en",
            confidence=result.get("confidence"),
        )
        db.add(log)
        db.commit()
    except Exception:
        pass  # Never fail user response due to logging errors

    return result
