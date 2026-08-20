"""User signup and login against the `users` table.

Belongs in `db/auth.py`.

Passwords are hashed with bcrypt before they ever touch the database or a
log line -- create_user() never persists or logs the raw password, and
verify_user() only ever compares hashes.
"""

import logging
import re
from typing import Any, Dict, Optional

import bcrypt
import psycopg2

from db.database import get_cursor

logger = logging.getLogger(__name__)

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class SignupError(Exception):
    """User-facing signup validation/uniqueness failure. Safe to str() and
    show directly in the UI -- never wraps a raw DB or bcrypt exception.
    """


def _validate_signup(username: str, email: str, password: str) -> None:
    if not USERNAME_PATTERN.match(username or ""):
        raise SignupError("Username must be 3-32 characters: letters, numbers, ., _, -")
    if not EMAIL_PATTERN.match(email or ""):
        raise SignupError("Enter a valid email address.")
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise SignupError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")


def create_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user account.

    Raises:
        SignupError: invalid input, or the username/email is already taken.
            Safe to display to the user.
    """
    _validate_signup(username, email, password)

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, username, email, created_at
                """,
                (username, email, password_hash),
            )
            return dict(cur.fetchone())
    except psycopg2.errors.UniqueViolation:
        raise SignupError("That username or email is already registered.")


def verify_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify credentials against the database.

    Returns:
        The user record (id, username, email -- no password_hash) on
        success, or None on ANY failure (unknown username, wrong
        password). The two cases are deliberately not distinguished so a
        login form can't be used to enumerate valid usernames.
    """
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()

    if row is None:
        # Still run bcrypt against a dummy hash so a nonexistent username
        # doesn't respond measurably faster than a wrong password -- a
        # basic timing-attack mitigation against username enumeration.
        bcrypt.checkpw(b"dummy-password", bcrypt.gensalt())
        return None

    if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return None

    return {"id": row["id"], "username": row["username"], "email": row["email"]}
