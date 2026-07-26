from pathlib import Path
import pickle

import faiss
import numpy as np


class VectorStore:
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_path / "index.faiss"
        self.id_map_file = self.index_path / "id_map.pkl"
        self.index = None
        self.id_map = []
        self._load()

    def _load(self):
        if self.index_file.exists() and self.id_map_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with self.id_map_file.open("rb") as handle:
                self.id_map = pickle.load(handle)
        else:
            self.index = faiss.IndexFlatL2(384)

    def add(self, embeddings, ids):
        if self.index is None:
            self.index = faiss.IndexFlatL2(384)
        vectors = np.array(embeddings, dtype="float32")
        self.index.add(vectors)
        self.id_map.extend(ids)
        self._save()

    def search(self, embedding, top_k=5):
        vector = np.array([embedding], dtype="float32")
        distances, indices = self.index.search(vector, min(top_k, self.index.ntotal))
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0:
                continue
            results.append({"id": self.id_map[int(idx)], "distance": float(dist)})
        return results

    def _save(self):
        faiss.write_index(self.index, str(self.index_file))
        with self.id_map_file.open("wb") as handle:
            pickle.dump(self.id_map, handle)
