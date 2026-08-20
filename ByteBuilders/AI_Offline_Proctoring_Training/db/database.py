"""PostgreSQL connection management and schema setup.

Belongs in `db/database.py`.

Uses a small psycopg2 connection pool rather than opening a fresh
connection per Streamlit rerun. Streamlit reruns the entire script on
every widget interaction, so a naive "connect on every page load" pattern
would open and close a Postgres connection dozens of times in a single
user session -- the pool is created once per process (via the module-level
_pool singleton) and reused across reruns.

Configuration is read from environment variables (see .env) rather than
hardcoded, matching the existing project's use of `load_dotenv()` for
LANGSMITH_*/OLLAMA_HOST in main.py.
"""

import logging
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()   

import psycopg2
import psycopg2.extras
import psycopg2.pool

logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "proctoring_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

_pool = None


def get_pool() -> psycopg2.pool.SimpleConnectionPool:
    global _pool
    if _pool is None:
        logger.info("Creating Postgres connection pool (db=%s host=%s)", DB_NAME, DB_HOST)
        _pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASSWORD,
        )
    return _pool


@contextmanager
def get_connection():
    """Borrow a connection from the pool; commits on success, rolls back on error."""
    conn = get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        get_pool().putconn(conn)


@contextmanager
def get_cursor(dict_cursor: bool = True):
    """Borrow a connection + cursor. dict_cursor=True returns rows as dicts
    (RealDictCursor) so callers can do row["field"] instead of row[0].
    """
    with get_connection() as conn:
        cursor_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
        finally:
            cur.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS proctoring_jobs (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_filename TEXT NOT NULL,
    video_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    risk_level TEXT,
    risk_score DOUBLE PRECISION,
    final_report TEXT,
    human_review TEXT,
    error_message TEXT,
    langsmith_run_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_proctoring_jobs_user_id ON proctoring_jobs(user_id);
"""


def init_db() -> None:
    """Create tables if they don't exist yet. Cheap and safe to call on
    every app start -- CREATE TABLE IF NOT EXISTS is a no-op after the
    first run.
    """
    with get_cursor(dict_cursor=False) as cur:
        cur.execute(SCHEMA)
    logger.info("Database schema ready")
