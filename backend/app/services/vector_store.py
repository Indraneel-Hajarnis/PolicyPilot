"""
FAISS vector store management.

Uses IndexFlatIP (inner product on L2-normalized vectors = cosine similarity).
Maintains an id_map that maps FAISS integer IDs → database chunk IDs.
"""

import pickle
from pathlib import Path

import faiss
import numpy as np

from app.config import settings
from app.core.exceptions import VectorStoreError
from app.core.logging_config import get_logger

logger = get_logger("services.vector_store")


class VectorStore:
    """Manages a FAISS index and its ID mapping to database chunk IDs."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index: faiss.IndexFlatIP | None = None
        self.id_map: list[int] = []  # FAISS ordinal → chunk DB id

        self._index_path = Path(settings.faiss_index_dir) / "index.faiss"
        self._map_path = Path(settings.faiss_index_dir) / "id_map.pkl"

    # ── Initialization ───────────────────────────────────────────────────

    def _ensure_index(self) -> None:
        """Create the FAISS index if it doesn't exist yet."""
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)
            logger.info("Created new FAISS IndexFlatIP (dim=%d)", self.dimension)

    # ── Core Operations ──────────────────────────────────────────────────

    def add_embeddings(
        self, embeddings: np.ndarray, chunk_db_ids: list[int]
    ) -> None:
        """
        Add embeddings to the FAISS index.

        Args:
            embeddings: numpy array of shape (n, dimension), L2-normalized.
            chunk_db_ids: Corresponding database chunk IDs.

        Raises:
            VectorStoreError: If shapes mismatch or insertion fails.
        """
        self._ensure_index()

        if len(embeddings) != len(chunk_db_ids):
            raise VectorStoreError(
                f"Embeddings count ({len(embeddings)}) != chunk IDs count ({len(chunk_db_ids)})"
            )

        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise VectorStoreError(
                f"Expected shape (n, {self.dimension}), got {embeddings.shape}"
            )

        try:
            self.index.add(embeddings.astype(np.float32))  # type: ignore[union-attr]
            self.id_map.extend(chunk_db_ids)
            logger.info(
                "Added %d vectors to FAISS index (total: %d)",
                len(embeddings),
                self.index.ntotal,  # type: ignore[union-attr]
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to add vectors: {e}")

    def search(
        self, query_vector: np.ndarray, top_k: int | None = None
    ) -> list[tuple[int, float]]:
        """
        Search for the most similar vectors.

        Args:
            query_vector: 1D numpy array of shape (dimension,).
            top_k: Number of results to return.

        Returns:
            List of (chunk_db_id, similarity_score) tuples, sorted by score descending.
        """
        self._ensure_index()
        if self.index.ntotal == 0:  # type: ignore[union-attr]
            return []

        top_k = top_k or settings.top_k
        # Clamp top_k to the index size
        top_k = min(top_k, self.index.ntotal)  # type: ignore[union-attr]

        query = query_vector.reshape(1, -1).astype(np.float32)

        try:
            scores, indices = self.index.search(query, top_k)  # type: ignore[union-attr]
        except Exception as e:
            raise VectorStoreError(f"Search failed: {e}")

        results: list[tuple[int, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:  # FAISS returns -1 for empty slots
                continue
            if idx < len(self.id_map):
                results.append((self.id_map[idx], float(score)))

        return results

    def remove_by_chunk_ids(self, chunk_db_ids: set[int]) -> None:
        """
        Remove vectors by their database chunk IDs.

        Since FAISS IndexFlatIP doesn't support direct removal,
        we rebuild the index without the specified vectors.
        """
        self._ensure_index()
        if not chunk_db_ids or self.index.ntotal == 0:  # type: ignore[union-attr]
            return

        # Reconstruct all vectors
        all_vectors = faiss.rev_swig_ptr(
            self.index.get_xb(), self.index.ntotal * self.dimension  # type: ignore[union-attr]
        )
        all_vectors = np.array(all_vectors).reshape(-1, self.dimension).copy()

        # Filter
        keep_mask = [cid not in chunk_db_ids for cid in self.id_map]
        keep_vectors = all_vectors[keep_mask]
        keep_ids = [cid for cid, keep in zip(self.id_map, keep_mask) if keep]

        # Rebuild
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = []

        if len(keep_vectors) > 0:
            self.index.add(keep_vectors.astype(np.float32))
            self.id_map = keep_ids

        logger.info(
            "Removed %d vectors, %d remaining",
            len(chunk_db_ids),
            self.index.ntotal,
        )

    # ── Persistence ──────────────────────────────────────────────────────

    def save(self) -> None:
        """Persist the FAISS index and ID map to disk."""
        self._ensure_index()
        Path(settings.faiss_index_dir).mkdir(parents=True, exist_ok=True)

        try:
            faiss.write_index(self.index, str(self._index_path))  # type: ignore[arg-type]
            with open(self._map_path, "wb") as f:
                pickle.dump(self.id_map, f)
            logger.info(
                "Saved FAISS index (%d vectors) to %s",
                self.index.ntotal,  # type: ignore[union-attr]
                self._index_path,
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to save index: {e}")

    def load(self) -> bool:
        """
        Load the FAISS index and ID map from disk.

        Returns:
            True if loaded successfully, False if files don't exist.
        """
        if not self._index_path.exists() or not self._map_path.exists():
            logger.info("No existing FAISS index found — starting fresh")
            self._ensure_index()
            return False

        try:
            self.index = faiss.read_index(str(self._index_path))
            with open(self._map_path, "rb") as f:
                self.id_map = pickle.load(f)  # noqa: S301
            logger.info(
                "Loaded FAISS index: %d vectors, %d ID mappings",
                self.index.ntotal,
                len(self.id_map),
            )
            return True
        except Exception as e:
            logger.error("Failed to load FAISS index: %s — starting fresh", e)
            self._ensure_index()
            return False

    @property
    def size(self) -> int:
        """Return the number of vectors in the index."""
        if self.index is None:
            return 0
        return self.index.ntotal


# Module-level singleton
vector_store = VectorStore()
