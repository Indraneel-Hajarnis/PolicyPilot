from pathlib import Path
import pickle

# pyrefly: ignore [missing-import]
import faiss
# pyrefly: ignore [missing-import]
import numpy as np 


class VectorStore:
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_path / "index.faiss"
        self.id_map_file = self.index_path / "id_map.pkl"
        self.index = None
        # id_map is now a list of dicts: {"doc_id": int, "chunk_index": int, "text": str}
        # (previously this was a truncated "doc_id::i::chunk[:100]" string, which both
        # lost most of the chunk text and made document filtering unreliable)
        self.id_map = []
        self._load()

    def _load(self):
        if self.index_file.exists() and self.id_map_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with self.id_map_file.open("rb") as handle:
                self.id_map = pickle.load(handle)
        else:
            self.index = faiss.IndexFlatL2(384)

    def add(self, embeddings, metadatas):
        """metadatas: list of dicts {"doc_id": int, "chunk_index": int, "text": str}"""
        if self.index is None:
            self.index = faiss.IndexFlatL2(384)
        vectors = np.array(embeddings, dtype="float32")
        self.index.add(vectors)
        self.id_map.extend(metadatas)
        self._save()

    def delete(self, document_id: int) -> int:
        """Remove all chunks associated with document_id and rebuild FAISS index."""
        if self.index is None or self.index.ntotal == 0 or not self.id_map:
            return 0

        dim = self.index.d
        kept_vectors = []
        kept_metadatas = []
        removed_count = 0

        for i, meta in enumerate(self.id_map):
            if meta.get("doc_id") == document_id:
                removed_count += 1
            else:
                try:
                    vec = self.index.reconstruct(i)
                    kept_vectors.append(vec)
                except Exception:
                    pass
                kept_metadatas.append(meta)

        if removed_count == 0:
            return 0

        new_index = faiss.IndexFlatL2(dim)
        if kept_vectors:
            vectors_np = np.array(kept_vectors, dtype="float32")
            new_index.add(vectors_np)

        self.index = new_index
        self.id_map = kept_metadatas
        self._save()
        return removed_count

    def search(self, embedding, top_k=5, document_id=None):
        """
        Search the index.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        vector = np.array([embedding], dtype="float32")
        fetch_k = self.index.ntotal if document_id else min(top_k, self.index.ntotal)

        distances, indices = self.index.search(vector, fetch_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.id_map):
                continue
            meta = self.id_map[int(idx)]
            if document_id and meta.get("doc_id") != document_id:
                continue
            item = dict(meta)
            item["distance"] = float(dist)
            results.append(item)
            if len(results) >= top_k:
                break
        return results

    def _save(self):
        faiss.write_index(self.index, str(self.index_file))
        with self.id_map_file.open("wb") as handle:
            pickle.dump(self.id_map, handle)