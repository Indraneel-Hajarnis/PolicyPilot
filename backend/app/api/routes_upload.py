"""
Upload endpoint — handles PDF upload, extraction, chunking, and embedding.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ExtractionError
from app.core.logging_config import get_logger
from app.db.database import get_db
from app.db.models import Chunk, Document
from app.db.schemas import UploadResponse
from app.services.chunker import chunker
from app.services.embedder import embedder
from app.services.language_utils import detect_language
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.vector_store import vector_store

logger = get_logger("api.upload")
router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload a PDF document for processing.

    Pipeline: save file → extract text → detect language → chunk → embed → index.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise ExtractionError(file.filename or "unknown", "Only PDF files are accepted")

    # 1. Save the uploaded file
    stored_filename = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = Path(settings.upload_dir) / stored_filename

    content = await file.read()
    file_size = len(content)

    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(content)

    logger.info("Saved upload: %s (%d bytes)", stored_filename, file_size)

    try:
        # 2. Extract text
        pages = extract_text_from_pdf(upload_path)

        # 3. Detect language from first few pages
        sample_text = " ".join(text for _, text in pages[:3])
        language = detect_language(sample_text)

        # 4. Create the document record
        doc = Document(
            filename=stored_filename,
            original_name=file.filename,
            page_count=len(pages),
            file_size=file_size,
            language=language,
            status="processing",
        )
        db.add(doc)
        await db.flush()  # Get the ID

        # 5. Chunk the text
        chunk_dicts = chunker.chunk_pages(pages)

        # 6. Create chunk records
        chunk_models = []
        for cd in chunk_dicts:
            chunk_model = Chunk(
                document_id=doc.id,
                content=cd["content"],
                page_number=cd["page_number"],
                chunk_index=cd["chunk_index"],
            )
            chunk_models.append(chunk_model)

        db.add_all(chunk_models)
        await db.flush()  # Get chunk IDs

        # 7. Generate embeddings
        texts = [c.content for c in chunk_models]
        embeddings = embedder.embed_texts(texts)

        # 8. Add to FAISS index
        chunk_db_ids = [c.id for c in chunk_models]
        vector_store.add_embeddings(embeddings, chunk_db_ids)

        # 9. Update chunk records with FAISS embedding IDs
        for i, chunk_model in enumerate(chunk_models):
            # The FAISS ordinal ID is (index_size_before_add + i)
            chunk_model.embedding_id = vector_store.size - len(chunk_models) + i

        # 10. Mark document as ready
        doc.status = "ready"

        # 11. Persist FAISS index
        vector_store.save()

        logger.info(
            "Document processed: '%s' — %d pages, %d chunks, language=%s",
            file.filename,
            len(pages),
            len(chunk_models),
            language,
        )

        return UploadResponse(
            id=doc.id,
            filename=stored_filename,
            original_name=file.filename,
            page_count=len(pages),
            file_size=file_size,
            language=language,
            status="ready",
            message=f"Document uploaded and processed: {len(chunk_models)} chunks indexed",
        )

    except ExtractionError:
        # Clean up the file on extraction failure
        upload_path.unlink(missing_ok=True)
        raise
    except Exception as e:
        upload_path.unlink(missing_ok=True)
        logger.exception("Upload processing failed: %s", e)
        raise ExtractionError(file.filename, str(e))
