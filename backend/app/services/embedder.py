import logging
from typing import List
from fastembed import TextEmbedding

logger = logging.getLogger("embedder")

class Embedder:
    """
    Wraps the fastembed model for generating dense embeddings using ONNX runtime.
    This replaces PyTorch/SentenceTransformers to drastically reduce memory footprint
    from >500MB to <150MB, allowing it to run smoothly on a 512MB RAM instance.
    Produces identical 384-dimensional vectors to sentence-transformers/all-MiniLM-L6-v2.
    """
    def __init__(self, target_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.target_model = target_model
        # Use fastembed to load the model
        logger.info(f"Initializing FastEmbed ONNX model: {self.target_model}")
        self.model = TextEmbedding(self.target_model)
        logger.info("Embedder initialized successfully via fastembed.")

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        # fastembed returns an iterator of numpy arrays
        embeddings_iter = self.model.embed(texts)
        return [vec.tolist() for vec in embeddings_iter]
