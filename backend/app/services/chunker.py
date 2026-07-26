"""
Text chunking service using LangChain's RecursiveCharacterTextSplitter.

Splits extracted PDF text into overlapping chunks while preserving
page-number metadata for source attribution.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.logging_config import get_logger

logger = get_logger("services.chunker")


class TextChunker:
    """Wraps LangChain's text splitter with PolicyPilot defaults."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False,
        )

    def chunk_pages(
        self, pages: list[tuple[int, str]]
    ) -> list[dict]:
        """
        Split page texts into overlapping chunks, preserving page metadata.

        Args:
            pages: List of (page_number, text) tuples from the PDF extractor.

        Returns:
            List of dicts with keys:
                - content (str): chunk text
                - page_number (int): source page
                - chunk_index (int): sequential index across the document
        """
        chunks: list[dict] = []
        chunk_index = 0

        for page_number, text in pages:
            if not text.strip():
                continue

            page_chunks = self._splitter.split_text(text)

            for chunk_text in page_chunks:
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue

                chunks.append(
                    {
                        "content": chunk_text,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1

        logger.info(
            "Chunked %d pages → %d chunks (size=%d, overlap=%d)",
            len(pages),
            len(chunks),
            self.chunk_size,
            self.chunk_overlap,
        )
        return chunks


# Module-level convenience instance
chunker = TextChunker()
