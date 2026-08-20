"""Proctoring job records: one row per uploaded video / pipeline run.

Belongs in `db/jobs.py`. This is the single source of truth for job status
that both worker.py (writes) and pages/3_Report.py (reads, via polling)
talk to -- Streamlit itself has no shared in-memory state across a
background thread and the browser's polling reruns.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from db.database import get_cursor

logger = logging.getLogger(__name__)

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_DONE = "DONE"
STATUS_FAILED = "FAILED"

_ERROR_MESSAGE_MAX_LENGTH = 2000


def create_job(user_id: int, video_filename: str, video_path: str) -> str:
    """Insert a new PENDING job row and return its id."""
    job_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO proctoring_jobs (id, user_id, video_filename, video_path, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (job_id, user_id, video_filename, video_path, STATUS_PENDING),
        )
    return job_id


def mark_running(job_id: str) -> None:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE proctoring_jobs SET status = %s WHERE id = %s",
            (STATUS_RUNNING, job_id),
        )


def mark_done(
    job_id: str,
    risk_level: str,
    risk_score: float,
    final_report: str,
    human_review: str,
    langsmith_run_id: Optional[str],
) -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE proctoring_jobs
            SET status = %s, risk_level = %s, risk_score = %s,
                final_report = %s, human_review = %s, langsmith_run_id = %s,
                completed_at = now()
            WHERE id = %s
            """,
            (STATUS_DONE, risk_level, risk_score, final_report, human_review,
             langsmith_run_id, job_id),
        )


def mark_failed(job_id: str, error_message: str) -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE proctoring_jobs
            SET status = %s, error_message = %s, completed_at = now()
            WHERE id = %s
            """,
            (STATUS_FAILED, (error_message or "")[:_ERROR_MESSAGE_MAX_LENGTH], job_id),
        )


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM proctoring_jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()
    return dict(row) if row else None


def get_user_jobs(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Most recent jobs for a user, newest first -- used to populate the
    session picker on the report page.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, video_filename, status, risk_level, risk_score,
                   created_at, completed_at
            FROM proctoring_jobs
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
