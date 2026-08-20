"""
tests/conftest.py
--------------------
Shared pytest fixtures.

Note: the `Student.face_embedding` column uses pgvector's Vector type,
which SQLite (used for fast local tests) cannot create. Tests that need a
database therefore mock the repository layer directly rather than
spinning up `Base.metadata.create_all()` against SQLite. For true
integration tests, point DATABASE_URL at a real Postgres+pgvector instance.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client():
    """A TestClient for the FastAPI app. Endpoint tests mock the
    repository/DB layer via monkeypatch rather than relying on a live DB."""
    with TestClient(app) as c:
        yield c
