"""
backend/api/malpractice.py
-----------------------------
Endpoints for uploading a malpractice image. This just receives and stores
the image + a bare-bones detection event; the heavy lifting (full agent
workflow, scoring, report) happens in backend/api/reports.py so the client
can choose to run analysis + reporting as one step or inspect the image
first.
"""
from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.schemas.malpractice import MalpracticeEventOut
from database.connection import get_db
from database.repository import create_malpractice_event, get_student_by_code

router = APIRouter(prefix="/api/malpractice", tags=["malpractice"])

MALPRACTICE_IMAGE_DIR = os.path.join("data", "malpractice_images")


@router.post("/upload", response_model=MalpracticeEventOut, status_code=201)
def upload_malpractice_image(
    image: UploadFile = File(...),
    student_code: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a malpractice-check image. Saves the file to disk and creates a
    placeholder MalpracticeEvent row (type/confidence get filled in once
    `/api/reports/generate` runs the full agent over it).
    """
    os.makedirs(MALPRACTICE_IMAGE_DIR, exist_ok=True)
    ext = os.path.splitext(image.filename or "")[1] or ".jpg"
    saved_name = f"malpractice_{uuid.uuid4().hex[:10]}{ext}"
    saved_path = os.path.join(MALPRACTICE_IMAGE_DIR, saved_name)

    with open(saved_path, "wb") as f:
        f.write(image.file.read())

    student_id = None
    if student_code:
        student = get_student_by_code(db, student_code)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student '{student_code}' not found.")
        student_id = student.id

    event = create_malpractice_event(
        db,
        student_id=student_id,
        image_path=saved_path,
        malpractice_type="pending_analysis",
        confidence=0.0,
        evidence={},
    )
    return event
