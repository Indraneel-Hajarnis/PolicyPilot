# pyrefly: ignore [missing-import]
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(500), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    chat_sessions = relationship('ChatSession', back_populates='user')
    query_logs = relationship('QueryLog', back_populates='user')


class RepositorySource(Base):
    __tablename__ = 'repository_sources'

    id = Column(Integer, primary_key=True, index=True)
    source_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False)
    base_url = Column(String(1000), nullable=True)
    listing_url = Column(String(1000), nullable=True)
    auth_trusted = Column(Boolean, nullable=False, default=True)
    sync_status = Column(String(50), nullable=False, default='idle')
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    seed_urls_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    documents = relationship('DocumentRecord', back_populates='repository_source')
    ingestion_jobs = relationship('IngestionJob', back_populates='repository_source', cascade='all, delete-orphan')


class DocumentRecord(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True, default=0)
    language = Column(String(10), nullable=True, default='en')
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    text_preview = Column(Text, nullable=True)
    issue_date = Column(String(50), nullable=True)

    department = Column(String(255), nullable=True)
    document_number = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True)

    status = Column(String(50), nullable=True, default='active')
    status_reason = Column(Text, nullable=True)

    source_id = Column(Integer, ForeignKey('repository_sources.id'), nullable=True, index=True)
    source_key = Column(String(100), nullable=True, index=True)
    source_url = Column(String(1000), nullable=True)
    source_document_id = Column(String(255), nullable=True)
    checksum = Column(String(128), nullable=True, index=True)
    is_repository_document = Column(Boolean, nullable=False, default=False)
    ocr_used = Column(Boolean, nullable=False, default=False)
    ocr_confidence = Column(Float, nullable=True)

    repository_source = relationship('RepositorySource', back_populates='documents')
    chunks = relationship('DocumentChunk', back_populates='document', cascade='all, delete-orphan')
    outgoing_relationships = relationship(
        'DocumentRelationship',
        foreign_keys='DocumentRelationship.source_document_id',
        back_populates='source_document',
        cascade='all, delete-orphan',
    )
    incoming_relationships = relationship(
        'DocumentRelationship',
        foreign_keys='DocumentRelationship.target_document_id',
        back_populates='target_document',
        cascade='all, delete-orphan',
    )


class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    __table_args__ = (
        UniqueConstraint('document_id', 'chunk_index', name='uq_document_chunk_index'),
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship('DocumentRecord', back_populates='chunks')


class DocumentRelationship(Base):
    __tablename__ = 'document_relationships'

    id = Column(Integer, primary_key=True, index=True)
    source_document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    target_document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    relation_type = Column(String(50), nullable=False, index=True)
    evidence_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    source_document = relationship('DocumentRecord', foreign_keys=[source_document_id], back_populates='outgoing_relationships')
    target_document = relationship('DocumentRecord', foreign_keys=[target_document_id], back_populates='incoming_relationships')


class IngestionJob(Base):
    __tablename__ = 'ingestion_jobs'

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('repository_sources.id', ondelete='SET NULL'), nullable=True, index=True)
    status = Column(String(50), nullable=False, default='queued')
    trigger = Column(String(50), nullable=False, default='manual')
    total_found = Column(Integer, nullable=False, default=0)
    imported_count = Column(Integer, nullable=False, default=0)
    skipped_count = Column(Integer, nullable=False, default=0)
    message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    repository_source = relationship('RepositorySource', back_populates='ingestion_jobs')


class QueryLog(Base):
    __tablename__ = 'query_logs'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    document_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    language = Column(String(10), nullable=True, default='en')
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship('User', back_populates='query_logs')


class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    title = Column(String(500), nullable=True, default='New Chat')
    document_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship('User', back_populates='chat_sessions')
    messages = relationship('ChatMessage', back_populates='session', cascade='all, delete-orphan')


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    sources_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship('ChatSession', back_populates='messages')
