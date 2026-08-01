import os
from pathlib import Path
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'PolicyPilot'
    debug: bool = True
    database_url: str = 'sqlite:///./data/policypilot.db'
    groq_api_key: str = ''
    model_name: str = 'llama-3.3-70b-versatile'
    vector_store_path: str = './data/faiss_index'
    embedding_model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    auth_secret: str = 'change-me-in-production'
    auth_token_ttl_minutes: int = 480
    similarity_threshold: float = 0.28
    tesseract_cmd: str = ''
    ocr_languages: str = 'eng+mar'
    repository_sync_limit: int = 25
    seed_desk_officer_username: str = 'desk.officer'
    seed_desk_officer_password: str = 'DeskOfficer123!'
    seed_legal_translator_username: str = 'legal.translator'
    seed_legal_translator_password: str = 'Translator123!'
    seed_it_admin_username: str = 'it.admin'
    seed_it_admin_password: str = 'Admin123!'

    @property
    def api_key(self) -> str:
        if self.groq_api_key:
            return self.groq_api_key
        if os.getenv('GROQ_API_KEY'):
            return os.getenv('GROQ_API_KEY')
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
                if line.startswith('GROQ_API_KEY=') and not line.startswith('#'):
                    val = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        return ''


settings = Settings()

