from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PolicyPilot"
    debug: bool = True
    database_url: str = "sqlite:///./data/policypilot.db"
    groq_api_key: str = ""
    model_name: str = "llama3-8b-8192"
    vector_store_path: str = "./data/faiss_index"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
