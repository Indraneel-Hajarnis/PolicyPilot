import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger("pdf_extractor")


def extract_pdf_info(path: Path) -> Tuple[str, int]:
    """Extract text and page count from a PDF. Returns (text, page_count)."""
    try:
        # pyrefly: ignore [missing-import]
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF (fitz) is not installed. Text extraction skipped.")
        return "", 0

    try:
        doc = fitz.open(str(path))
        page_count = len(doc)
        text_pages = []
        for page in doc:
            try:
                page_text = page.get_text()
                if page_text:
                    text_pages.append(page_text)
            except Exception as page_err:
                logger.warning("Failed to extract text from page in %s: %s", path, page_err)
        doc.close()
        full_text = "\n".join(text_pages)
        return full_text, page_count
    except Exception as e:
        logger.error("Failed to open or process PDF %s: %s", path, e)
        return "", 0


def extract_text_from_pdf(path: Path) -> str:
    """Legacy wrapper – returns only text."""
    text, _ = extract_pdf_info(path)
    return text
