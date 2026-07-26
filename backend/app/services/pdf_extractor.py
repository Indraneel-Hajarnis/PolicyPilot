from pathlib import Path


def extract_text_from_pdf(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return ""

    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text
