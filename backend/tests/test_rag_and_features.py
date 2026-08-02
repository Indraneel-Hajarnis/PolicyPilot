import os
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import DocumentRecord, User, DocumentRelationship
from app.services.vector_store import VectorStore
from app.services.rag_engine import answer_question, index_document
from app.services.language_utils import detect_language, translate_and_expand_query
from app.services.pdf_extractor import extract_pdf_detailed
from app.services.docx_extractor import extract_docx_detailed
from app.services.status_inference import infer_document_relationships, extract_gr_metadata
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ROLE_PERMISSIONS,
)

from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite:///:memory:"


class MockEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]


@pytest.fixture(autouse=True)
def mock_embedder_singleton(monkeypatch):
    monkeypatch.setattr("app.services.rag_engine._get_embedder", lambda: MockEmbedder())


@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)



def test_grounded_rag_refusal_when_no_context():
    """Verify that RAG returns a strict refusal response when no context matches."""
    res = answer_question("What is the refund policy for solar pump installations?", document_id=999999)
    assert res["confidence"] == 0.0
    assert len(res["sources"]) == 0
    assert "Insufficient Authenticated Evidence" in res["answer"] or "शासकीय दस्तऐवज उपलब्ध नाहीत" in res["answer"]


def test_vector_store_deletion(tmp_path):
    """Verify that vector_store.delete removes document vectors and updates FAISS index."""
    vs = VectorStore(tmp_path)
    embeddings = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
    metadatas = [
        {"doc_id": 101, "chunk_index": 0, "text": "Doc 101 chunk 0"},
        {"doc_id": 101, "chunk_index": 1, "text": "Doc 101 chunk 1"},
        {"doc_id": 202, "chunk_index": 0, "text": "Doc 202 chunk 0"},
    ]
    vs.add(embeddings, metadatas)
    assert vs.index.ntotal == 3

    # Delete doc_id=101
    removed = vs.delete(101)
    assert removed == 2
    assert vs.index.ntotal == 1
    assert vs.id_map[0]["doc_id"] == 202


def test_multilingual_language_and_query_expansion():
    """Verify language detection and Marathi government query expansion."""
    text_mr = "महाराष्ट्र शासन शिक्षण विभाग निर्णय क्रमांक २०२३"
    assert detect_language(text_mr) in ("mr", "hi")

    expanded = translate_and_expand_query("Tell me about government resolution for teacher promotion", target_lang="mr")
    assert "शासन निर्णय" in expanded or "पदोन्नती" in expanded


def test_status_inference_and_relationships(db_session):
    """Verify automatic status update to 'superseded' when a new GR references an old GR."""
    old_doc = DocumentRecord(
        filename="old_gr.pdf",
        original_name="old_gr.pdf",
        document_number="FIN-2019/CR-44",
        status="active",
    )
    db_session.add(old_doc)
    db_session.commit()
    db_session.refresh(old_doc)

    new_text = "महाराष्ट्र शासन वित्त विभाग. नवीन शासन निर्णय. संदर्भ: यापूर्वीचा शासन निर्णय क्र. FIN-2019/CR-44 पूर्णपणे अधिक्रमित (Supersedes) करण्यात आला आहे."
    new_doc = DocumentRecord(
        filename="new_gr.pdf",
        original_name="new_gr.pdf",
        document_number="FIN-2023/CR-100",
        status="active",
    )
    db_session.add(new_doc)
    db_session.commit()
    db_session.refresh(new_doc)

    rels = infer_document_relationships(new_doc, new_text, db_session)
    assert len(rels) > 0
    assert rels[0].relation_type == "supersedes"

    db_session.refresh(old_doc)
    assert old_doc.status == "superseded"


def test_auth_password_and_jwt_tokens(db_session):
    """Verify PBKDF2 password hashing and JWT access token creation/decoding."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

    user = User(username="test_admin", full_name="Test Admin", password_hash=hashed, role="it_admin")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(user)
    payload = decode_access_token(token)
    assert payload["sub"] == user.id
    assert payload["role"] == "it_admin"
    assert "user_admin" in ROLE_PERMISSIONS["it_admin"]


def test_docx_extraction_detailed(tmp_path):
    """Verify docx_extractor returns detailed page tuples format."""
    dummy_docx = tmp_path / "sample.docx"
    full_text, pages, tuples, ocr_used, ocr_conf = extract_docx_detailed(dummy_docx)
    assert isinstance(pages, int)
    assert isinstance(tuples, list)


def test_api_routes_and_reindex(db_session):
    """Verify FastAPI test client endpoints including health and reindex."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.database import get_db

    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["message"] == "PolicyPilot API is running"

    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_reindex = client.post("/api/upload/reindex")
    assert res_reindex.status_code == 200
    assert "queued" in res_reindex.json()

    app.dependency_overrides.clear()

