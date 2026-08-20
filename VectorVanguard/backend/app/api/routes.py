from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db, engine
from app.core.config import settings
from app.models.exam_session import ExamSession
from app.models.student import Student
from app.services.agent import run_agent
from app.services.ingestion import ingest_evidence


router = APIRouter()


UPLOAD_DIRECTORY = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "raw"
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


class InvestigationRequest(BaseModel):
    query: str


class InvestigationResponse(BaseModel):
    answer: str


@router.get("/health")
def health_check():
    """
    Basic application health check.

    Verifies that the API process is running and
    that PostgreSQL is reachable.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        database_status = "ok"

    except Exception:
        database_status = "error"

    overall_status = (
        "ok"
        if database_status == "ok"
        else "degraded"
    )

    return {
        "status": overall_status,
        "application": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database": database_status,
    }


@router.get("/students")
def get_students(
    db: Session = Depends(get_db),
):
    students = (
        db.query(Student)
        .order_by(Student.id)
        .all()
    )

    return [
        {
            "id": student.id,
            "student_id": student.student_id,
            "name": student.name,
        }
        for student in students
    ]


@router.get("/sessions")
def get_sessions(
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ExamSession)
        .order_by(ExamSession.id)
        .all()
    )

    return [
        {
            "id": session.id,
            "student_id": session.student_id,
            "exam_name": session.exam_name,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
        }
        for session in sessions
    ]


@router.post(
    "/investigate",
    response_model=InvestigationResponse,
)
def investigate(
    request: InvestigationRequest,
):
    answer = run_agent(
        request.query
    )

    return {
        "answer": answer
    }


@router.post("/upload-evidence")
async def upload_evidence(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type.",
        )

    file_data = await file.read()

    if not file_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB limit.",
        )

    evidence_id = f"EVD-{uuid4().hex[:12]}"

    filename = f"{evidence_id}{extension}"

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path = (
        UPLOAD_DIRECTORY / filename
    )

    image_path.write_bytes(file_data)

    image = cv2.imread(str(image_path))

    if image is None:
        image_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid readable image.",
        )

    try:
        evidence = ingest_evidence(
            db=db,
            session_id=session_id,
            image_path=str(image_path),
            evidence_id=evidence_id,
        )

    except Exception as exc:
        db.rollback()
        image_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Evidence processing failed: {exc}",
        )

    return {
        "message": "Evidence uploaded and processed successfully.",
        "evidence_id": evidence.evidence_id,
        "session_id": evidence.session_id,
        "image_path": evidence.image_path,
        "ocr_text": evidence.ocr_text,
    }