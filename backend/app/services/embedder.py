from sentence_transformers import SentenceTransformer
from app.config import settings


class Embedder:
    def __init__(self, model_name: str | None = None):
        target_model = model_name or settings.embedding_model_name
        self.model = SentenceTransformer(target_model)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).tolist()

