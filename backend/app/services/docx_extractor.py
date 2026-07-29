"""
DOCX text extractor — mirrors the pdf_extractor interface.
Uses python-docx to extract paragraph text from .docx files.
"""
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger("docx_extractor")


def extract_docx_info(path: Path) -> Tuple[str, int]:
    """Extract text and estimated page count from a DOCX file.
    Returns (text, estimated_page_count).
    """
    try:
        # pyrefly: ignore [missing-import]
        from docx import Document
    except ImportError:
        logger.warning("python-docx is not installed. DOCX text extraction skipped. Install with: pip install python-docx")
        return "", 0

    try:
        doc = Document(str(path))
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        paragraphs.append(cell_text)

        full_text = "\n".join(paragraphs)

        # Estimate page count (~3000 chars per page)
        estimated_pages = max(1, len(full_text) // 3000) if full_text else 0

        return full_text, estimated_pages
    except Exception as e:
        logger.error("Failed to process DOCX %s: %s", path, e)
        return "", 0


def extract_text_from_docx(path: Path) -> str:
    """Legacy wrapper — returns only text."""
    text, _ = extract_docx_info(path)
    return text
