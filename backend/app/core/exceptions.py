"""
Custom exception classes and FastAPI exception handlers for PolicyPilot.
"""

# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse 
from app.core.logging_config import get_logger

logger = get_logger("exceptions")


# ── Custom Exceptions ────────────────────────────────────────────────────────


class PolicyPilotError(Exception):
    """Base exception for all PolicyPilot errors."""

    def __init__(self, message: str = "An unexpected error occurred", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DocumentNotFoundError(PolicyPilotError):
    """Raised when a requested document does not exist."""

    def __init__(self, document_id: int | str = ""):
        msg = f"Document not found: {document_id}" if document_id else "Document not found"
        super().__init__(message=msg, status_code=404)


class ExtractionError(PolicyPilotError):
    """Raised when PDF text extraction fails."""

    def __init__(self, filename: str = "", detail: str = ""):
        msg = f"Failed to extract text from '{filename}'"
        if detail:
            msg += f": {detail}"
        super().__init__(message=msg, status_code=422)


class EmbeddingError(PolicyPilotError):
    """Raised when the embedding model fails."""

    def __init__(self, detail: str = ""):
        msg = "Embedding generation failed"
        if detail:
            msg += f": {detail}"
        super().__init__(message=msg, status_code=500)


class LLMError(PolicyPilotError):
    """Raised when the Groq LLM API call fails."""

    def __init__(self, detail: str = ""):
        msg = "LLM request failed"
        if detail:
            msg += f": {detail}"
        super().__init__(message=msg, status_code=502)


class VectorStoreError(PolicyPilotError):
    """Raised when FAISS vector store operations fail."""

    def __init__(self, detail: str = ""):
        msg = "Vector store operation failed"
        if detail:
            msg += f": {detail}"
        super().__init__(message=msg, status_code=500)


# ── Exception Handlers ──────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI application."""

    @app.exception_handler(PolicyPilotError)
    async def policypilot_error_handler(request: Request, exc: PolicyPilotError):
        logger.error("PolicyPilotError: %s (status=%d)", exc.message, exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "type": "UnhandledException"},
        )
