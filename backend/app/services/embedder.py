"""
Embedding service using sentence-transformers.

Singleton wrapper that lazily loads the model on first use
and batch-encodes text chunks into normalized vectors.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging_config import get_logger

logger = get_logger("services.embedder")


class Embedder:
    """Manages the sentence-transformer model and generates embeddings."""

    _instance: "Embedder | None" = None
    _model: SentenceTransformer | None = None

    def __new__(cls) -> "Embedder":
        """Singleton pattern — only one model loaded in memory."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self) -> None:
        """Lazily load the sentence-transformer model."""
        if self._model is None:
            logger.info("Loading embedding model: %s", settings.embedding_model)
            try:
                self._model = SentenceTransformer(settings.embedding_model)
                logger.info(
                    "Embedding model loaded — dimension: %d",
                    self._model.get_sentence_embedding_dimension(),
                )
            except Exception as e:
                raise EmbeddingError(f"Failed to load model '{settings.embedding_model}': {e}")

    @property
    def model(self) -> SentenceTransformer:
        """Get the loaded model, initializing if needed."""
        self._load_model()
        return self._model  # type: ignore[return-value]

    @property
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Encode a batch of texts into normalized embedding vectors.

        Args:
            texts: List of text strings to embed.

        Returns:
            numpy array of shape (len(texts), dimension) with L2-normalized vectors.

        Raises:
            EmbeddingError: If encoding fails.
        """
        if not texts:
            return np.array([])

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=64,
                show_progress_bar=False,
                normalize_embeddings=True,  # Normalize for cosine similarity via inner product
            )
            logger.info("Embedded %d texts → shape %s", len(texts), embeddings.shape)
            return embeddings.astype(np.float32)
        except Exception as e:
            raise EmbeddingError(f"Batch encoding failed: {e}")

    def embed_query(self, query: str) -> np.ndarray:
        """
        Encode a single query text into a normalized vector.

        Args:
            query: The query string.

        Returns:
            1D numpy array of shape (dimension,).
        """
        result = self.embed_texts([query])
        return result[0]


# Module-level singleton
embedder = Embedder()
