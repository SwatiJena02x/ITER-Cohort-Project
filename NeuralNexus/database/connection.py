"""
database/connection.py
-----------------------
PostgreSQL connection management using SQLAlchemy.

Provides:
- `engine`      : the SQLAlchemy engine, built from DATABASE_URL in .env
- `SessionLocal` : a session factory for creating DB sessions
- `Base`        : the declarative base all ORM models inherit from
- `get_db()`    : a FastAPI dependency that yields a session and closes it
"""
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import socket

load_dotenv()

def _resolve_database_url() -> str:
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/proctoring_db",
    )
    if "@postgres:" in url:
        try:
            socket.gethostbyname("postgres")
        except Exception:
            # Running locally outside docker container network
            url = url.replace("@postgres:", "@127.0.0.1:")
    return url

DATABASE_URL = _resolve_database_url()

# `pool_pre_ping` avoids stale-connection errors on long-running backends.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def get_db():
    """FastAPI dependency: yields a DB session and guarantees it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """Context manager for use outside FastAPI (e.g. in agent nodes, scripts)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Create all tables and perform safe column migration for missing fields."""
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Safe auto-migration for newly added Student columns
    from sqlalchemy import text
    with engine.connect() as conn:
        for col_name, col_type in [
            ("last_login_at", "TIMESTAMP"),
            ("face_match_score", "FLOAT"),
            ("face_match_status", "VARCHAR(50)"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass
