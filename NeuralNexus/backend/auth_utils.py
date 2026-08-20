"""
backend/auth_utils.py
----------------------
Password hashing (bcrypt) and JWT creation/verification helpers.
Used by the auth API endpoints and the FastAPI dependency `get_current_user`.

JWT payload shape:
    { "sub": str(user_id), "role": "admin"|"student", "email": str, "exp": ... }
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "proctoring_super_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
try:
    import bcrypt as _bcrypt

    def hash_password(plain: str) -> str:
        return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()

    def verify_password(plain: str, hashed: str) -> bool:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())

except ImportError:
    # Fallback: use hashlib SHA-256 (not production-safe but keeps app running)
    import hashlib

    def hash_password(plain: str) -> str:  # type: ignore[misc]
        return hashlib.sha256(plain.encode()).hexdigest()

    def verify_password(plain: str, hashed: str) -> bool:  # type: ignore[misc]
        return hashlib.sha256(plain.encode()).hexdigest() == hashed


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
try:
    from jose import JWTError, jwt as _jwt

    def create_access_token(data: dict) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
        return _jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token(token: str) -> dict | None:
        try:
            return _jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            return None

except ImportError:
    # Fallback: simple base64 token (NOT secure – for dev without python-jose)
    import base64
    import json

    def create_access_token(data: dict) -> str:  # type: ignore[misc]
        payload = data.copy()
        payload["exp"] = (datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)).isoformat()
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    def decode_token(token: str) -> dict | None:  # type: ignore[misc]
        try:
            payload = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
            exp = datetime.fromisoformat(payload.get("exp", "2000-01-01"))
            if exp.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                return None
            return payload
        except Exception:
            return None


# ---------------------------------------------------------------------------
# FastAPI dependency: extract current user from Authorization header
# ---------------------------------------------------------------------------
from fastapi import Depends, Header, HTTPException, Query, status


def get_current_user(
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
) -> dict:
    """
    FastAPI dependency. Extracts and validates the JWT from either:
      1) `Authorization: Bearer <token>` header, or
      2) `?token=<token>` query parameter (used for browser PDF downloads).
    Returns the token payload dict on success.
    Raises 401 on missing / invalid / expired token.
    """
    raw_token = None
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization.removeprefix("Bearer ").strip()
    elif token:
        raw_token = token.strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header or token parameter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(raw_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency that additionally enforces role == 'admin'."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user


def require_student(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency that additionally enforces role == 'student'."""
    if current_user.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required.")
    return current_user
