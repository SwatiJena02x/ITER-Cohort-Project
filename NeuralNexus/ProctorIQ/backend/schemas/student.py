"""
backend/schemas/student.py
---------------------------
Pydantic validation models for student registration and retrieval.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentCreate(BaseModel):
    """Payload for registering a new student profile."""
    student_code: str = Field(..., min_length=1, max_length=50, examples=["STU2026001"])
    full_name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    course: str | None = Field(default=None, max_length=150)
    # profile_image is uploaded separately as multipart/form-data (see api/students.py)


class StudentOut(BaseModel):
    """What we return to clients after creating/fetching a student."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_code: str
    full_name: str
    email: EmailStr
    course: str | None
    profile_image_path: str
    created_at: datetime


class StudentList(BaseModel):
    students: list[StudentOut]
    total: int
