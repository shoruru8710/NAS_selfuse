"""Application configuration via Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    debug: bool = True

    # Database
    postgres_db: str = "nas_storage"
    postgres_user: str = "nas_user"
    postgres_password: str = ""
    postgres_host: str = "db"
    postgres_port: int = 5432

    # Service auth
    service_token: str = ""

    # Storage
    storage_root: str = "/data/storage/objects"

    # Embedding
    embedding_provider: str = "local"  # "local" or "openai"
    openai_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # RAG
    chunk_size: int = 800
    chunk_overlap: int = 150

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
