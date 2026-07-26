import os
from pathlib import Path
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "PolicyPilot"
    debug: bool = True
    database_url: str = "sqlite:///./data/policypilot.db"
    groq_api_key: str = ""
    model_name: str = "llama-3.3-70b-versatile"
    vector_store_path: str = "./data/faiss_index"

    @property
    def api_key(self) -> str:
        """Dynamically get GROQ_API_KEY from memory, env, or .env file."""
        if self.groq_api_key:
            return self.groq_api_key
        if os.getenv("GROQ_API_KEY"):
            return os.getenv("GROQ_API_KEY")
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                if line.startswith("GROQ_API_KEY=") and not line.startswith("#"):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        return ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
