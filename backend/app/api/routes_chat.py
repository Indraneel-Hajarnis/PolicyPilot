"""
Chat session CRUD — persistent conversation history (SRS Section 3.7, FR3).
"""
import json
from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ChatSession, ChatMessage
from app.db.schemas import ChatSessionCreate, ChatMessageCreate

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions")
def list_sessions(limit: int = 50, db: Session = Depends(get_db)):
    """List all chat sessions, newest first."""
    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for s in sessions:
        msg_count = db.query(func.count(ChatMessage.id)).filter(ChatMessage.session_id == s.id).scalar() or 0
        result.append({
            "id": s.id,
            "title": s.title,
            "document_id": s.document_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "message_count": msg_count,
        })
    return result


@router.post("/sessions")
def create_session(payload: ChatSessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session."""
    session = ChatSession(
        title=payload.title or "New Chat",
        document_id=payload.document_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "title": session.title,
        "document_id": session.document_id,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        "message_count": 0,
    }


@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages for a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return {
        "session": {
            "id": session.id,
            "title": session.title,
            "document_id": session.document_id,
        },
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "confidence": m.confidence,
                "sources": json.loads(m.sources_json) if m.sources_json else [],
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@router.post("/sessions/{session_id}/messages")
def add_message(session_id: int, payload: ChatMessageCreate, db: Session = Depends(get_db)):
    """Add a message to a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg = ChatMessage(
        session_id=session_id,
        role=payload.role,
        content=payload.content,
        confidence=payload.confidence,
        sources_json=payload.sources_json,
    )
    db.add(msg)

    # Auto-generate session title from first user message
    if payload.role == "user" and session.title == "New Chat":
        session.title = payload.content[:80] + ("..." if len(payload.content) > 80 else "")

    db.commit()
    db.refresh(msg)
    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "confidence": msg.confidence,
        "sources": json.loads(msg.sources_json) if msg.sources_json else [],
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    }


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session deleted", "id": session_id}


@router.patch("/sessions/{session_id}")
def update_session(session_id: int, payload: ChatSessionCreate, db: Session = Depends(get_db)):
    """Update session title or document scope."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if payload.title is not None:
        session.title = payload.title
    if payload.document_id is not None:
        session.document_id = payload.document_id
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "title": session.title,
        "document_id": session.document_id,
    }
