from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application configuration loaded from backend/.env."""

    # Application
    APP_NAME: str = "VectorVanguard-API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # PostgreSQL
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "vectorvanguard_db"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./storage/chroma"
    CHROMA_COLLECTION_NAME: str = "exam_evidence_vectors"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3.1:8b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text:latest"
    OLLAMA_VISION_MODEL: str = "gemma3:4b"

    # Tesseract OCR
    TESSERACT_PATH: str | None = None

    # Load variables from backend/.env
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Build the SQLAlchemy PostgreSQL connection URL."""
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Application-wide settings instance
settings = Settings()
