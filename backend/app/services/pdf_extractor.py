"""
PDF text extraction using PyMuPDF (fitz).

Extracts text page-by-page, handling encrypted/corrupt PDFs gracefully.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.core.exceptions import ExtractionError
from app.core.logging_config import get_logger

logger = get_logger("services.pdf_extractor")


def extract_text_from_pdf(file_path: str | Path) -> list[tuple[int, str]]:
    """
    Extract text from each page of a PDF file.

    Args:
        file_path: Path to the PDF file on disk.

    Returns:
        List of (page_number, text) tuples. Page numbers are 1-indexed.

    Raises:
        ExtractionError: If the PDF cannot be opened or text extraction fails.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtractionError(file_path.name, "File does not exist")

    pages: list[tuple[int, str]] = []

    try:
        doc = fitz.open(str(file_path))
    except Exception as e:
        raise ExtractionError(file_path.name, str(e))

    try:
        if doc.is_encrypted:
            # Try opening without a password (some PDFs have empty passwords)
            if not doc.authenticate(""):
                raise ExtractionError(file_path.name, "PDF is password-protected")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")

            # Clean up whitespace but preserve paragraph structure
            text = text.strip()
            if text:
                pages.append((page_num + 1, text))  # 1-indexed

        logger.info(
            "Extracted text from '%s': %d pages, %d non-empty",
            file_path.name,
            len(doc),
            len(pages),
        )
    except ExtractionError:
        raise
    except Exception as e:
        raise ExtractionError(file_path.name, str(e))
    finally:
        doc.close()

    if not pages:
        raise ExtractionError(
            file_path.name,
            "No text content found — the PDF may be image-only",
        )

    return pages


def get_page_count(file_path: str | Path) -> int:
    """Return total page count of a PDF without full text extraction."""
    try:
        doc = fitz.open(str(file_path))
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 0
