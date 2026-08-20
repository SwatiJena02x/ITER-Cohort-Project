from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = "AI Exam Proctoring Assistant"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CACHE_KEY = os.getenv("CACHE_KEY", "exam-proctoring-local-key")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/proctoring")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///" + str(BASE_DIR / "data" / "proctoring.db"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(BASE_DIR / "vector_store"))
LOCAL_CACHE_PATH = os.getenv("LOCAL_CACHE_PATH", str(BASE_DIR / "data" / "local_cache.db"))
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
