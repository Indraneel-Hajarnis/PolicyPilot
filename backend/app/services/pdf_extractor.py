import io
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger("pdf_extractor")


def _ocr_page_image(page) -> Tuple[str, float]:
    """Render page image and perform OCR using pytesseract if available."""
    try:
        from PIL import Image
        import pytesseract
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes()))
        ocr_text = pytesseract.image_to_string(img, lang="eng+mar")
        return ocr_text.strip(), 0.85
    except Exception as exc:
        logger.debug("Tesseract OCR fallback skipped/failed: %s", exc)
        return "", 0.0


def extract_pdf_detailed(path: Path) -> Tuple[str, int, List[Tuple[int, str]], bool, float]:
    """
    Extract text, page count, per-page tuples [(page_num, text)], ocr_used, and ocr_confidence.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF (fitz) is not installed. Text extraction skipped.")
        return "", 0, [], False, 0.0

    try:
        doc = fitz.open(str(path))
        page_count = len(doc)
        page_tuples = []
        ocr_pages_count = 0

        for page_idx, page in enumerate(doc, start=1):
            try:
                page_text = page.get_text() or ""
                clean_text = page_text.strip()
                if len(clean_text) < 30:
                    ocr_text, _ = _ocr_page_image(page)
                    if ocr_text:
                        clean_text = ocr_text
                        ocr_pages_count += 1

                page_tuples.append((page_idx, clean_text))
            except Exception as page_err:
                logger.warning("Failed to extract text from page %d in %s: %s", page_idx, path, page_err)

        doc.close()
        full_text = "\n\n".join(txt for _, txt in page_tuples if txt)
        ocr_used = ocr_pages_count > 0
        avg_confidence = round(0.85 if ocr_used else 1.0, 2)
        return full_text, page_count, page_tuples, ocr_used, avg_confidence
    except Exception as e:
        logger.error("Failed to open or process PDF %s: %s", path, e)
        return "", 0, [], False, 0.0


def extract_pdf_info(path: Path) -> Tuple[str, int]:
    """Extract text and page count from a PDF. Returns (text, page_count)."""
    full_text, page_count, _, _, _ = extract_pdf_detailed(path)
    return full_text, page_count


def extract_text_from_pdf(path: Path) -> str:
    """Legacy wrapper – returns only text."""
    text, _ = extract_pdf_info(path)
    return text
