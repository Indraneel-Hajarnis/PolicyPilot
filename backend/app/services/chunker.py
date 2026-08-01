from typing import List, Tuple, Dict, Any
# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


def split_page_tuples(
    page_tuples: List[Tuple[int, str]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict[str, Any]]:
    """
    Split per-page text tuples [(page_number, text)] into chunks while preserving page provenance.
    Returns list of dicts: {"text": chunk_text, "page_number": page_number, "chunk_index": idx}
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    result = []
    global_idx = 0

    for page_num, page_text in page_tuples:
        if not page_text or not page_text.strip():
            continue
        chunks = splitter.split_text(page_text)
        for chunk in chunks:
            result.append({
                "text": chunk,
                "page_number": page_num,
                "chunk_index": global_idx,
            })
            global_idx += 1

    return result

