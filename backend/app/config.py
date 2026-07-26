"""
PolicyPilot configuration — loads settings from environment variables / .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings backed by environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq LLM ─────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ── Embedding Model ──────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Chunking ─────────────────────────────────
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # ── Retrieval ────────────────────────────────
    top_k: int = 5
    similarity_threshold: float = 0.30

    # ── Paths ────────────────────────────────────
    upload_dir: str = "data/uploads"
    faiss_index_dir: str = "data/faiss_index"

    # ── Database ─────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./data/policypilot.db"

    # ── Server ───────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Helpers ──────────────────────────────────
    def ensure_directories(self) -> None:
        """Create upload and index directories if they don't exist."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.faiss_index_dir).mkdir(parents=True, exist_ok=True)


# Singleton instance — import this everywhere
settings = Settings()
