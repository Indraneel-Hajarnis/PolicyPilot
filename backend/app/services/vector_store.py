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

    def search(self, embedding, top_k=5, document_id=None):
        """
        Search the index.

        IndexFlatL2 has no native metadata filtering, so a plain top_k search
        is done globally across ALL documents' chunks. If document_id is
        provided, we over-fetch (search the whole index) and filter down to
        that document AFTER retrieval, then truncate to top_k. Without this,
        scoping to one document could return zero results whenever that
        document's real matches weren't already inside a small global top_k.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        vector = np.array([embedding], dtype="float32")
        fetch_k = self.index.ntotal if document_id else min(top_k, self.index.ntotal)

        distances, indices = self.index.search(vector, fetch_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0:
                continue
            meta = self.id_map[int(idx)]
            if document_id and meta.get("doc_id") != document_id:
                continue
            results.append({
                "doc_id": meta.get("doc_id"),
                "chunk_index": meta.get("chunk_index"),
                "text": meta.get("text"),
                "distance": float(dist),
            })
            if len(results) >= top_k:
                break
        return results

    def _save(self):
        faiss.write_index(self.index, str(self.index_file))
        with self.id_map_file.open("wb") as handle:
            pickle.dump(self.id_map, handle)